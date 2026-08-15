"""
Tests for ExecutionPlanner.

Architecture v2.3 (Frozen MVP)

The planner produces the canonical MVP execution pipeline:

    information
        ↓
    impact
        ↓
    report
        ↓
    evaluation
"""

from __future__ import annotations

from mobile_ai_system.agents.supervisor.execution_planner import (
    ExecutionPlanner,
)
from mobile_ai_system.application.models.execution_plan import (
    ExecutionPlan,
)
from mobile_ai_system.application.models.request_model import (
    Request,
)
from mobile_ai_system.application.parsers.parse_result import (
    ParseResult,
)


def make_result(
    intent: str = "analysis",
) -> ParseResult:
    """
    Create a minimal valid ParseResult.
    """

    request = Request(
        user_request="Analyze Verizon churn",
        intent=intent,
    )

    return ParseResult(
        request=request,
        parser_name="RuleParser",
        confidence=1.0,
        valid=True,
    )


def test_default_pipeline():
    """
    Planner should create the canonical MVP pipeline.
    """

    planner = ExecutionPlanner()

    plan = planner.build_plan(
        make_result()
    )

    assert isinstance(
        plan,
        ExecutionPlan,
    )

    assert plan.total_steps == 4

    assert plan.steps == [
        "information",
        "impact",
        "report",
        "evaluation",
    ]


def test_plan_preserves_intent_metadata():
    """
    Intent should be propagated into plan metadata.
    """

    planner = ExecutionPlanner()

    plan = planner.build_plan(
        make_result("analysis")
    )

    assert plan.metadata[
        "intent"
    ] == "analysis"


def test_plan_preserves_parser_metadata():
    """
    Parser information should be propagated.
    """

    planner = ExecutionPlanner()

    plan = planner.build_plan(
        make_result()
    )

    assert plan.metadata[
        "parser"
    ] == "RuleParser"


def test_plan_preserves_confidence_metadata():
    """
    Parser confidence should be propagated.
    """

    planner = ExecutionPlanner()

    plan = planner.build_plan(
        make_result()
    )

    assert plan.metadata[
        "confidence"
    ] == 1.0


def test_plans_are_independent():
    """
    Each call should return a new ExecutionPlan.
    """

    planner = ExecutionPlanner()

    first = planner.build_plan(
        make_result()
    )

    second = planner.build_plan(
        make_result()
    )

    assert first is not second

    first.steps.pop()

    assert first.total_steps == 3

    assert second.total_steps == 4


def test_all_steps_enabled_by_default():
    """
    Canonical pipeline stages should initially be enabled.
    """

    planner = ExecutionPlanner()

    plan = planner.build_plan(
        make_result()
    )

    assert plan.enabled_steps() == [
        "information",
        "impact",
        "report",
        "evaluation",
    ]