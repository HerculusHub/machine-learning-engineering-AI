
"""
Sensitivity Engine

Architecture v2.3 (Frozen MVP)

Responsibilities
----------------
Analyze which features contribute most to predicted
customer churn.

Current MVP
-----------
- Reads the FeatureVector stored in ChurnResult.
- Produces deterministic placeholder sensitivity scores.
- Produces FeatureSensitivity objects.

Future versions
---------------
- SHAP
- Permutation Importance
- Partial Dependence Plots
- ICE
"""

from __future__ import annotations

from mobile_ai_system.application.models.information_result import (
    InformationResult,
)
from mobile_ai_system.impact.interfaces.i_sensitivity_engine import (
    ISensitivityEngine,
)
from mobile_ai_system.impact.models.churn_result import (
    ChurnResult,
)
from mobile_ai_system.impact.models.sensitivity_result import (
    FeatureSensitivity,
    SensitivityResult,
)


class SensitivityEngine(ISensitivityEngine):
    """
    Default implementation of ISensitivityEngine.

    The Frozen MVP uses deterministic placeholder scores.

    The public interface is intentionally stable so that the
    internal implementation can later be replaced by SHAP or
    another explanation algorithm without changing downstream
    components.
    """

    # ---------------------------------------------------------
    # Engine information
    # ---------------------------------------------------------

    @property
    def engine_name(self) -> str:
        """
        Return the name of this sensitivity engine.
        """

        return "placeholder"

    def supports_shap(self) -> bool:
        """
        Return whether SHAP explanations are currently supported.

        Frozen MVP:
            False
        """

        return False

    def supports_global_importance(self) -> bool:
        """
        Return whether global feature importance is supported.

        Frozen MVP:
            False
        """

        return False

    # ---------------------------------------------------------
    # Analysis
    # ---------------------------------------------------------

    def analyze(
        self,
        information: InformationResult,
        churn: ChurnResult,
    ) -> SensitivityResult:
        """
        Analyse feature sensitivity.

        Parameters
        ----------
        information
            Original information-layer result.

            The MVP does not yet use this object directly,
            but it is kept in the interface because future
            sensitivity methods may need event context.

        churn
            Churn prediction containing the exact FeatureVector
            used by the prediction model.

        Returns
        -------
        SensitivityResult
            Structured feature sensitivity results.
        """

        feature_vector = churn.feature_vector

        feature_results: list[FeatureSensitivity] = []

        for feature_name in sorted(
            feature_vector.features.keys()
        ):
            feature_results.append(
                FeatureSensitivity(
                    feature_name=feature_name,
                    importance_score=0.0,
                    sensitivity_score=0.0,
                    shap_value=None,
                    direction="unknown",
                )
            )

        return SensitivityResult(
            features=feature_results,
            model_name=churn.model_name,
            metadata={
                "engine": self.engine_name,
                "method": "placeholder",
                "feature_count": len(feature_results),
                "supports_shap": self.supports_shap(),
                "supports_global_importance": (
                    self.supports_global_importance()
                ),
                "information_record_count": (
                    information.total_records
                ),
            },
        )
