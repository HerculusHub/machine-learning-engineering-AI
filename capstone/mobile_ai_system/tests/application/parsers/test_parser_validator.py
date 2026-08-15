from mobile_ai_system.application.models.request_model import Request
from mobile_ai_system.application.parsers.parser_validator import ParserValidator


def test_valid_request():

    request = Request(
        user_request="Analyze Verizon pricing.",
        intent="analysis",
        operators=["verizon"],
        topics=["pricing"],
    )

    valid, warnings, errors = ParserValidator().validate(request)

    assert valid
    assert errors == []


def test_missing_operator():

    request = Request(
        user_request="Analyze pricing.",
        intent="analysis",
        topics=["pricing"],
    )

    valid, warnings, errors = ParserValidator().validate(request)

    assert valid
    assert len(warnings) == 1


def test_empty_request():

    request = Request()

    valid, warnings, errors = ParserValidator().validate(request)

    assert not valid
    assert len(errors) == 1