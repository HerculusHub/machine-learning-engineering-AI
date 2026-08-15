
"""
Churn Result

Architecture v2.3 (Frozen MVP)

Represents the output produced by the ChurnEngine.

This model contains prediction results only.
Business causal reasoning and financial calculations
belong to downstream Impact Layer components.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mobile_ai_system.impact.models.feature_vector import (
    FeatureVector,
)


@dataclass(slots=True)
class ChurnResult:
    """
    Predicted customer churn.

    Attributes
    ----------
    predicted_churn_rate:
        Predicted probability/rate of customer churn.

        Expected range:

            0.0 <= predicted_churn_rate <= 1.0

    confidence:
        Confidence associated with the prediction.

        For the Frozen MVP this is derived from the
        distance of the predicted probability from
        the classification boundary.

    feature_vector:
        Exact FeatureVector used to produce the prediction.

        This allows the SensitivityEngine to analyse
        exactly the same features used by the churn model.

    metadata:
        Additional model and inference information.
    """

    predicted_churn_rate: float = 0.0

    confidence: float = 1.0

    feature_vector: FeatureVector = field(
        default_factory=FeatureVector,
    )

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    # ---------------------------------------------------------
    # Validation / normalization
    # ---------------------------------------------------------

    def __post_init__(self) -> None:
        """
        Normalize probability-like values to [0.0, 1.0].
        """

        self.predicted_churn_rate = max(
            0.0,
            min(
                1.0,
                float(self.predicted_churn_rate),
            ),
        )

        self.confidence = max(
            0.0,
            min(
                1.0,
                float(self.confidence),
            ),
        )

    # ---------------------------------------------------------
    # Convenience properties
    # ---------------------------------------------------------

    @property
    def probability(self) -> float:
        """
        Backward-compatible alias for predicted_churn_rate.
        """

        return self.predicted_churn_rate

    @property
    def predicted_churn(self) -> bool:
        """
        Return the binary churn classification.

        Frozen MVP threshold:

            probability >= 0.5
        """

        return self.predicted_churn_rate >= 0.5

    @property
    def has_churn(self) -> bool:
        """
        Backward-compatible convenience property.

        Returns True when the predicted churn rate
        is greater than zero.
        """

        return self.predicted_churn_rate > 0.0

    @property
    def model_name(self) -> str:
        """
        Return the model name stored in metadata.

        This preserves compatibility with the earlier
        ChurnResult contract while avoiding duplicate state.
        """

        return str(
            self.metadata.get(
                "model",
                "",
            )
        )

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the result for reporting, APIs,
        persistence, or diagnostics.
        """

        return {
            "predicted_churn_rate": self.predicted_churn_rate,
            "probability": self.probability,
            "predicted_churn": self.predicted_churn,
            "confidence": self.confidence,
            "model_name": self.model_name,
            "feature_vector": {
                "features": dict(
                    self.feature_vector.features,
                ),
                "metadata": dict(
                    self.feature_vector.metadata,
                ),
            },
            "metadata": dict(
                self.metadata,
            ),
        }
