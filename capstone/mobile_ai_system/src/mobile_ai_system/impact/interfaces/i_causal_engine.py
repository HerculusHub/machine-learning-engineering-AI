"""
Causal Engine Interface

Architecture v2.3 (Frozen MVP)

Defines the interface for business causal inference.

The Causal Engine is responsible for identifying
the most probable business causes of predicted
customer churn by combining:

    • Information layer output
    • Churn prediction
    • Sensitivity analysis
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from mobile_ai_system.application.models.information_result import (
    InformationResult,
)
from mobile_ai_system.impact.models.causal_result import (
    CausalResult,
)
from mobile_ai_system.impact.models.churn_result import (
    ChurnResult,
)
from mobile_ai_system.impact.models.sensitivity_result import (
    SensitivityResult,
)


class ICausalEngine(ABC):
    """
    Interface for business causal inference.

    Implementations may use:

        • Rule-based reasoning (MVP)
        • Structural Causal Models
        • DoWhy
        • EconML
        • Bayesian Networks
        • Causal Forests
    """

    @abstractmethod
    def infer(
        self,
        information: InformationResult,
        churn: ChurnResult,
        sensitivity: SensitivityResult,
    ) -> CausalResult:
        """
        Infer the most probable business causes of
        predicted customer churn.

        Parameters
        ----------
        information
            Output from the Information Agent.

        churn
            Output from the Churn Engine.

        sensitivity
            Output from the Sensitivity Engine.

        Returns
        -------
        CausalResult
            Ranked causal explanations with
            confidence estimates and supporting
            business evidence.
        """
        raise NotImplementedError