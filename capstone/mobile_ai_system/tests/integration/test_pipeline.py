"""
Integration test for the canonical application pipeline.

Architecture v2.3 (Frozen MVP)

This test verifies that Bootstrap exposes a runnable
ApplicationRunner and that the runner can execute a
minimal canonical pipeline against PipelineContext.
"""

from __future__ import annotations

from mobile_ai_system.application.models.execution_plan import (
    ExecutionPlan,
)
from mobile_ai_system.application.models.pipeline_context import (
    PipelineContext,
)


def test_pipeline(container):
    """
    ApplicationRunner should execute a registered
    pipeline stage and return PipelineContext.
    """

    runner = container.resolve(
        "runner"
    )

    context = PipelineContext()

    def information_handler(
        ctx: PipelineContext,
    ) -> PipelineContext:
        ctx.information_result = {
            "records": [],
        }

        return ctx

    runner.register(
        "information",
        information_handler,
    )

    plan = ExecutionPlan(
        steps=[
            "information",
        ]
    )

    result = runner.run(
        plan,
        context,
    )

    assert result is context

    assert result.information_result == {
        "records": [],
    }