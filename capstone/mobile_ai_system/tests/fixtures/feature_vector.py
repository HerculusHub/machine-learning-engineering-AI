"""
FeatureVector fixtures.
"""

from __future__ import annotations

from mobile_ai_system.impact.models.feature_vector import (
    FeatureVector,
)


def build_feature_vector() -> FeatureVector:
    """
    Sample feature vector used by unit tests.
    """

    return FeatureVector(

        features={

            "price_cut": 1.0,

            "network_outage": 0.0,

            "promotion": 0.0,

            "customer_complaints": 0.15,

        },

        metadata={

            "fixture": True,

        },

    )