"""
Integration test for the Information -> Impact -> Report pipeline.

Architecture v2.3 (Frozen MVP)

This test verifies application-stage handoff through
PipelineContext and ApplicationRunner.

External boundaries are replaced with deterministic fakes:

- churn model
- LLM generation

Step 11E compatibility
----------------------
FakeChurnModel implements the current runtime persisted-model
contract required by ChurnPredictionService:

    predict_proba()
    feature_columns
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from mobile_ai_system.application.bootstrap import (
    Bootstrap,
)
from mobile_ai_system.application.models.execution_plan import (
    ExecutionPlan,
)
from mobile_ai_system.application.models.information_result import (
    InformationResult,
)
from mobile_ai_system.application.models.pipeline_context import (
    PipelineContext,
)
from mobile_ai_system.impact.models.impact_result import (
    ImpactResult,
)


# =============================================================
# Fake persisted churn model
# =============================================================


class FakeChurnModel:
    """
    Deterministic binary churn model.

    The fake mirrors the minimum persisted-model contract
    required by ChurnPredictionService.
    """

    def __init__(
        self,
        probability: float = 0.20,
    ) -> None:

        self.probability = probability

        self.feature_columns = [
            "event_count",
        ]

    def predict_proba(
        self,
        X,
    ):
        """
        Return deterministic binary probabilities for
        every input row.
        """

        return [
            [
                1.0 - self.probability,
                self.probability,
            ]
            for _ in range(
                len(X)
            )
        ]


# =============================================================
# Fake report-generation LLM
# =============================================================


class FakeLLMTool:
    """
    Deterministic report-generation tool.
    """

    def __init__(
        self,
        response: str = "Executive impact report.",
    ) -> None:

        self.response = response

        self.calls: list[
            dict
        ] = []

    def generate(
        self,
        provider: str,
        model: str,
        prompt: str,
    ) -> str:

        self.calls.append(
            {
                "provider": provider,
                "model": model,
                "prompt": prompt,
            }
        )

        return self.response


# =============================================================
# Information fixture
# =============================================================


def build_information_result(
) -> InformationResult:
    """
    Simulated Information Layer result.
    """

    return InformationResult(
        records=[
            {
                "event_id": "EVENT-001",
                "operator_name": "AT&T",
                "event_category": "pricing",
                "key_points": [
                    (
                        "Competitor reduced "
                        "wireless prices."
                    )
                ],
            },
            {
                "event_id": "EVENT-002",
                "operator_name": "Verizon",
                "event_category": "promotion",
                "key_points": [
                    (
                        "Competitor launched a "
                        "retention promotion."
                    )
                ],
            },
            {
                "event_id": "EVENT-003",
                "operator_name": "T-Mobile",
                "event_category": "network",
                "key_points": [
                    (
                        "Regional network issue "
                        "reported."
                    )
                ],
            },
        ],

        metadata={
            "fixture": "information-impact-report",
        },
    )


# =============================================================
# Information -> Impact -> Report integration
# =============================================================


def test_information_impact_report_pipeline():
    """
    Execute information -> impact -> report through
    the real ApplicationRunner.
    """

    fake_information = (
        build_information_result()
    )

    fake_model = FakeChurnModel(
        probability=0.20,
    )

    fake_llm = FakeLLMTool(
        response=(
            "Generated telecom executive report."
        )
    )

    with patch(
        (
            "mobile_ai_system.impact.engines."
            "churn_engine.Path.exists"
        ),
        return_value=True,
    ), patch(
        (
            "mobile_ai_system.impact.engines."
            "churn_engine.joblib.load"
        ),
        return_value=fake_model,
    ), patch(
        (
            "mobile_ai_system.agents."
            "report_agent.load_agent_prompts"
        ),
        return_value=(
            "REQUEST={user_request}\n"
            "EVENTS={retrieved_events}\n"
            "IMPACT={impact_result}"
        ),
    ):

        container = Bootstrap().build()

        runner = container.resolve(
            "runner"
        )

        information_agent = (
            container.resolve(
                "information_agent"
            )
        )

        report_agent = (
            container.resolve(
                "report_agent"
            )
        )

        report_agent.tools = {
            "llm": fake_llm,
        }

        # -----------------------------------------------------
        # Replace external Information retrieval only.
        # -----------------------------------------------------

        def information_handler(
            context: PipelineContext,
        ) -> PipelineContext:

            context.information_result = (
                fake_information
            )

            return context

        runner.register(
            "information",
            information_handler,
        )

        context = PipelineContext(
            metadata={
                "user_request": (
                    "Assess competitor impact "
                    "on churn."
                ),
            }
        )

        plan = ExecutionPlan(
            steps=[
                "information",
                "impact",
                "report",
            ]
        )

        result = runner.run(
            plan,
            context,
        )

    assert result is context

    # =========================================================
    # Information
    # =========================================================

    assert (
        result.information_result
        is
        fake_information
    )

    assert (
        result.information_result
        .total_records
        ==
        3
    )

    # =========================================================
    # Impact
    # =========================================================

    assert isinstance(
        result.impact_result,
        ImpactResult,
    )

    assert (
        result
        .impact_result
        .churn
        .predicted_churn_rate
        ==
        pytest.approx(
            0.20
        )
    )

    assert (
        result
        .impact_result
        .churn
        .feature_vector
        .features[
            "event_count"
        ]
        ==
        pytest.approx(
            3.0
        )
    )

    assert (
        result
        .impact_result
        .financial
        .lost_customers
        ==
        pytest.approx(
            200_000.0
        )
    )

    # =========================================================
    # Report
    # =========================================================

    assert (
        result.report_result
        ==
        "Generated telecom executive report."
    )

    assert (
        len(
            fake_llm.calls
        )
        ==
        1
    )

    prompt = (
        fake_llm.calls[
            0
        ][
            "prompt"
        ]
    )

    assert (
        "Assess competitor impact on churn."
        in
        prompt
    )

    assert (
        "EVENT-001"
        in
        prompt
    )

    assert (
        "EVENT-002"
        in
        prompt
    )

    assert (
        "EVENT-003"
        in
        prompt
    )

    assert (
        "predicted_churn_rate"
        in
        prompt
    )


# =============================================================
# Pipeline execution order
# =============================================================


def test_pipeline_execution_order():
    """
    Verify that report executes only after impact and
    impact executes only after information.
    """

    fake_information = (
        build_information_result()
    )

    fake_model = FakeChurnModel(
        probability=0.15,
    )

    fake_llm = FakeLLMTool()

    execution_order: list[
        str
    ] = []

    with patch(
        (
            "mobile_ai_system.impact.engines."
            "churn_engine.Path.exists"
        ),
        return_value=True,
    ), patch(
        (
            "mobile_ai_system.impact.engines."
            "churn_engine.joblib.load"
        ),
        return_value=fake_model,
    ), patch(
        (
            "mobile_ai_system.agents."
            "report_agent.load_agent_prompts"
        ),
        return_value=(
            "{user_request}\n"
            "{retrieved_events}\n"
            "{impact_result}"
        ),
    ):

        container = Bootstrap().build()

        runner = container.resolve(
            "runner"
        )

        impact_agent = (
            container.resolve(
                "impact_agent"
            )
        )

        report_agent = (
            container.resolve(
                "report_agent"
            )
        )

        report_agent.tools = {
            "llm": fake_llm,
        }

        original_impact_execute = (
            impact_agent.execute
        )

        original_report_execute = (
            report_agent.execute
        )

        def information_handler(
            context: PipelineContext,
        ) -> PipelineContext:

            execution_order.append(
                "information"
            )

            context.information_result = (
                fake_information
            )

            return context

        def impact_handler(
            context: PipelineContext,
        ) -> PipelineContext:

            execution_order.append(
                "impact"
            )

            assert (
                context.information_result
                is
                fake_information
            )

            return (
                original_impact_execute(
                    context
                )
            )

        def report_handler(
            context: PipelineContext,
        ) -> PipelineContext:

            execution_order.append(
                "report"
            )

            assert (
                context.impact_result
                is not None
            )

            return (
                original_report_execute(
                    context
                )
            )

        runner.register(
            "information",
            information_handler,
        )

        runner.register(
            "impact",
            impact_handler,
        )

        runner.register(
            "report",
            report_handler,
        )

        result = runner.run(
            ExecutionPlan(
                steps=[
                    "information",
                    "impact",
                    "report",
                ]
            ),
            PipelineContext(
                metadata={
                    "user_request": (
                        "Pipeline test"
                    ),
                }
            ),
        )

    assert execution_order == [
        "information",
        "impact",
        "report",
    ]

    assert (
        result.information_result
        is not None
    )

    assert (
        result.impact_result
        is not None
    )

    assert (
        result.report_result
        is not None
    )


# =============================================================
# Report precondition
# =============================================================


def test_report_stage_requires_impact():
    """
    Report stage should fail when ImpactResult is missing.
    """

    container = Bootstrap().build()

    runner = container.resolve(
        "runner"
    )

    context = PipelineContext(
        information_result=(
            build_information_result()
        ),
    )

    plan = ExecutionPlan(
        steps=[
            "report",
        ]
    )

    with pytest.raises(
        RuntimeError,
        match="no ImpactResult",
    ):

        runner.run(
            plan,
            context,
        )