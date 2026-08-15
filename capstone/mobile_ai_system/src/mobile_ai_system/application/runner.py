"""
Application Runner

Architecture v2.3 (Frozen MVP)

Executes an ExecutionPlan sequentially.

The runner knows nothing about business logic.
It simply dispatches registered handlers.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from mobile_ai_system.application.models.execution_plan import (
    ExecutionPlan,
)
from mobile_ai_system.application.models.pipeline_context import (
    PipelineContext,
)


class ApplicationRunner:
    """
    Generic execution engine.

    Each pipeline step is associated with one handler.

    Example

        runner.register(
            "information",
            information_agent.execute,
        )

        runner.register(
            "impact",
            impact_agent.execute,
        )
    """

    def __init__(self) -> None:

        self._handlers: dict[
            str,
            Callable[[PipelineContext], PipelineContext],
        ] = {}

    # ---------------------------------------------------------
    # Registration
    # ---------------------------------------------------------

    def register(
        self,
        step_name: str,
        handler: Callable[
            [PipelineContext],
            PipelineContext,
        ],
    ) -> None:
        """
        Register (or replace) a pipeline handler.
        """

        self._handlers[step_name] = handler

    # ---------------------------------------------------------
    # Query
    # ---------------------------------------------------------

    def has_handler(
        self,
        step_name: str,
    ) -> bool:

        return step_name in self._handlers

    # ---------------------------------------------------------
    # Execution
    # ---------------------------------------------------------

    def run(
        self,
        plan: ExecutionPlan,
        context: PipelineContext,
    ) -> PipelineContext:
        """
        Execute every enabled pipeline step.
        """

        for step_name in plan.steps:

            if not plan.is_enabled(step_name):
                continue

            context = self._execute_step(
                step_name,
                context,
            )

        return context

    # ---------------------------------------------------------
    # Internal
    # ---------------------------------------------------------

    def _execute_step(
        self,
        step_name: str,
        context: PipelineContext,
    ) -> PipelineContext:

        handler = self._handlers.get(step_name)

        if handler is None:

            raise KeyError(
                f"No handler registered for pipeline step "
                f"'{step_name}'."
            )

        result = handler(context)

        if result is None:

            raise RuntimeError(
                f"Pipeline step '{step_name}' returned None."
            )

        if not isinstance(
            result,
            PipelineContext,
        ):

            raise TypeError(
                f"Pipeline step '{step_name}' returned "
                f"{type(result).__name__}; "
                "expected PipelineContext."
            )

        return result

    # ---------------------------------------------------------
    # Utility
    # ---------------------------------------------------------

    def clear(self) -> None:
        """
        Remove every registered handler.
        """

        self._handlers.clear()

    @property
    def handlers(self) -> dict[str, Any]:
        """
        Read-only copy used by unit tests.
        """

        return dict(self._handlers)