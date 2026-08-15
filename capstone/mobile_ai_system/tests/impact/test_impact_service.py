"""
Unit tests for ImpactService.

Architecture v2.3 (Frozen MVP)
"""

from unittest.mock import MagicMock

from mobile_ai_system.application.models.information_result import (
    InformationResult,
)
from mobile_ai_system.impact.models.causal_result import (
    CausalResult,
)
from mobile_ai_system.impact.models.churn_result import (
    ChurnResult,
)
from mobile_ai_system.impact.models.feature_vector import (
    FeatureVector,
)
from mobile_ai_system.impact.models.financial_result import (
    FinancialResult,
)
from mobile_ai_system.impact.models.sensitivity_result import (
    SensitivityResult,
)
from mobile_ai_system.impact.services.impact_service import (
    ImpactService,
)


def build_information_result() -> InformationResult:
    return InformationResult(
        records=[
            {
                "event_id": "EVENT-1",
                "operator_name": "Verizon",
            }
        ],
        metadata={
            "fixture": True,
        },
    )


def build_churn_result() -> ChurnResult:
    return ChurnResult(
        predicted_churn_rate=0.10,
        confidence=0.90,
        feature_vector=FeatureVector(
            features={
                "event_count": 1.0,
            }
        ),
        metadata={
            "model": "test_model",
        },
    )


def build_sensitivity_result() -> SensitivityResult:
    return SensitivityResult(
        features=[],
        model_name="test_model",
        metadata={
            "fixture": True,
        },
    )


def build_causal_result() -> CausalResult:
    return CausalResult(
        confidence=0.80,
        metadata={
            "fixture": True,
        },
    )


def build_financial_result() -> FinancialResult:
    return FinancialResult(
        predicted_churn_rate=0.10,
        lost_customers=100_000,
        monthly_revenue_loss=6_000_000.0,
        annual_revenue_loss=72_000_000.0,
        monthly_profit_loss=2_100_000.0,
        annual_profit_loss=25_200_000.0,
        market_share_loss=0.10,
        customer_base=1_000_000,
        arpu=60.0,
        gross_margin=0.35,
        confidence=0.80,
        metadata={
            "fixture": True,
        },
    )


def make_service():
    churn_engine = MagicMock()
    sensitivity_engine = MagicMock()
    causal_engine = MagicMock()
    financial_engine = MagicMock()

    service = ImpactService(
        churn_engine=churn_engine,
        sensitivity_engine=sensitivity_engine,
        causal_engine=causal_engine,
        financial_engine=financial_engine,
    )

    return (
        service,
        churn_engine,
        sensitivity_engine,
        causal_engine,
        financial_engine,
    )


def test_predict_churn():
    (
        service,
        churn_engine,
        _,
        _,
        _,
    ) = make_service()

    information = build_information_result()
    churn = build_churn_result()

    churn_engine.predict.return_value = churn

    result = service.predict_churn(
        information,
    )

    assert result is churn

    churn_engine.predict.assert_called_once_with(
        information,
    )


def test_analyze_sensitivity():
    (
        service,
        _,
        sensitivity_engine,
        _,
        _,
    ) = make_service()

    information = build_information_result()
    churn = build_churn_result()
    sensitivity = build_sensitivity_result()

    sensitivity_engine.analyze.return_value = sensitivity

    result = service.analyze_sensitivity(
        information,
        churn,
    )

    assert result is sensitivity

    sensitivity_engine.analyze.assert_called_once_with(
        information,
        churn,
    )


def test_infer_causality():
    (
        service,
        _,
        _,
        causal_engine,
        _,
    ) = make_service()

    information = build_information_result()
    churn = build_churn_result()
    sensitivity = build_sensitivity_result()
    causal = build_causal_result()

    causal_engine.infer.return_value = causal

    result = service.infer_causality(
        information,
        churn,
        sensitivity,
    )

    assert result is causal

    causal_engine.infer.assert_called_once_with(
        information,
        churn,
        sensitivity,
    )


def test_estimate_financials():
    (
        service,
        _,
        _,
        _,
        financial_engine,
    ) = make_service()

    churn = build_churn_result()
    causal = build_causal_result()
    financial = build_financial_result()

    financial_engine.estimate.return_value = financial

    result = service.estimate_financials(
        churn,
        causal,
    )

    assert result is financial

    financial_engine.estimate.assert_called_once_with(
        churn,
        causal,
    )


def test_evaluate_runs_complete_pipeline():
    (
        service,
        churn_engine,
        sensitivity_engine,
        causal_engine,
        financial_engine,
    ) = make_service()

    information = build_information_result()
    churn = build_churn_result()
    sensitivity = build_sensitivity_result()
    causal = build_causal_result()
    financial = build_financial_result()

    churn_engine.predict.return_value = churn
    sensitivity_engine.analyze.return_value = sensitivity
    causal_engine.infer.return_value = causal
    financial_engine.estimate.return_value = financial

    result = service.evaluate(
        information,
    )

    assert result.churn is churn
    assert result.sensitivity is sensitivity
    assert result.causal is causal
    assert result.financial is financial

    churn_engine.predict.assert_called_once_with(
        information,
    )

    sensitivity_engine.analyze.assert_called_once_with(
        information,
        churn,
    )

    causal_engine.infer.assert_called_once_with(
        information,
        churn,
        sensitivity,
    )

    financial_engine.estimate.assert_called_once_with(
        churn,
        causal,
    )


def test_evaluate_sets_metadata():
    (
        service,
        churn_engine,
        sensitivity_engine,
        causal_engine,
        financial_engine,
    ) = make_service()

    information = build_information_result()

    churn_engine.predict.return_value = build_churn_result()
    sensitivity_engine.analyze.return_value = build_sensitivity_result()
    causal_engine.infer.return_value = build_causal_result()
    financial_engine.estimate.return_value = build_financial_result()

    result = service.evaluate(
        information,
    )

    assert result.metadata["service"] == "ImpactService"

    assert result.metadata[
        "information_record_count"
    ] == 1