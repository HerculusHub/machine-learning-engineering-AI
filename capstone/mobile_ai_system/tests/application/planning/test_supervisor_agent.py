"""
Unit tests for SupervisorAgent.

Architecture v2.3 (Frozen MVP)

SupervisorAgent is responsible for converting
ParseResult into ExecutionPlan.

It does not execute pipeline stages.
"""

from __future__ import annotations

from mobile_ai_system.agents.supervisor.supervisor_agent import (
    SupervisorAgent,
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


def build_parse_result(
    intent: str = "analysis",
) -> ParseResult:
    """
    Build a minimal ParseResult for Supervisor tests.
    """

    request = Request(
        user_request="Analyze competitor impact.",
        intent=intent,
    )

    return ParseResult(
        request=request,
        parser_name="RuleParser",
        confidence=1.0,
        valid=True,
    )


def test_supervisor_name():
    """
    SupervisorAgent should expose its canonical name.
    """

    agent = SupervisorAgent()

    assert agent.name == "SupervisorAgent"


def test_plan_returns_execution_plan():
    """
    plan() should return an ExecutionPlan.
    """

    agent = SupervisorAgent()

    result = agent.plan(
        build_parse_result(),
    )

    assert isinstance(
        result,
        ExecutionPlan,
    )


def test_plan_contains_canonical_pipeline():
    """
    Supervisor should produce the canonical Frozen MVP
    stage order.
    """

    agent = SupervisorAgent()

    plan = agent.plan(
        build_parse_result(),
    )

    assert plan.steps == [
        "information",
        "impact",
        "report",
        "evaluation",
    ]


def test_plan_preserves_intent_metadata():
    """
    Execution-plan metadata should preserve request intent.
    """

    agent = SupervisorAgent()

    plan = agent.plan(
        build_parse_result(
            intent="comparison",
        ),
    )

    assert plan.metadata[
        "intent"
    ] == "comparison"


def test_plan_preserves_parser_metadata():
    """
    Execution-plan metadata should preserve parser name.
    """

    agent = SupervisorAgent()

    plan = agent.plan(
        build_parse_result(),
    )

    assert plan.metadata[
        "parser"
    ] == "RuleParser"


def test_plan_preserves_confidence_metadata():
    """
    Execution-plan metadata should preserve parser confidence.
    """

    agent = SupervisorAgent()

    plan = agent.plan(
        build_parse_result(),
    )

    assert plan.metadata[
        "confidence"
    ] == 1.0


def test_plan_returns_new_instance_each_time():
    """
    Supervisor planning should return independent plans.
    """

    agent = SupervisorAgent()

    first = agent.plan(
        build_parse_result(),
    )

    second = agent.plan(
        build_parse_result(),
    )

    assert first is not second

    first.disable(
        "impact"
    )

    assert second.is_enabled(
        "impact"
    ) is True


def test_all_pipeline_steps_enabled_by_default():
    """
    Supervisor-generated plans should enable all
    Frozen MVP stages by default.
    """

    agent = SupervisorAgent()

    plan = agent.plan(
        build_parse_result(),
    )

    assert plan.disabled_steps == set()

    assert plan.enabled_steps() == [
        "information",
        "impact",
        "report",
        "evaluation",
    ]