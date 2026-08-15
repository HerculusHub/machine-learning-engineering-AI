from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FeatureVector:
    """
    Feature representation produced by the Impact Layer.

    Architecture v2.3 (Frozen MVP)

    The FeatureVector is the normalized feature representation
    passed from the FeatureBuilder to downstream Impact engines.

    Attributes
    ----------
    features:
        Dictionary containing feature names and their numeric values.

    metadata:
        Metadata describing how the feature vector was produced.
    """

    features: dict[str, Any] = field(
        default_factory=dict,
    )

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    def get(
        self,
        name: str,
        default: Any = None,
    ) -> Any:
        """
        Return a feature value.

        Parameters
        ----------
        name:
            Feature name.

        default:
            Value returned when the feature does not exist.
        """

        return self.features.get(
            name,
            default,
        )

    def set(
        self,
        name: str,
        value: Any,
    ) -> None:
        """
        Set or replace a feature value.
        """

        self.features[name] = value

    def has(
        self,
        name: str,
    ) -> bool:
        """
        Return True when the feature exists.
        """

        return name in self.features

    @property
    def feature_count(self) -> int:
        """
        Number of features contained in the vector.
        """

        return len(self.features)

    def is_empty(self) -> bool:
        """
        Return True when no features are present.
        """

        return not self.features