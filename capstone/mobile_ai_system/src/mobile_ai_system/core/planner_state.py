from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class PlannerState:
    """
    Planning state shared by the Planner and Supervisor.

    Phase 2 MVP

    Stores the current execution plan.
    """

    task_queue: list[str] = field(default_factory=list)

    completed_tasks: list[str] = field(default_factory=list)

    current_task: str | None = None

    plan_summary: str = ""