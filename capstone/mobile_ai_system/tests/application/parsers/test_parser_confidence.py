from mobile_ai_system.application.models.request_model import Request
from mobile_ai_system.application.parsers.parser_confidence import ParserConfidence


def test_high_confidence():

    request = Request(
        user_request="Analyze Verizon pricing.",
        intent="analysis",
        operators=["verizon"],
        topics=["pricing"],
    )

    confidence = ParserConfidence().score(request)

    assert confidence >= 0.8


def test_low_confidence():

    request = Request(
        user_request="Hello",
        intent="analysis",
    )

    confidence = ParserConfidence().score(request)

    assert confidence < 0.5