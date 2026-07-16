from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ArtifactState:
    """
    Generated artifacts.
    """

    reports: dict[str, str] = field(
        default_factory=dict
    )

    tables: dict[str, object] = field(
        default_factory=dict
    )

    charts: dict[str, object] = field(
        default_factory=dict
    )

    files: dict[str, str] = field(
        default_factory=dict
    )