"""
Execution Planner

Architecture v2.3 (Frozen MVP)

Responsibilities
----------------
Create an execution plan from a parsed request.

Release 0.1
-----------
Deterministic planner.

Does NOT
--------
- Execute services
- Call agents
- Use LLMs
"""

from __future__ import annotations

from mobile_ai_system.application.models.execution_plan import (
    ExecutionPlan,
)
from mobile_ai_system.application.parsers.parse_result import (
    ParseResult,
)


class ExecutionPlanner:
    """
    Deterministic workflow planner.

    Release 0.1 produces the canonical MVP pipeline:

        information
            ↓
        impact
            ↓
        report
            ↓
        evaluation
    """

    DEFAULT_PIPELINE = [
        "information",
        "impact",
        "report",
        "evaluation",
    ]

    def build_plan(
        self,
        parse_result: ParseResult,
    ) -> ExecutionPlan:
        """
        Build the deterministic MVP execution plan.
        """

        return ExecutionPlan(
            steps=self.DEFAULT_PIPELINE.copy(),
            metadata={
                "intent": parse_result.request.intent,
                "parser": parse_result.parser_name,
                "confidence": parse_result.confidence,
            },
        )