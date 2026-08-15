"""
Financial Engine Interface

Architecture v2.3 (Frozen MVP)

Defines the interface for translating predicted
customer churn into financial business impact.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from mobile_ai_system.impact.models.causal_result import (
    CausalResult,
)
from mobile_ai_system.impact.models.churn_result import (
    ChurnResult,
)
from mobile_ai_system.impact.models.financial_result import (
    FinancialResult,
)


class IFinancialEngine(ABC):
    """
    Interface for financial impact estimation.
    """

    @abstractmethod
    def estimate(
        self,
        churn: ChurnResult,
        causal: CausalResult,
    ) -> FinancialResult:
        """
        Estimate business impact.

        Parameters
        ----------
        churn
            Predicted customer churn.

        causal
            Business causes of churn.

        Returns
        -------
        FinancialResult
        """
        raise NotImplementedError