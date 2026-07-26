"""
Request Model

Architecture v2.3 (Frozen)

Responsibilities
----------------
- Represent a normalized user request.
- Carry structured information through the Application Layer.
- Remain independent of agents and LLMs.

Does NOT
---------
- Execute business logic.
- Store workflow state.
- Call external services.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Request:
    """
    Canonical user request used by the Application Layer.

    Attributes
    ----------
    user_request:
        Original user input.

    task_type:
        Parsed task category, e.g.
        "impact_analysis",
        "market_analysis",
        "competitive_analysis".

    target:
        Primary analysis target.
        Example:
            "Verizon"

    parameters:
        Structured parameters extracted from the request.

    metadata:
        Additional runtime metadata.
    """

    user_request: str

    task_type: str = ""

    target: str = ""

    parameters: dict[str, Any] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the request into a dictionary.
        """

        return {
            "user_request": self.user_request,
            "task_type": self.task_type,
            "target": self.target,
            "parameters": dict(self.parameters),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Request":
        """
        Construct a Request from a dictionary.
        """

        return cls(
            user_request=data.get("user_request", ""),
            task_type=data.get("task_type", ""),
            target=data.get("target", ""),
            parameters=data.get("parameters", {}),
            metadata=data.get("metadata", {}),
        )