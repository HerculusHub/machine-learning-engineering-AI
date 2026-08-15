from __future__ import annotations

import pytest

from mobile_ai_system.application.runner import (
    ApplicationRunner,
)
from mobile_ai_system.application.models.execution_plan import (
    ExecutionPlan,
)
from mobile_ai_system.application.models.pipeline_context import (
    PipelineContext,
)


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def make_context() -> PipelineContext:

    return PipelineContext()


# ---------------------------------------------------------
# Registration
# ---------------------------------------------------------

def test_register_handler():

    runner = ApplicationRunner()

    runner.register(
        "information",
        lambda ctx: ctx,
    )

    assert runner.has_handler("information")


# ---------------------------------------------------------
# Successful execution
# ---------------------------------------------------------

def test_run_pipeline():

    runner = ApplicationRunner()

    executed = []

    def information(ctx):

        executed.append("information")
        return ctx

    def impact(ctx):

        executed.append("impact")
        return ctx

    runner.register(
        "information",
        information,
    )

    runner.register(
        "impact",
        impact,
    )

    plan = ExecutionPlan(
        steps=[
            "information",
            "impact",
        ]
    )

    context = make_context()

    result = runner.run(
        plan,
        context,
    )

    assert result is context

    assert executed == [
        "information",
        "impact",
    ]


# ---------------------------------------------------------
# Disabled step
# ---------------------------------------------------------

def test_disabled_step_is_skipped():

    runner = ApplicationRunner()

    executed = []

    def information(ctx):

        executed.append("information")
        return ctx

    def impact(ctx):

        executed.append("impact")
        return ctx

    runner.register(
        "information",
        information,
    )

    runner.register(
        "impact",
        impact,
    )

    plan = ExecutionPlan(
        steps=[
            "information",
            "impact",
        ]
    )

    plan.disable("impact")

    runner.run(
        plan,
        make_context(),
    )

    assert executed == [
        "information",
    ]


# ---------------------------------------------------------
# Missing handler
# ---------------------------------------------------------

def test_missing_handler():

    runner = ApplicationRunner()

    plan = ExecutionPlan(
        steps=[
            "information",
        ]
    )

    with pytest.raises(KeyError):

        runner.run(
            plan,
            make_context(),
        )


# ---------------------------------------------------------
# Handler returns None
# ---------------------------------------------------------

def test_handler_returns_none():

    runner = ApplicationRunner()

    runner.register(
        "information",
        lambda ctx: None,
    )

    plan = ExecutionPlan(
        steps=[
            "information",
        ]
    )

    with pytest.raises(RuntimeError):

        runner.run(
            plan,
            make_context(),
        )


# ---------------------------------------------------------
# Wrong return type
# ---------------------------------------------------------

def test_wrong_return_type():

    runner = ApplicationRunner()

    runner.register(
        "information",
        lambda ctx: {},
    )

    plan = ExecutionPlan(
        steps=[
            "information",
        ]
    )

    with pytest.raises(TypeError):

        runner.run(
            plan,
            make_context(),
        )


# ---------------------------------------------------------
# Clear handlers
# ---------------------------------------------------------

def test_clear_handlers():

    runner = ApplicationRunner()

    runner.register(
        "information",
        lambda ctx: ctx,
    )

    assert runner.has_handler("information")

    runner.clear()

    assert not runner.has_handler("information")


# ---------------------------------------------------------
# Handlers property
# ---------------------------------------------------------

def test_handlers_property_returns_copy():

    runner = ApplicationRunner()

    runner.register(
        "information",
        lambda ctx: ctx,
    )

    handlers = runner.handlers

    handlers.clear()

    assert runner.has_handler("information")