"""
SensitivityResult fixtures.
"""

from __future__ import annotations

from mobile_ai_system.impact.models.sensitivity_result import (
    SensitivityResult,
)


def build_sensitivity_result() -> SensitivityResult:

    return SensitivityResult(

        feature_importance={

            "price_cut": 0.61,

            "customer_complaints": 0.23,

            "promotion": 0.11,

        },

        top_features=[

            "price_cut",

            "customer_complaints",

            "promotion",

        ],

        metadata={

            "fixture": True,

        },

    )