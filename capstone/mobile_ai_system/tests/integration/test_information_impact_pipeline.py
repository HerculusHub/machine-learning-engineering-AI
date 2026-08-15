"""
Integration test for the Information -> Impact pipeline.

Architecture v2.3 (Frozen MVP)

This test verifies stage-to-stage handoff through
PipelineContext using ApplicationRunner.

The Information stage is allowed to populate
information_result, and the Impact stage then consumes it.

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
    Deterministic churn model for integration testing.

    The fake mirrors the minimum persisted-model contract
    required by ChurnPredictionService.
    """

    def __init__(
        self,
        probability: float = 0.30,
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
# Information fixture
# =============================================================


def build_information_result(
) -> InformationResult:
    """
    InformationResult that simulates the output of the
    real Information Layer.
    """

    return InformationResult(
        records=[
            {
                "event_id": "EVENT-001",
                "operator_name": "AT&T",
                "event_category": "pricing",
                "key_points": [
                    "Competitor reduced prices."
                ],
            },
            {
                "event_id": "EVENT-002",
                "operator_name": "T-Mobile",
                "event_category": "promotion",
                "key_points": [
                    (
                        "Competitor launched a "
                        "retention offer."
                    )
                ],
            },
            {
                "event_id": "EVENT-003",
                "operator_name": "Verizon",
                "event_category": "network",
                "key_points": [
                    "Service disruption reported."
                ],
            },
        ],

        metadata={
            "fixture": "information-impact",
        },
    )


# =============================================================
# Information -> Impact integration
# =============================================================


def test_information_to_impact_pipeline():
    """
    ApplicationRunner should execute information first,
    then pass its result to ImpactAgent through
    PipelineContext.
    """

    fake_information = (
        build_information_result()
    )

    fake_model = FakeChurnModel(
        probability=0.30,
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

        context = PipelineContext()

        plan = ExecutionPlan(
            steps=[
                "information",
                "impact",
            ]
        )

        # -----------------------------------------------------
        # For this integration boundary, isolate external
        # Information Layer retrieval while still allowing
        # ApplicationRunner to dispatch the real
        # InformationAgent handler.
        # -----------------------------------------------------

        with patch.object(
            information_agent,
            "execute",
            side_effect=lambda ctx: (
                _populate_information(
                    ctx,
                    fake_information,
                )
            ),
        ):

            # -------------------------------------------------
            # Re-register the patched bound handler because
            # ApplicationRunner already captured the original
            # bound method during Bootstrap.
            # -------------------------------------------------

            runner.register(
                "information",
                information_agent.execute,
            )

            result = runner.run(
                plan,
                context,
            )

    assert result is context

    # =========================================================
    # Information stage
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
    # Impact stage
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
            0.30
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
        .sensitivity
        .total_features
        ==
        1
    )

    assert (
        result
        .impact_result
        .causal
        .cause_count
        ==
        1
    )

    assert (
        result
        .impact_result
        .causal
        .causes[
            0
        ]
        .supporting_events
        ==
        [
            "EVENT-001",
            "EVENT-002",
            "EVENT-003",
        ]
    )

    assert (
        result
        .impact_result
        .financial
        .lost_customers
        ==
        pytest.approx(
            300_000.0
        )
    )

    assert (
        result
        .impact_result
        .metadata[
            "information_record_count"
        ]
        ==
        3
    )


# =============================================================
# Execution ordering
# =============================================================


def test_information_stage_runs_before_impact():
    """
    Impact must observe information_result produced by the
    preceding information stage.
    """

    fake_information = (
        build_information_result()
    )

    fake_model = FakeChurnModel(
        probability=0.10,
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
        return_value=fake_model,
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

        impact_agent = (
            container.resolve(
                "impact_agent"
            )
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

        original_impact_execute = (
            impact_agent.execute
        )

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

        runner.register(
            "information",
            information_handler,
        )

        runner.register(
            "impact",
            impact_handler,
        )

        result = runner.run(
            ExecutionPlan(
                steps=[
                    "information",
                    "impact",
                ]
            ),
            PipelineContext(),
        )

    assert execution_order == [
        "information",
        "impact",
    ]

    assert (
        result.information_result
        is
        fake_information
    )

    assert (
        result.impact_result
        is not None
    )


# =============================================================
# Helper
# =============================================================


def _populate_information(
    context: PipelineContext,
    information: InformationResult,
) -> PipelineContext:
    """
    Test helper that simulates InformationAgent output.
    """

    context.information_result = (
        information
    )

    return context