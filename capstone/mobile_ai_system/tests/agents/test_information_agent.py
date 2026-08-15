from mobile_ai_system.agents.information.information_agent import (
    InformationAgent,
)

from mobile_ai_system.application.models.information_result import (
    InformationResult,
)

from mobile_ai_system.application.models.request_model import Request
from mobile_ai_system.application.parsers.parse_result import ParseResult


class DummyService:

    def retrieve(self, request):

        return InformationResult(

            records=[{"operator": "Verizon"}]

        )


def test_information_agent():

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

    agent = InformationAgent(

        DummyService(),

    )

    result = agent.execute(

        parse_result,

    )

    assert result.total_records == 1

    assert result.records[0]["operator"] == "Verizon"