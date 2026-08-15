"""
Impact Service Interface

Architecture v2.3 (Frozen MVP)

Coordinates all engines within the Impact Layer.

The service itself performs no prediction,
no causal inference,
and no financial calculations.

Its responsibility is orchestration.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from mobile_ai_system.application.models.information_result import (
    InformationResult,
)
from mobile_ai_system.impact.models.churn_result import (
    ChurnResult,
)
from mobile_ai_system.impact.models.sensitivity_result import (
    SensitivityResult,
)
from mobile_ai_system.impact.models.causal_result import (
    CausalResult,
)
from mobile_ai_system.impact.models.financial_result import (
    FinancialResult,
)
from mobile_ai_system.impact.models.impact_result import (
    ImpactResult,
)


class IImpactService(ABC):
    """
    Interface for the Impact Layer orchestration service.

    The service coordinates the sequential execution
    of all analytical engines.
    """

    @abstractmethod
    def evaluate(
        self,
        information: InformationResult,
    ) -> ImpactResult:
        """
        Execute the complete impact analysis pipeline.

        Parameters
        ----------
        information
            Information Layer output.

        Returns
        -------
        ImpactResult
        """
        ...

    @abstractmethod
    def predict_churn(
        self,
        information: InformationResult,
    ) -> ChurnResult:
        """
        Execute only the churn prediction stage.
        """
        ...

    @abstractmethod
    def analyze_sensitivity(
        self,
        information: InformationResult,
        churn: ChurnResult,
    ) -> SensitivityResult:
        """
        Execute only the sensitivity analysis stage.
        """
        ...

    @abstractmethod
    def infer_causality(
        self,
        information: InformationResult,
        churn: ChurnResult,
        sensitivity: SensitivityResult,
    ) -> CausalResult:
        """
        Execute only the causal inference stage.
        """
        ...

    @abstractmethod
    def estimate_financials(
        self,
        churn: ChurnResult,
        causal: CausalResult,
    ) -> FinancialResult:
        """
        Execute only the financial estimation stage.
        """
        ...