from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mobile_ai_system.memory.memory_manager import MemoryManager

from .planner_state import PlannerState
from .execution_state import ExecutionState
from .artifact_state import ArtifactState
from .metadata_state import MetadataState


@dataclass(slots=True)
class AgentState:
    """
    Canonical state shared by all agents.
    """

    user_request: str

    memory: MemoryManager

    planner: PlannerState = field(
        default_factory=PlannerState
    )

    execution: ExecutionState = field(
        default_factory=ExecutionState
    )

    tool_results: dict[str, Any] = field(
        default_factory=dict
    )

    artifacts: ArtifactState = field(
        default_factory=ArtifactState
    )

    evaluation: dict[str, Any] = field(
        default_factory=dict
    )

    metadata: MetadataState = field(
        default_factory=MetadataState
    )