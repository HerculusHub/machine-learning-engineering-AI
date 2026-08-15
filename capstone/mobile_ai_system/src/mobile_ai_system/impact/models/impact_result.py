
"""
Impact Result

Architecture v2.3 (Frozen MVP)

Represents the complete business impact assessment
produced by the Impact Layer.

This is the primary output returned by the ImpactAgent
and consumed by the Report Layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from mobile_ai_system.impact.models.causal_result import (
    CausalResult,
)
from mobile_ai_system.impact.models.churn_result import (
    ChurnResult,
)
from mobile_ai_system.impact.models.financial_result import (
    FinancialResult,
)
from mobile_ai_system.impact.models.sensitivity_result import (
    SensitivityResult,
)


@dataclass(slots=True)
class ImpactResult:
    """
    Aggregated output of the Impact Layer.

    Combines:

        • Churn prediction
        • Sensitivity analysis
        • Causal reasoning
        • Financial impact estimation
    """

    churn: ChurnResult | None = None

    sensitivity: SensitivityResult | None = None

    causal: CausalResult | None = None

    financial: FinancialResult | None = None

    summary: str = ""

    risk_level: str = "low"
    """
    Expected values:

        low
        medium
        high
        critical
    """

    metadata: dict = field(default_factory=dict)

    # ---------------------------------------------------------
    # Availability
    # ---------------------------------------------------------

    @property
    def has_churn_result(self) -> bool:

        return self.churn is not None

    @property
    def has_sensitivity_result(self) -> bool:

        return self.sensitivity is not None

    @property
    def has_causal_result(self) -> bool:

        return self.causal is not None

    @property
    def has_financial_result(self) -> bool:

        return self.financial is not None

    @property
    def is_complete(self) -> bool:
        """
        Returns True if all major analyses are available.
        """

        return (
            self.has_churn_result
            and self.has_sensitivity_result
            and self.has_causal_result
            and self.has_financial_result
        )

    # ---------------------------------------------------------
    # Executive Metrics
    # ---------------------------------------------------------

    @property
    def estimated_revenue_loss(self) -> float:

        if self.financial is None:
            return 0.0

        return self.financial.estimated_revenue_loss

    @property
    def estimated_profit_loss(self) -> float:

        if self.financial is None:
            return 0.0

        return self.financial.estimated_profit_loss

    @property
    def estimated_customer_loss(self) -> int:

        if self.financial is None:
            return 0

        return self.financial.estimated_customer_loss

    @property
    def predicted_churn_rate(self) -> float:

        if self.churn is None:
            return 0.0

        return self.churn.predicted_churn_rate

    # ---------------------------------------------------------
    # Utility
    # ---------------------------------------------------------

    def executive_summary(self) -> str:
        """
        Generate a concise executive summary.

        Used by the Report Layer when no custom summary
        has been generated yet.
        """

        if self.summary:
            return self.summary

        parts: list[str] = []

        if self.churn is not None:

            parts.append(
                f"Predicted churn rate: "
                f"{self.churn.predicted_churn_rate:.2%}"
            )

        if self.financial is not None:

            parts.append(
                f"Estimated revenue loss: "
                f"${self.financial.estimated_revenue_loss:,.0f}"
            )

            parts.append(
                f"Estimated customer loss: "
                f"{self.financial.estimated_customer_loss:,}"
            )

        if self.causal is not None and not self.causal.is_empty:

            top = self.causal.top_factors(1)

            if top:
                factor = top[0]

                parts.append(
                    f"Primary driver: "
                    f"{factor.affected_feature}"
                )

        parts.append(f"Risk level: {self.risk_level}")

        return " | ".join(parts)

