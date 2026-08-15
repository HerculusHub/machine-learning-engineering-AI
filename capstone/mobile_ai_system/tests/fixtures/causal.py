"""
CausalResult fixtures.
"""

from __future__ import annotations

from mobile_ai_system.impact.models.causal_result import (
    CausalResult,
)

from mobile_ai_system.impact.models.causal_factor import (
    CausalFactor,
)


def build_causal_result() -> CausalResult:

    result = CausalResult(

        confidence=0.91,

    )

    result.add_cause(

        CausalFactor(

            factor="price_cut",

            estimated_effect=0.60,

            confidence=0.91,

            explanation="Competitor price reduction.",

            supporting_events=[],

        )

    )

    return result