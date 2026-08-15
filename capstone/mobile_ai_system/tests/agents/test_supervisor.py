from mobile_ai_system.agents.supervisor.supervisor_agent import (
    SupervisorAgent,
)

from mobile_ai_system.application.models.request_model import Request
from mobile_ai_system.application.parsers.parse_result import ParseResult


def test_supervisor_builds_plan():

    request = Request(

        user_request="Analyze Verizon",

        intent="analysis",

    )

    parse_result = ParseResult(

        request=request,

        parser_name="RuleParser",

        confidence=1.0,

        valid=True,

    )

    supervisor = SupervisorAgent()

    plan = supervisor.plan(parse_result)

    assert plan.total_steps == 4

    assert plan.steps[0] == "information"

    assert plan.steps == [
        "information",
        "impact",
        "report",
        "evaluation",
    ]