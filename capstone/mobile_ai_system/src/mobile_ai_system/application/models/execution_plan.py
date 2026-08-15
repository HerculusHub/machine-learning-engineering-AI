from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ExecutionPlan:
    """
    Execution plan produced by the Supervisor.

    Architecture v2.3 (Frozen MVP)
    """

    steps: list[str] = field(default_factory=list)

    metadata: dict = field(default_factory=dict)

    disabled_steps: set[str] = field(default_factory=set)

    @property
    def total_steps(self) -> int:
        return len(self.steps)

    def add_step(self, step: str) -> None:
        if step not in self.steps:
            self.steps.append(step)

    def disable(self, step: str) -> None:
        self.disabled_steps.add(step)

    def enable(self, step: str) -> None:
        self.disabled_steps.discard(step)

    def is_enabled(self, step: str) -> bool:
        return step not in self.disabled_steps

    def enabled_steps(self) -> list[str]:
        return [
            step
            for step in self.steps
            if self.is_enabled(step)
        ]