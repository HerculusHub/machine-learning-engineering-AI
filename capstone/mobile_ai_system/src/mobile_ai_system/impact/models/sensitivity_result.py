"""
Sensitivity Result

Architecture v2.3 (Frozen MVP)

Represents the output of the Sensitivity Engine.

The Sensitivity Engine analyzes which features have the
greatest influence on predicted customer churn.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class FeatureSensitivity:
    """
    Sensitivity metrics for a single feature.
    """

    feature_name: str

    importance_score: float

    sensitivity_score: float

    shap_value: float | None = None

    direction: str = "unknown"
    """
    Expected values:

        "positive"
        "negative"
        "unknown"

    positive:
        increasing the feature increases churn

    negative:
        increasing the feature reduces churn
    """


@dataclass(slots=True)
class SensitivityResult:
    """
    Output of the Sensitivity Engine.
    """

    features: list[FeatureSensitivity] = field(
        default_factory=list
    )

    model_name: str = ""

    metadata: dict = field(default_factory=dict)

    @property
    def total_features(self) -> int:
        """
        Number of analyzed features.
        """
        return len(self.features)

    @property
    def is_empty(self) -> bool:
        return len(self.features) == 0

    def ranked_features(
        self,
    ) -> list[FeatureSensitivity]:
        """
        Return features ranked by importance.
        """

        return sorted(
            self.features,
            key=lambda feature: feature.importance_score,
            reverse=True,
        )

    def top_features(
        self,
        k: int = 10,
    ) -> list[FeatureSensitivity]:
        """
        Return the Top-K most important features.
        """

        return self.ranked_features()[:k]

    def feature(
        self,
        name: str,
    ) -> FeatureSensitivity | None:
        """
        Retrieve one feature by name.
        """

        for feature in self.features:

            if feature.feature_name == name:
                return feature

        return None