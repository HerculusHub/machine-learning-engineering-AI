
"""
Unit tests for FinancialEngine.

Architecture v2.3 (Frozen MVP)
"""

import pytest

from mobile_ai_system.impact.engines.financial_engine import (
    FinancialEngine,
)
from mobile_ai_system.impact.models.causal_result import (
    CausalResult,
)
from mobile_ai_system.impact.models.churn_result import (
    ChurnResult,
)
from mobile_ai_system.impact.models.financial_result import (
    FinancialResult,
)


def build_churn_result(
    churn_rate: float = 0.05,
) -> ChurnResult:
    """
    Build a minimal ChurnResult for financial tests.
    """

    return ChurnResult(
        predicted_churn_rate=churn_rate,
        confidence=0.90,
        metadata={
            "model": "test_churn_model",
        },
    )


def build_causal_result() -> CausalResult:
    """
    Build a minimal CausalResult for financial tests.
    """

    return CausalResult(
        confidence=0.80,
        metadata={
            "engine": "test",
        },
    )


def test_financial():
    """
    FinancialEngine should convert churn into
    deterministic financial impact.
    """

    engine = FinancialEngine(
        customer_base=1_000_000,
        monthly_arpu=60.0,
        gross_margin=0.35,
    )

    result = engine.estimate(
        build_churn_result(
            churn_rate=0.05,
        ),
        build_causal_result(),
    )

    assert isinstance(
        result,
        FinancialResult,
    )

    assert result.predicted_churn_rate == pytest.approx(
        0.05
    )

    assert result.lost_customers == pytest.approx(
        50_000
    )

    assert result.monthly_revenue_loss == pytest.approx(
        3_000_000.0
    )

    assert result.annual_revenue_loss == pytest.approx(
        36_000_000.0
    )

    assert result.monthly_profit_loss == pytest.approx(
        1_050_000.0
    )

    assert result.annual_profit_loss == pytest.approx(
        12_600_000.0
    )

    assert result.market_share_loss == pytest.approx(
        0.05
    )

    assert result.customer_base == 1_000_000

    assert result.arpu == pytest.approx(
        60.0
    )

    assert result.gross_margin == pytest.approx(
        0.35
    )

    assert result.confidence == pytest.approx(
        0.80
    )

    assert result.metadata["engine"] == "deterministic"

    assert result.metadata["method"] == "deterministic"


def test_zero_churn_produces_zero_loss():
    """
    Zero predicted churn should produce zero
    customer, revenue, and profit losses.
    """

    engine = FinancialEngine()

    result = engine.estimate(
        build_churn_result(
            churn_rate=0.0,
        ),
        build_causal_result(),
    )

    assert result.lost_customers == pytest.approx(
        0.0
    )

    assert result.monthly_revenue_loss == pytest.approx(
        0.0
    )

    assert result.annual_revenue_loss == pytest.approx(
        0.0
    )

    assert result.monthly_profit_loss == pytest.approx(
        0.0
    )

    assert result.annual_profit_loss == pytest.approx(
        0.0
    )


def test_engine_name():
    """
    FinancialEngine should expose its implementation name.
    """

    engine = FinancialEngine()

    assert engine.engine_name == "deterministic"


def test_scenario_analysis_not_supported():
    """
    Scenario analysis is outside Frozen MVP.
    """

    engine = FinancialEngine()

    assert engine.supports_scenario_analysis() is False


def test_discounted_cashflow_not_supported():
    """
    Discounted cash-flow analysis is outside Frozen MVP.
    """

    engine = FinancialEngine()

    assert engine.supports_discounted_cashflow() is False


def test_invalid_customer_base():
    """
    Negative customer base should be rejected.
    """

    with pytest.raises(
        ValueError,
        match="customer_base",
    ):
        FinancialEngine(
            customer_base=-1,
        )


def test_invalid_monthly_arpu():
    """
    Negative ARPU should be rejected.
    """

    with pytest.raises(
        ValueError,
        match="monthly_arpu",
    ):
        FinancialEngine(
            monthly_arpu=-1.0,
        )


def test_invalid_gross_margin():
    """
    Gross margin must remain within [0, 1].
    """

    with pytest.raises(
        ValueError,
        match="gross_margin",
    ):
        FinancialEngine(
            gross_margin=1.5,
        )
