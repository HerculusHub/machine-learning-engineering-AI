"""
Request Model

Architecture v2.3 (Frozen)

Responsibilities
----------------
Represent a normalized user request throughout the
Application Layer.

Does NOT
---------
- Execute business logic
- Call external services
- Use LLMs
- Store workflow state
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Request:
    """
    Canonical request object used throughout the system.

    Release 0.1

    Produced by:
        RequestParser

    Consumed by:
        Supervisor
        InformationService
        ImpactService
        ReportService
        EvaluationService
    """

    # --------------------------------------------------
    # Original user input
    # --------------------------------------------------

    user_request: str = ""

    # --------------------------------------------------
    # Parsed intent
    # --------------------------------------------------

    intent: str = ""

    # --------------------------------------------------
    # Extracted entities
    # --------------------------------------------------

    operators: list[str] = field(default_factory=list)

    topics: list[str] = field(default_factory=list)

    events: list[str] = field(default_factory=list)

    # --------------------------------------------------
    # Application task
    # --------------------------------------------------

    task_type: str = ""

    # --------------------------------------------------
    # Optional parameters
    # --------------------------------------------------

    parameters: dict[str, Any] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)

    # ==================================================
    # Backward Compatibility
    # ==================================================

    @property
    def operator(self) -> str | None:
        """
        Return the primary operator.

        Kept for Release 0.1 compatibility.
        """

        return self.operators[0] if self.operators else None

    @property
    def topic(self) -> str | None:

        return self.topics[0] if self.topics else None

    @property
    def event(self) -> str | None:

        return self.events[0] if self.events else None

    @property
    def target(self) -> str | None:
        """
        Alias used by downstream services.

        Currently the primary operator.
        """

        return self.operator

    # ==================================================
    # Serialization
    # ==================================================

    def to_dict(self) -> dict[str, Any]:

        return {
            "user_request": self.user_request,
            "intent": self.intent,
            "operators": list(self.operators),
            "topics": list(self.topics),
            "events": list(self.events),
            "task_type": self.task_type,
            "parameters": dict(self.parameters),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Request":

        return cls(
            user_request=data.get("user_request", ""),
            intent=data.get("intent", ""),
            operators=list(data.get("operators", [])),
            topics=list(data.get("topics", [])),
            events=list(data.get("events", [])),
            task_type=data.get("task_type", ""),
            parameters=dict(data.get("parameters", {})),
            metadata=dict(data.get("metadata", {})),
        )