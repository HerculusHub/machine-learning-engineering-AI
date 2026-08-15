"""
Feature Builder

Architecture v2.3 (Frozen MVP)

Converts InformationResult into a FeatureVector.

No machine-learning prediction occurs here.

This component is responsible only for feature
engineering and feature normalization.
"""

from __future__ import annotations

from mobile_ai_system.application.models.information_result import (
    InformationResult,
)
from mobile_ai_system.impact.models.feature_vector import (
    FeatureVector,
)


class FeatureBuilder:
    """
    Converts InformationResult into a FeatureVector.
    """

    @staticmethod
    def build(
        information: InformationResult,
    ) -> FeatureVector:
        """
        Build a FeatureVector.

        Current MVP extracts only a small number
        of high-level features.

        Later this will become the complete ML
        feature engineering pipeline.
        """

        features: dict[str, float] = {}

        #
        # Basic statistics
        #

        features["event_count"] = float(
            information.total_records
        )

        #
        # Future examples
        #
        # features["price_reduction_events"]
        # features["network_outage_events"]
        # features["promotion_events"]
        # features["sentiment_mean"]
        # features["importance_mean"]
        # features["confidence_mean"]
        #

        return FeatureVector(
            features=features,
            metadata={
                "source": "FeatureBuilder",
                "version": "0.1",
            },
        )