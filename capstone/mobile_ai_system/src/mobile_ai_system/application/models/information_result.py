"""
Information Result

Architecture v2.3 (Frozen MVP)

Represents structured information retrieved from
the information layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class InformationResult:
    """
    Output of the Information Agent.
    """

    records: list[dict] = field(default_factory=list)

    metadata: dict = field(default_factory=dict)

    @property
    def total_records(self) -> int:
        return len(self.records)

    @property
    def is_empty(self) -> bool:
        return self.total_records == 0