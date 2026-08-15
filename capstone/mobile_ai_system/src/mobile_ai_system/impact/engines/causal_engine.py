"""
Causal Engine

Architecture v2.3 (Frozen MVP)

Responsibilities
----------------
Infer the most probable business causes of predicted
customer churn.

Current MVP
-----------
Rule-based causal inference using outputs from:

- InformationResult
- ChurnResult
- SensitivityResult

Future versions
---------------
- DoWhy
- EconML
- Bayesian Networks
- Structural Causal Models
- Causal Forests
"""

from __future__ import annotations

from typing import Any

from mobile_ai_system.application.models.information_result import (
    InformationResult,
)
from mobile_ai_system.impact.interfaces.i_causal_engine import (
    ICausalEngine,
)
from mobile_ai_system.impact.models.causal_factor import (
    CausalFactor,
)
from mobile_ai_system.impact.models.causal_result import (
    CausalResult,
)
from mobile_ai_system.impact.models.churn_result import (
    ChurnResult,
)
from mobile_ai_system.impact.models.sensitivity_result import (
    FeatureSensitivity,
    SensitivityResult,
)


class CausalEngine(ICausalEngine):
    """
    Default causal inference engine.

    The Frozen MVP converts sensitivity results into
    candidate causal factors using deterministic rules.

    This is intentionally not a statistical causal model.
    Future implementations can replace the inference logic
    without changing the public interface.
    """

    # ---------------------------------------------------------
    # Engine information
    # ---------------------------------------------------------

    @property
    def engine_name(self) -> str:
        """
        Return the causal engine name.
        """

        return "rule_based"

    def supports_counterfactuals(self) -> bool:
        """
        Frozen MVP does not support counterfactual inference.
        """

        return False

    def supports_multiple_events(self) -> bool:
        """
        The MVP can preserve evidence from multiple events.

        It does not yet estimate interaction effects between
        simultaneous events.
        """

        return True

    # ---------------------------------------------------------
    # Public inference
    # ---------------------------------------------------------

    def infer(
        self,
        information: InformationResult,
        churn: ChurnResult,
        sensitivity: SensitivityResult,
    ) -> CausalResult:
        """
        Infer candidate business causes of predicted churn.

        Parameters
        ----------
        information
            Structured event records from the Information Layer.

        churn
            Churn prediction produced by ChurnEngine.

        sensitivity
            Feature-level sensitivity analysis.

        Returns
        -------
        CausalResult
            Ranked candidate causal factors.
        """

        supporting_events = self._extract_supporting_events(
            information,
        )

        result = CausalResult(
            confidence=churn.confidence,
            metadata={
                "engine": self.engine_name,
                "method": "rule-based",
                "information_record_count": (
                    information.total_records
                ),
                "sensitivity_feature_count": (
                    sensitivity.total_features
                ),
            },
        )

        for feature in sensitivity.ranked_features():

            factor = self._build_causal_factor(
                feature=feature,
                churn=churn,
                supporting_events=supporting_events,
            )

            result.add_cause(
                factor,
            )

        result.sort_by_effect()

        return result

    # ---------------------------------------------------------
    # Causal factor construction
    # ---------------------------------------------------------

    def _build_causal_factor(
        self,
        feature: FeatureSensitivity,
        churn: ChurnResult,
        supporting_events: list[str],
    ) -> CausalFactor:
        """
        Convert one FeatureSensitivity into a CausalFactor.

        Frozen MVP uses feature importance as a placeholder
        for estimated effect.

        A future formal causal model will replace this rule.
        """

        estimated_effect = float(
            feature.importance_score
        )

        explanation = self._build_explanation(
            feature,
        )

        return CausalFactor(
            factor=feature.feature_name,
            estimated_effect=estimated_effect,
            confidence=churn.confidence,
            explanation=explanation,
            supporting_events=list(
                supporting_events,
            ),
            metadata={
                "source": "SensitivityEngine",
                "importance_score": (
                    feature.importance_score
                ),
                "sensitivity_score": (
                    feature.sensitivity_score
                ),
                "shap_value": (
                    feature.shap_value
                ),
                "direction": (
                    feature.direction
                ),
            },
        )

    # ---------------------------------------------------------
    # Supporting evidence
    # ---------------------------------------------------------

    @staticmethod
    def _extract_supporting_events(
        information: InformationResult,
    ) -> list[str]:
        """
        Extract event identifiers from InformationResult.

        InformationResult.records currently contains dictionaries.
        Records without an event_id are ignored.
        """

        event_ids: list[str] = []

        for record in information.records:

            event_id = CausalEngine._extract_event_id(
                record,
            )

            if event_id:
                event_ids.append(
                    event_id,
                )

        return event_ids

    @staticmethod
    def _extract_event_id(
        record: Any,
    ) -> str:
        """
        Extract an event ID from either a dictionary or
        an object-style record.

        Supporting both forms keeps this boundary robust if the
        Information Layer later introduces typed event records.
        """

        if isinstance(
            record,
            dict,
        ):
            value = record.get(
                "event_id",
                "",
            )

            return str(value) if value else ""

        value = getattr(
            record,
            "event_id",
            "",
        )

        return str(value) if value else ""

    # ---------------------------------------------------------
    # Explanation
    # ---------------------------------------------------------

    @staticmethod
    def _build_explanation(
        feature: FeatureSensitivity,
    ) -> str:
        """
        Build the Frozen MVP explanation text.
        """

        if feature.direction == "positive":
            relationship = (
                "is associated with increased churn"
            )

        elif feature.direction == "negative":
            relationship = (
                "is associated with reduced churn"
            )

        else:
            relationship = (
                "is identified as a potential churn driver"
            )

        return (
            f"Feature '{feature.feature_name}' "
            f"{relationship}. "
            f"Importance score="
            f"{feature.importance_score:.4f}; "
            f"sensitivity score="
            f"{feature.sensitivity_score:.4f}."
        )