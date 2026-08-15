"""
Financial Result

Architecture v2.3 (Frozen MVP)

Represents the estimated business and financial
impact produced by the FinancialEngine.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class FinancialResult:
    """
    Estimated business impact.

    Produced by the FinancialEngine.
    """

    #
    # Customer impact
    #
    predicted_churn_rate: float = 0.0

    lost_customers: float = 0.0

    #
    # Revenue impact
    #
    monthly_revenue_loss: float = 0.0

    annual_revenue_loss: float = 0.0

    #
    # Profit impact
    #
    monthly_profit_loss: float = 0.0

    annual_profit_loss: float = 0.0

    #
    # Market impact
    #
    market_share_loss: float = 0.0

    #
    # Business assumptions
    #
    customer_base: int = 0

    arpu: float = 0.0

    gross_margin: float = 0.0

    #
    # Confidence
    #
    confidence: float = 1.0

    #
    # Additional diagnostics
    #
    metadata: dict = field(
        default_factory=dict,
    )

    @property
    def has_financial_impact(self) -> bool:
        """
        Returns True if any financial loss
        has been estimated.
        """
        return self.annual_revenue_loss > 0

    @property
    def annual_customer_value_loss(self) -> float:
        """
        Average annual revenue lost per customer.
        """

        if self.lost_customers <= 0:
            return 0.0

        return (
            self.annual_revenue_loss
            / self.lost_customers
        )

    def to_dict(self) -> dict:
        """
        Serialize the result.
        """

        return {

            "predicted_churn_rate": self.predicted_churn_rate,

            "lost_customers": self.lost_customers,

            "monthly_revenue_loss": self.monthly_revenue_loss,

            "annual_revenue_loss": self.annual_revenue_loss,

            "monthly_profit_loss": self.monthly_profit_loss,

            "annual_profit_loss": self.annual_profit_loss,

            "market_share_loss": self.market_share_loss,

            "customer_base": self.customer_base,

            "arpu": self.arpu,

            "gross_margin": self.gross_margin,

            "confidence": self.confidence,

            "metadata": self.metadata,

        }