"""
Tests for RequestParser.

Architecture v2.3 (Frozen Release 0.1)
"""

from mobile_ai_system.application.parsers.request_parser import (
    RequestParser,
)


def test_request_parser_delegates():

    parser = RequestParser()

    result = parser.parse(
        "Analyze Verizon customer churn."
    )

    assert result.valid

    assert result.parser_name == "RuleParser"

    assert result.confidence >= 0.9

    request = result.request

    assert request.intent == "analysis"

    assert request.operator == "verizon"

    assert request.topic == "customer churn"
    

def test_request_parser_compare():

    parser = RequestParser()

    result = parser.parse(
        "Compare Verizon and ATT pricing."
    )

    assert result.valid

    request = result.request

    assert request.intent == "comparison"

    assert set(request.operators) == {
        "verizon",
        "at&t",
    }

    assert request.topics == [
        "pricing",
    ]


def test_request_parser_report():

    parser = RequestParser()

    result = parser.parse(
        "Report Verizon subscriber growth."
    )

    assert result.valid

    request = result.request

    assert request.intent == "report"

    assert request.operators == [
        "verizon",
    ]

    assert request.topics == [
        "subscriber growth",
    ]