"""
Execution Factory

Architecture v2.3 (Frozen MVP)

Creates standard execution plans.

No execution occurs here.
"""

from __future__ import annotations

from mobile_ai_system.application.models.execution_plan import (
    ExecutionPlan,
)


class ExecutionFactory:
    """
    Factory for constructing standard pipeline plans.
    """

    @staticmethod
    def information_only() -> ExecutionPlan:
        """
        Execute only the Information stage.
        """

        return ExecutionPlan(
            steps=[
                "information",
            ]
        )

    @staticmethod
    def default_plan() -> ExecutionPlan:
        """
        Execute Information and Impact stages.
        """

        return ExecutionPlan(
            steps=[
                "information",
                "impact",
            ]
        )

    @staticmethod
    def full_pipeline() -> ExecutionPlan:
        """
        Execute the complete Frozen MVP pipeline.
        """

        return ExecutionPlan(
            steps=[
                "information",
                "impact",
                "report",
                "evaluation",
            ]
        )