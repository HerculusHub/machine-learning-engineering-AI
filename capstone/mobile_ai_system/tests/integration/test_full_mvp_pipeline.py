"""
Integration test for the complete MVP pipeline.

Architecture v2.3 (Frozen MVP)

Pipeline
--------
information
    ↓
impact
    ↓
report
    ↓
evaluation

The test uses real application components and
PipelineContext handoff.

Only external boundaries are replaced with fakes:

- persisted churn model
- report-generation LLM
- evaluation LLM

Step 11E compatibility
----------------------
FakeChurnModel implements the current runtime persisted-model
contract required by ChurnPredictionService:

    predict_proba()
    feature_columns
"""

from __future__ import annotations

import json
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

    Runtime contract
    ----------------
    feature_columns
        Declares the feature schema expected by the model.

    predict_proba()
        Returns binary class probabilities.

    Notes
    -----
    The current frozen-MVP FeatureBuilder produces
    ``event_count`` for this integration path, so that is the
    only feature required by this deterministic fake.
    """

    def __init__(
        self,
        probability: float = 0.25,
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
        Return deterministic probabilities for every row.
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
# Fake report LLM
# =============================================================


class FakeReportLLM:
    """
    Deterministic LLM used by ReportAgent.
    """

    def __init__(
        self,
        response: str = (
            "Generated executive telecom report."
        ),
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
# Fake evaluation LLM
# =============================================================


class FakeEvaluationLLM:
    """
    Deterministic LLM used by EvaluationAgent.
    """

    def __init__(
        self,
        score: float = 0.90,
    ) -> None:

        self.score = score

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

        return json.dumps(
            {
                "score": self.score,

                "strengths": [
                    "Clear structure",
                    "Strong impact analysis",
                ],

                "weaknesses": [
                    "Limited scenario analysis",
                ],

                "suggestions": [
                    "Add scenario analysis",
                ],
            }
        )


# =============================================================
# Information fixture
# =============================================================


def build_information_result(
) -> InformationResult:
    """
    Build deterministic Information Layer output.
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
                        "Competitor introduced "
                        "a retention offer."
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
            "fixture": "full-mvp-pipeline",
        },
    )


# =============================================================
# Complete MVP pipeline
# =============================================================


def test_complete_mvp_pipeline():
    """
    Execute the complete application pipeline:

        information
            ↓
        impact
            ↓
        report
            ↓
        evaluation

    A passing evaluation should also publish the draft
    report as PipelineContext.final_response.
    """

    fake_information = (
        build_information_result()
    )

    fake_churn_model = (
        FakeChurnModel(
            probability=0.25,
        )
    )

    report_llm = FakeReportLLM(
        response=(
            "Generated executive telecom report "
            "with competitive impact analysis."
        ),
    )

    evaluation_llm = (
        FakeEvaluationLLM(
            score=0.90,
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
        return_value=fake_churn_model,
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

        report_agent = (
            container.resolve(
                "report_agent"
            )
        )

        evaluation_agent = (
            container.resolve(
                "evaluation_agent"
            )
        )

        report_agent.tools = {
            "llm": report_llm,
        }

        evaluation_agent.tools = {
            "llm": evaluation_llm,
        }

        # -----------------------------------------------------
        # Replace only external Information retrieval.
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
                    "Assess competitor impact on "
                    "customer churn and financial "
                    "performance."
                ),
            },
        )

        plan = ExecutionPlan(
            steps=[
                "information",
                "impact",
                "report",
                "evaluation",
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
            0.25
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
            250_000.0
        )
    )

    assert (
        result
        .impact_result
        .financial
        .monthly_revenue_loss
        ==
        pytest.approx(
            15_000_000.0
        )
    )

    assert (
        result
        .impact_result
        .financial
        .annual_revenue_loss
        ==
        pytest.approx(
            180_000_000.0
        )
    )

    # =========================================================
    # Report
    # =========================================================

    expected_report = (
        "Generated executive telecom report "
        "with competitive impact analysis."
    )

    assert (
        result.report_result
        ==
        expected_report
    )

    assert (
        len(
            report_llm.calls
        )
        ==
        1
    )

    report_prompt = (
        report_llm.calls[
            0
        ][
            "prompt"
        ]
    )

    assert (
        (
            "Assess competitor impact on "
            "customer churn"
        )
        in
        report_prompt
    )

    assert (
        "EVENT-001"
        in
        report_prompt
    )

    assert (
        "EVENT-002"
        in
        report_prompt
    )

    assert (
        "EVENT-003"
        in
        report_prompt
    )

    # =========================================================
    # Evaluation
    # =========================================================

    assert (
        result.evaluation_result
        is not None
    )

    assert (
        result.evaluation_result[
            "score"
        ]
        ==
        pytest.approx(
            0.90
        )
    )

    assert (
        result.evaluation_result[
            "strengths"
        ]
        ==
        [
            "Clear structure",
            "Strong impact analysis",
        ]
    )

    assert (
        result.evaluation_result[
            "weaknesses"
        ]
        ==
        [
            "Limited scenario analysis",
        ]
    )

    assert (
        result.evaluation_result[
            "suggestions"
        ]
        ==
        [
            "Add scenario analysis",
        ]
    )

    assert (
        result.metadata[
            "evaluation_score"
        ]
        ==
        pytest.approx(
            0.90
        )
    )

    assert (
        result.metadata[
            "requires_report_refinement"
        ]
        is False
    )

    # =========================================================
    # Final response
    # =========================================================

    assert (
        result.final_response
        ==
        expected_report
    )

    assert (
        result.metadata[
            "report_refinement_performed"
        ]
        is False
    )

    assert (
        result.metadata[
            "report_refinement_count"
        ]
        ==
        0
    )

    # =========================================================
    # Reflection
    # =========================================================

    reflections = (
        result.metadata[
            "reflections"
        ]
    )

    assert (
        len(
            reflections
        )
        ==
        1
    )

    reflection = (
        reflections[
            0
        ]
    )

    assert (
        reflection[
            "score"
        ]
        ==
        pytest.approx(
            0.90
        )
    )

    assert (
        reflection[
            "lesson"
        ]
        ==
        "Add scenario analysis"
    )

    # =========================================================
    # External-call counts
    # =========================================================

    assert (
        len(
            evaluation_llm.calls
        )
        ==
        1
    )


# =============================================================
# Pipeline execution order
# =============================================================


def test_complete_pipeline_execution_order():
    """
    Verify stage execution order.

    Information must execute before Impact,
    Impact before Report, and Report before Evaluation.
    """

    fake_information = (
        build_information_result()
    )

    fake_churn_model = (
        FakeChurnModel(
            probability=0.10,
        )
    )

    report_llm = FakeReportLLM(
        response="Pipeline order report.",
    )

    evaluation_llm = (
        FakeEvaluationLLM(
            score=0.80,
        )
    )

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
        return_value=fake_churn_model,
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

        evaluation_agent = (
            container.resolve(
                "evaluation_agent"
            )
        )

        report_agent.tools = {
            "llm": report_llm,
        }

        evaluation_agent.tools = {
            "llm": evaluation_llm,
        }

        original_impact_execute = (
            impact_agent.execute
        )

        original_report_execute = (
            report_agent.execute
        )

        original_evaluation_execute = (
            evaluation_agent.execute
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
                is not None
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

        def evaluation_handler(
            context: PipelineContext,
        ) -> PipelineContext:

            execution_order.append(
                "evaluation"
            )

            assert (
                context.report_result
                is not None
            )

            return (
                original_evaluation_execute(
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

        runner.register(
            "evaluation",
            evaluation_handler,
        )

        result = runner.run(
            ExecutionPlan(
                steps=[
                    "information",
                    "impact",
                    "report",
                    "evaluation",
                ]
            ),
            PipelineContext(
                metadata={
                    "user_request": (
                        "Validate complete "
                        "MVP pipeline."
                    ),
                },
            ),
        )

    assert execution_order == [
        "information",
        "impact",
        "report",
        "evaluation",
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

    assert (
        result.evaluation_result
        is not None
    )


# =============================================================
# Missing-report evaluation behavior
# =============================================================


def test_evaluation_stage_without_report_returns_zero_score():
    """
    Current Frozen MVP EvaluationAgent handles a missing
    report gracefully instead of raising an exception.
    """

    container = Bootstrap().build()

    runner = container.resolve(
        "runner"
    )

    context = PipelineContext()

    plan = ExecutionPlan(
        steps=[
            "evaluation",
        ]
    )

    result = runner.run(
        plan,
        context,
    )

    assert (
        result.evaluation_result[
            "score"
        ]
        ==
        pytest.approx(
            0.0
        )
    )

    assert (
        result.metadata[
            "evaluation_score"
        ]
        ==
        pytest.approx(
            0.0
        )
    )

    assert (
        result.metadata[
            "requires_report_refinement"
        ]
        is True
    )

    assert (
        result.final_response
        is None
    )