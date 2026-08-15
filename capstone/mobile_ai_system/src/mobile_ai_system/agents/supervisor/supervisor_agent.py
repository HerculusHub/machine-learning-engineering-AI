"""
Supervisor Agent

Architecture v2.3 (Frozen MVP)

Responsibilities
----------------
Convert ParseResult into ExecutionPlan.

The Supervisor does not execute pipeline stages.
It delegates deterministic planning to ExecutionPlanner.
"""

from __future__ import annotations

from mobile_ai_system.agents.supervisor.execution_planner import (
    ExecutionPlanner,
)
from mobile_ai_system.application.models.execution_plan import (
    ExecutionPlan,
)
from mobile_ai_system.application.parsers.parse_result import (
    ParseResult,
)


class SupervisorAgent:
    """
    Supervisor responsible for producing an ExecutionPlan.

    Release 0.1 uses deterministic planning.

    No retrieval, analysis, reporting, evaluation,
    or LLM execution occurs here.
    """

    def __init__(
        self,
        planner: ExecutionPlanner | None = None,
    ) -> None:
        self._planner = (
            planner
            if planner is not None
            else ExecutionPlanner()
        )

    @property
    def name(self) -> str:
        """
        Return the agent name.
        """

        return "SupervisorAgent"

    def plan(
        self,
        parse_result: ParseResult,
    ) -> ExecutionPlan:
        """
        Build an execution plan from the parsed request.
        """

        return self._planner.build_plan(
            parse_result,
        )