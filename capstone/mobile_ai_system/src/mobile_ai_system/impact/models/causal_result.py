"""
Causal Result

Architecture v2.3 (Frozen MVP)

Represents the complete output produced by the
CausalEngine.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from mobile_ai_system.impact.models.causal_factor import (
    CausalFactor,
)


@dataclass(slots=True)
class CausalResult:
    """
    Output of the CausalEngine.

    Contains all inferred causal factors together with
    metadata describing how the inference was performed.
    """

    #
    # Ordered by estimated importance
    #
    causes: list[CausalFactor] = field(
        default_factory=list,
    )

    #
    # Overall confidence of the causal analysis.
    #
    confidence: float = 1.0

    #
    # Additional diagnostic information.
    #
    metadata: dict = field(
        default_factory=dict,
    )

    @property
    def cause_count(self) -> int:
        """
        Number of inferred causes.
        """
        return len(self.causes)

    @property
    def has_causes(self) -> bool:
        """
        Returns True if at least one cause exists.
        """
        return self.cause_count > 0

    @property
    def primary_cause(self) -> CausalFactor | None:
        """
        Returns the highest-ranked causal factor.

        Returns
        -------
        CausalFactor | None
        """

        if not self.causes:
            return None

        return self.causes[0]

    def add_cause(
        self,
        cause: CausalFactor,
    ) -> None:
        """
        Append a causal factor.
        """

        self.causes.append(cause)

    def sort_by_effect(
        self,
        descending: bool = True,
    ) -> None:
        """
        Sort causes by absolute estimated effect.
        """

        self.causes.sort(
            key=lambda c: abs(c.estimated_effect),
            reverse=descending,
        )

    def to_dict(self) -> dict:
        """
        Serialize the result.

        Useful for APIs and reporting.
        """

        return {
            "confidence": self.confidence,
            "causes": [
                {
                    "factor": cause.factor,
                    "estimated_effect": cause.estimated_effect,
                    "confidence": cause.confidence,
                    "explanation": cause.explanation,
                    "supporting_events": cause.supporting_events,
                    "metadata": cause.metadata,
                }
                for cause in self.causes
            ],
            "metadata": self.metadata,
        }