from mobile_ai_system.application.models.execution_plan import (
    ExecutionPlan,
)


def test_execution_plan_defaults():
    plan = ExecutionPlan()

    assert plan.steps == []
    assert plan.metadata == {}
    assert plan.disabled_steps == set()
    assert plan.total_steps == 0


def test_add_step():
    plan = ExecutionPlan()

    plan.add_step(
        "information"
    )

    assert plan.steps == [
        "information"
    ]


def test_duplicate_step_is_ignored():
    plan = ExecutionPlan(
        steps=[
            "information",
        ]
    )

    plan.add_step(
        "information"
    )

    assert plan.steps == [
        "information"
    ]


def test_disable_step():
    plan = ExecutionPlan(
        steps=[
            "information",
            "impact",
        ]
    )

    plan.disable(
        "impact"
    )

    assert plan.is_enabled(
        "impact"
    ) is False


def test_enable_step():
    plan = ExecutionPlan(
        steps=[
            "impact",
        ]
    )

    plan.disable(
        "impact"
    )

    plan.enable(
        "impact"
    )

    assert plan.is_enabled(
        "impact"
    ) is True


def test_enabled_steps():
    plan = ExecutionPlan(
        steps=[
            "information",
            "impact",
            "report",
        ]
    )

    plan.disable(
        "impact"
    )

    assert plan.enabled_steps() == [
        "information",
        "report",
    ]