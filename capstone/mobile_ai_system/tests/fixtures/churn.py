"""
ChurnResult fixtures.
"""

from __future__ import annotations

from mobile_ai_system.impact.models.churn_result import (
    ChurnResult,
)


def build_churn_result() -> ChurnResult:

    return ChurnResult(

        predicted_probability=0.08,

        confidence=0.93,

        metadata={

            "fixture": True,

        },

    )