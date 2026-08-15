"""
Integration test for ApplicationRunner -> ImpactAgent -> ImpactService.

Architecture v2.3 (Frozen MVP)

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
    Deterministic churn model used for integration testing.

    The fake mirrors the minimum persisted-model contract
    required by ChurnPredictionService.
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
    Build InformationResult already produced by the
    Information stage.
    """

    return InformationResult(
        records=[
            {
                "event_id": "EVENT-001",
                "operator_name": "AT&T",
                "event_category": "pricing",
            },
            {
                "event_id": "EVENT-002",
                "operator_name": "T-Mobile",
                "event_category": "promotion",
            },
        ],

        metadata={
            "fixture": "runner-impact",
        },
    )


# =============================================================
# Runner -> Impact integration
# =============================================================


def test_runner_executes_impact_stage():
    """
    ApplicationRunner should dispatch the impact stage
    through ImpactAgent and populate impact_result.
    """

    fake_model = FakeChurnModel(
        probability=0.25,
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

        information = (
            build_information_result()
        )

        context = PipelineContext(
            information_result=(
                information
            ),
        )

        plan = ExecutionPlan(
            steps=[
                "impact",
            ]
        )

        result = runner.run(
            plan,
            context,
        )

    assert result is context

    assert isinstance(
        result.impact_result,
        ImpactResult,
    )

    assert (
        result.information_result
        is
        information
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
            2.0
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
        ]
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


# =============================================================
# Missing InformationResult
# =============================================================


def test_runner_impact_stage_requires_information():
    """
    ImpactAgent should fail when the Information stage
    has not populated PipelineContext.
    """

    container = Bootstrap().build()

    runner = container.resolve(
        "runner"
    )

    context = PipelineContext()

    plan = ExecutionPlan(
        steps=[
            "impact",
        ]
    )

    with pytest.raises(
        RuntimeError,
        match="no InformationResult",
    ):

        runner.run(
            plan,
            context,
        )


# =============================================================
# Disabled stage
# =============================================================


def test_runner_skips_disabled_impact_stage():
    """
    Disabled impact stage should not execute.
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
            "impact",
        ]
    )

    plan.disable(
        "impact"
    )

    result = runner.run(
        plan,
        context,
    )

    assert result is context

    assert (
        result.impact_result
        is None
    )