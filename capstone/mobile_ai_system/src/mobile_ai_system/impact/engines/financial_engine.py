
"""
Financial Engine

Architecture v2.3 (Frozen MVP)

Responsibilities
----------------
Translate predicted customer churn into
business and financial impact.

Current MVP
-----------
Uses deterministic formulas and configurable
business assumptions.

Future Versions
---------------
- Company-specific financial models
- CLV estimation
- EBITDA impact
- Cash flow impact
- Market valuation impact
"""

from __future__ import annotations

from mobile_ai_system.impact.interfaces.i_financial_engine import (
    IFinancialEngine,
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


class FinancialEngine(IFinancialEngine):
    """
    Estimate financial impact from predicted churn.

    The Frozen MVP uses configurable business assumptions
    and deterministic formulas.

    More advanced financial models can replace the internal
    calculations later without changing the public interface.
    """

    def __init__(
        self,
        customer_base: int = 1_000_000,
        monthly_arpu: float = 60.0,
        gross_margin: float = 0.35,
    ) -> None:
        if customer_base < 0:
            raise ValueError(
                "customer_base must be non-negative."
            )

        if monthly_arpu < 0:
            raise ValueError(
                "monthly_arpu must be non-negative."
            )

        if not 0.0 <= gross_margin <= 1.0:
            raise ValueError(
                "gross_margin must be between 0.0 and 1.0."
            )

        self.customer_base = customer_base
        self.monthly_arpu = monthly_arpu
        self.gross_margin = gross_margin

    # ---------------------------------------------------------
    # Engine information
    # ---------------------------------------------------------

    @property
    def engine_name(self) -> str:
        """
        Return the financial engine name.
        """

        return "deterministic"

    def supports_scenario_analysis(self) -> bool:
        """
        Frozen MVP does not yet support
        multi-scenario financial analysis.
        """

        return False

    def supports_discounted_cashflow(self) -> bool:
        """
        Frozen MVP does not yet support
        discounted cash-flow analysis.
        """

        return False

    # ---------------------------------------------------------
    # Estimation
    # ---------------------------------------------------------

    def estimate(
        self,
        churn: ChurnResult,
        causal: CausalResult,
    ) -> FinancialResult:
        """
        Estimate financial impact.

        Parameters
        ----------
        churn
            Predicted churn result.

        causal
            Causal inference result.

        Returns
        -------
        FinancialResult
        """

        churn_rate = max(
            0.0,
            min(
                float(
                    churn.predicted_churn_rate
                ),
                1.0,
            ),
        )

        # -----------------------------------------------------
        # Customer loss
        # -----------------------------------------------------

        lost_customers = (
            churn_rate
            * self.customer_base
        )

        # -----------------------------------------------------
        # Revenue loss
        # -----------------------------------------------------

        monthly_revenue_loss = (
            lost_customers
            * self.monthly_arpu
        )

        annual_revenue_loss = (
            monthly_revenue_loss
            * 12.0
        )

        # -----------------------------------------------------
        # Profit loss
        # -----------------------------------------------------

        monthly_profit_loss = (
            monthly_revenue_loss
            * self.gross_margin
        )

        annual_profit_loss = (
            annual_revenue_loss
            * self.gross_margin
        )

        # -----------------------------------------------------
        # Market-share approximation
        # -----------------------------------------------------

        market_share_loss = churn_rate

        return FinancialResult(
            predicted_churn_rate=churn_rate,
            lost_customers=lost_customers,
            monthly_revenue_loss=monthly_revenue_loss,
            annual_revenue_loss=annual_revenue_loss,
            monthly_profit_loss=monthly_profit_loss,
            annual_profit_loss=annual_profit_loss,
            market_share_loss=market_share_loss,
            customer_base=self.customer_base,
            arpu=self.monthly_arpu,
            gross_margin=self.gross_margin,
            confidence=causal.confidence,
            metadata={
                "engine": self.engine_name,
                "method": "deterministic",
                "causal_factor_count": causal.cause_count,
            },
        )
