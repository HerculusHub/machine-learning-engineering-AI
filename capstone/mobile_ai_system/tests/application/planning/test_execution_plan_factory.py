"""
Unit tests for ExecutionFactory.

Architecture v2.3 (Frozen MVP)

ExecutionFactory creates standard ExecutionPlan
instances for common pipeline configurations.
"""

from __future__ import annotations

from mobile_ai_system.application.models.execution_plan import (
    ExecutionPlan,
)
from mobile_ai_system.application.planning.execution_factory import (
    ExecutionFactory,
)


def test_information_only_returns_execution_plan():
    """
    information_only() should return an ExecutionPlan.
    """

    plan = ExecutionFactory.information_only()

    assert isinstance(
        plan,
        ExecutionPlan,
    )


def test_information_only_steps():
    """
    information_only() should contain only the
    Information stage.
    """

    plan = ExecutionFactory.information_only()

    assert plan.steps == [
        "information",
    ]

    assert plan.total_steps == 1


def test_default_plan_returns_execution_plan():
    """
    default_plan() should return an ExecutionPlan.
    """

    plan = ExecutionFactory.default_plan()

    assert isinstance(
        plan,
        ExecutionPlan,
    )


def test_default_plan_steps():
    """
    default_plan() should execute Information
    followed by Impact.
    """

    plan = ExecutionFactory.default_plan()

    assert plan.steps == [
        "information",
        "impact",
    ]

    assert plan.total_steps == 2


def test_full_pipeline_returns_execution_plan():
    """
    full_pipeline() should return an ExecutionPlan.
    """

    plan = ExecutionFactory.full_pipeline()

    assert isinstance(
        plan,
        ExecutionPlan,
    )


def test_full_pipeline_steps():
    """
    full_pipeline() should produce the canonical
    Frozen MVP stage order.
    """

    plan = ExecutionFactory.full_pipeline()

    assert plan.steps == [
        "information",
        "impact",
        "report",
        "evaluation",
    ]

    assert plan.total_steps == 4


def test_factory_plans_are_independent():
    """
    Each factory call should return a new independent plan.
    """

    first = ExecutionFactory.full_pipeline()

    second = ExecutionFactory.full_pipeline()

    assert first is not second

    first.disable(
        "impact"
    )

    first.metadata[
        "source"
    ] = "first"

    assert second.is_enabled(
        "impact"
    ) is True

    assert second.metadata == {}


def test_factory_steps_are_independent():
    """
    Mutating one factory-produced plan should not
    affect another plan.
    """

    first = ExecutionFactory.default_plan()

    second = ExecutionFactory.default_plan()

    first.add_step(
        "report"
    )

    assert first.steps == [
        "information",
        "impact",
        "report",
    ]

    assert second.steps == [
        "information",
        "impact",
    ]


def test_information_only_has_no_disabled_steps():
    """
    Factory-produced plans should have all stages
    enabled by default.
    """

    plan = ExecutionFactory.information_only()

    assert plan.disabled_steps == set()

    assert plan.enabled_steps() == [
        "information",
    ]


def test_default_plan_has_no_disabled_steps():
    """
    Default plan should enable every stage.
    """

    plan = ExecutionFactory.default_plan()

    assert plan.disabled_steps == set()

    assert plan.enabled_steps() == [
        "information",
        "impact",
    ]


def test_full_pipeline_has_no_disabled_steps():
    """
    Full pipeline should enable every MVP stage.
    """

    plan = ExecutionFactory.full_pipeline()

    assert plan.disabled_steps == set()

    assert plan.enabled_steps() == [
        "information",
        "impact",
        "report",
        "evaluation",
    ]