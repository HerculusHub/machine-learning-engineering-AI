"""
FinancialResult fixtures.
"""

from __future__ import annotations

from mobile_ai_system.impact.models.financial_result import (
    FinancialResult,
)


def build_financial_result() -> FinancialResult:

    return FinancialResult(

        predicted_churn_rate=0.08,

        lost_customers=80000,

        monthly_revenue_loss=4_800_000,

        annual_revenue_loss=57_600_000,

        monthly_profit_loss=1_680_000,

        annual_profit_loss=20_160_000,

        market_share_loss=0.08,

        customer_base=1_000_000,

        arpu=60,

        gross_margin=0.35,

        confidence=0.91,

    )