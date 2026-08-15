"""
Impact Service

Architecture v2.3 (Frozen MVP)

Responsibilities
----------------
Coordinate the complete Impact Layer pipeline.

The service itself contains no prediction,
sensitivity-analysis, causal-inference, or
financial-calculation business logic.

Execution flow
--------------
InformationResult
    ↓
ChurnEngine
    ↓
ChurnResult
    ↓
SensitivityEngine
    ↓
SensitivityResult
    ↓
CausalEngine
    ↓
CausalResult
    ↓
FinancialEngine
    ↓
FinancialResult
    ↓
ImpactResult
"""

from __future__ import annotations

from mobile_ai_system.application.models.information_result import (
    InformationResult,
)
from mobile_ai_system.impact.interfaces.i_causal_engine import (
    ICausalEngine,
)
from mobile_ai_system.impact.interfaces.i_churn_engine import (
    IChurnEngine,
)
from mobile_ai_system.impact.interfaces.i_financial_engine import (
    IFinancialEngine,
)
from mobile_ai_system.impact.interfaces.i_impact_service import (
    IImpactService,
)
from mobile_ai_system.impact.interfaces.i_sensitivity_engine import (
    ISensitivityEngine,
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
from mobile_ai_system.impact.models.impact_result import (
    ImpactResult,
)
from mobile_ai_system.impact.models.sensitivity_result import (
    SensitivityResult,
)


class ImpactService(IImpactService):
    """
    Default Impact Layer orchestration service.

    The service delegates all analytical work to
    specialized engines.
    """

    def __init__(
        self,
        churn_engine: IChurnEngine,
        sensitivity_engine: ISensitivityEngine,
        causal_engine: ICausalEngine,
        financial_engine: IFinancialEngine,
    ) -> None:
        self._churn_engine = churn_engine
        self._sensitivity_engine = sensitivity_engine
        self._causal_engine = causal_engine
        self._financial_engine = financial_engine

    # ---------------------------------------------------------
    # Complete pipeline
    # ---------------------------------------------------------

    def evaluate(
        self,
        information: InformationResult,
    ) -> ImpactResult:
        """
        Execute the complete Impact Layer pipeline.
        """

        churn = self.predict_churn(
            information,
        )

        sensitivity = self.analyze_sensitivity(
            information,
            churn,
        )

        causal = self.infer_causality(
            information,
            churn,
            sensitivity,
        )

        financial = self.estimate_financials(
            churn,
            causal,
        )

        return ImpactResult(
            churn=churn,
            sensitivity=sensitivity,
            causal=causal,
            financial=financial,
            metadata={
                "service": "ImpactService",
                "information_record_count": (
                    information.total_records
                ),
            },
        )

    # ---------------------------------------------------------
    # Churn
    # ---------------------------------------------------------

    def predict_churn(
        self,
        information: InformationResult,
    ) -> ChurnResult:
        """
        Execute customer churn prediction.
        """

        return self._churn_engine.predict(
            information,
        )

    # ---------------------------------------------------------
    # Sensitivity
    # ---------------------------------------------------------

    def analyze_sensitivity(
        self,
        information: InformationResult,
        churn: ChurnResult,
    ) -> SensitivityResult:
        """
        Execute feature sensitivity analysis.
        """

        return self._sensitivity_engine.analyze(
            information,
            churn,
        )

    # ---------------------------------------------------------
    # Causal inference
    # ---------------------------------------------------------

    def infer_causality(
        self,
        information: InformationResult,
        churn: ChurnResult,
        sensitivity: SensitivityResult,
    ) -> CausalResult:
        """
        Execute causal inference.
        """

        return self._causal_engine.infer(
            information,
            churn,
            sensitivity,
        )

    # ---------------------------------------------------------
    # Financial impact
    # ---------------------------------------------------------

    def estimate_financials(
        self,
        churn: ChurnResult,
        causal: CausalResult,
    ) -> FinancialResult:
        """
        Execute financial-impact estimation.
        """

        return self._financial_engine.estimate(
            churn,
            causal,
        )

    # ---------------------------------------------------------
    # Engine access
    # ---------------------------------------------------------

    @property
    def churn_engine(self) -> IChurnEngine:
        """
        Return the configured churn engine.
        """

        return self._churn_engine

    @property
    def sensitivity_engine(self) -> ISensitivityEngine:
        """
        Return the configured sensitivity engine.
        """

        return self._sensitivity_engine

    @property
    def causal_engine(self) -> ICausalEngine:
        """
        Return the configured causal engine.
        """

        return self._causal_engine

    @property
    def financial_engine(self) -> IFinancialEngine:
        """
        Return the configured financial engine.
        """

        return self._financial_engine