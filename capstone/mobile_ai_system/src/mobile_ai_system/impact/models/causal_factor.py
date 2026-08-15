"""
Causal Factor

Architecture v2.3 (Frozen MVP)

Represents one inferred business cause.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class CausalFactor:
    """
    One inferred causal factor.
    """

    factor: str

    estimated_effect: float

    confidence: float

    explanation: str = ""

    supporting_events: list[str] = field(
        default_factory=list,
    )

    metadata: dict = field(
        default_factory=dict,
    )