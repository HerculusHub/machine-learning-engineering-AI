from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class ExecutionRecord:
    """
    One execution step.
    """

    agent: str

    action: str

    observation: str = ""

    tool: str | None = None

    timestamp: datetime = field(
        default_factory=datetime.utcnow
    )


@dataclass(slots=True)
class ExecutionState:
    """
    Runtime execution state.
    """

    history: list[ExecutionRecord] = field(
        default_factory=list
    )

    iteration: int = 0

    max_iterations: int = 3