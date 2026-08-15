"""
Pipeline Result

Architecture v2.3 (Frozen)

Represents the final output of one execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PipelineResult:
    """
    Final result returned by ApplicationRunner.
    """

    success: bool = True

    request: Any | None = None

    information: Any | None = None

    impact: Any | None = None

    report: Any | None = None

    evaluation: Any |None = None

    error: str | None = None

    metadata: dict[str, Any] = field(default_factory=dict)