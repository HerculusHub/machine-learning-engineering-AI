"""
Integration tests for the complete Impact Layer pipeline.

Architecture v2.3 (Frozen MVP)

This test uses the real Impact Layer components:

    InformationResult
        ↓
    FeatureBuilder
        ↓
    ChurnEngine
        ↓
    SensitivityEngine
        ↓
    CausalEngine
        ↓
    FinancialEngine
        ↓
    ImpactService
        ↓
    ImpactResult

Only the persisted churn model is replaced with a fake
binary-classification model.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from mobile_ai_system.application.models.information_result import (
    InformationResult,
)
from mobile_ai_system.impact.engines.causal_engine import (
    CausalEngine,
)
from mobile_ai_system.impact.engines.churn_engine import (
    ChurnEngine,
)
from mobile_ai_system.impact.engines.financial_engine import (
    FinancialEngine,
)
from mobile_ai_system.impact.engines.sensitivity_engine import (
    SensitivityEngine,
)
from mobile_ai_system.impact.models.impact_result import (
    ImpactResult,
)
from mobile_ai_system.impact.services.impact_service import (
    ImpactService,
)


class FakeChurnModel:
    """
    Deterministic binary churn model used by the
    Impact Layer integration test.
    """

    def __init__(
        self,
        churn_probability: float = 0.20,
    ) -> None:
        self.churn_probability = churn_probability

    def predict_proba(
        self,
        X,
    ):
        """
        Return sklearn-style binary probabilities.
        """

        return [
            [
                1.0 - self.churn_probability,
                self.churn_probability,
            ]
        ]


def build_information_result() -> InformationResult:
    """
    Build realistic Information Layer input.

    FeatureBuilder currently extracts event_count, so
    multiple records verify that the information really
    flows through FeatureBuilder into ChurnEngine.
    """

    return InformationResult(
        records=[
            {
                "event_id": "EVENT-001",
                "operator_name": "AT&T",
                "event_category": "pricing",
                "key_points": [
                    "Competitor reduced wireless prices."
                ],
            },
            {
                "event_id": "EVENT-002",
                "operator_name": "T-Mobile",
                "event_category": "promotion",
                "key_points": [
                    "Competitor introduced a retention promotion."
                ],
            },
            {
                "event_id": "EVENT-003",
                "operator_name": "Verizon",
                "event_category": "network",
                "key_points": [
                    "Regional service disruption reported."
                ],
            },
        ],
        metadata={
            "fixture": "impact_pipeline",
        },
    )


def build_service() -> ImpactService:
    """
    Build the real ImpactService and real analytical
    engines used by the integration test.
    """

    churn_engine = ChurnEngine(
        model_path="fake_churn_model.joblib",
    )

    sensitivity_engine = SensitivityEngine()

    causal_engine = CausalEngine()

    financial_engine = FinancialEngine(
        customer_base=1_000_000,
        monthly_arpu=60.0,
        gross_margin=0.35,
    )

    return ImpactService(
        churn_engine=churn_engine,
        sensitivity_engine=sensitivity_engine,
        causal_engine=causal_engine,
        financial_engine=financial_engine,
    )


def test_complete_impact_pipeline():
    """
    Execute the complete real Impact Layer pipeline.
    """

    information = build_information_result()

    fake_model = FakeChurnModel(
        churn_probability=0.20,
    )

    with patch(
        "mobile_ai_system.impact.engines.churn_engine.Path.exists",
        return_value=True,
    ), patch(
        "mobile_ai_system.impact.engines.churn_engine.joblib.load",
        return_value=fake_model,
    ):
        service = build_service()

        result = service.evaluate(
            information,
        )

    assert isinstance(
        result,
        ImpactResult,
    )

    # ---------------------------------------------------------
    # Churn
    # ---------------------------------------------------------

    assert result.churn.predicted_churn_rate == pytest.approx(
        0.20
    )

    assert result.churn.feature_vector.features[
        "event_count"
    ] == pytest.approx(
        3.0
    )

    assert result.churn.metadata[
        "model"
    ] == "fake_churn_model"

    assert result.churn.metadata[
        "feature_count"
    ] == 1

    assert result.churn.metadata[
        "predicted_churn"
    ] is False

    # ---------------------------------------------------------
    # Sensitivity
    # ---------------------------------------------------------

    assert result.sensitivity.total_features == 1

    assert result.sensitivity.features[
        0
    ].feature_name == "event_count"

    assert result.sensitivity.features[
        0
    ].importance_score == pytest.approx(
        0.0
    )

    assert result.sensitivity.metadata[
        "information_record_count"
    ] == 3

    # ---------------------------------------------------------
    # Causal
    # ---------------------------------------------------------

    assert result.causal.cause_count == 1

    assert result.causal.causes[
        0
    ].factor == "event_count"

    assert result.causal.causes[
        0
    ].supporting_events == [
        "EVENT-001",
        "EVENT-002",
        "EVENT-003",
    ]

    assert result.causal.metadata[
        "information_record_count"
    ] == 3

    # ---------------------------------------------------------
    # Financial
    # ---------------------------------------------------------

    assert result.financial.predicted_churn_rate == pytest.approx(
        0.20
    )

    assert result.financial.lost_customers == pytest.approx(
        200_000.0
    )

    assert result.financial.monthly_revenue_loss == pytest.approx(
        12_000_000.0
    )

    assert result.financial.annual_revenue_loss == pytest.approx(
        144_000_000.0
    )

    assert result.financial.monthly_profit_loss == pytest.approx(
        4_200_000.0
    )

    assert result.financial.annual_profit_loss == pytest.approx(
        50_400_000.0
    )

    # ---------------------------------------------------------
    # Service metadata
    # ---------------------------------------------------------

    assert result.metadata[
        "service"
    ] == "ImpactService"

    assert result.metadata[
        "information_record_count"
    ] == 3


def test_pipeline_with_zero_churn():
    """
    Zero churn should propagate safely through every
    downstream Impact component.
    """

    information = build_information_result()

    fake_model = FakeChurnModel(
        churn_probability=0.0,
    )

    with patch(
        "mobile_ai_system.impact.engines.churn_engine.Path.exists",
        return_value=True,
    ), patch(
        "mobile_ai_system.impact.engines.churn_engine.joblib.load",
        return_value=fake_model,
    ):
        service = build_service()

        result = service.evaluate(
            information,
        )

    assert result.churn.predicted_churn_rate == pytest.approx(
        0.0
    )

    assert result.financial.lost_customers == pytest.approx(
        0.0
    )

    assert result.financial.monthly_revenue_loss == pytest.approx(
        0.0
    )

    assert result.financial.annual_revenue_loss == pytest.approx(
        0.0
    )

    assert result.financial.monthly_profit_loss == pytest.approx(
        0.0
    )

    assert result.financial.annual_profit_loss == pytest.approx(
        0.0
    )


def test_pipeline_with_high_churn():
    """
    High churn probability should propagate into a positive
    classification and corresponding financial impact.
    """

    information = build_information_result()

    fake_model = FakeChurnModel(
        churn_probability=0.80,
    )

    with patch(
        "mobile_ai_system.impact.engines.churn_engine.Path.exists",
        return_value=True,
    ), patch(
        "mobile_ai_system.impact.engines.churn_engine.joblib.load",
        return_value=fake_model,
    ):
        service = build_service()

        result = service.evaluate(
            information,
        )

    assert result.churn.predicted_churn_rate == pytest.approx(
        0.80
    )

    assert result.churn.predicted_churn is True

    assert result.financial.lost_customers == pytest.approx(
        800_000.0
    )

    assert result.financial.annual_revenue_loss == pytest.approx(
        576_000_000.0
    )