"""
Tests for RequestParser.

Architecture v2.3 (Frozen)
"""

from mobile_ai_system.application.services.request_parser import RequestParser


def test_parse_verizon_request():

    parser = RequestParser()

    request = parser.parse(
        "Analyze Verizon customer churn after price increase."
    )

    assert request.task_type == "analysis"

    assert request.target == "verizon"

    assert request.parameters["topic"] == "customer churn"

    assert request.parameters["event"] == "price increase"

    assert (
        request.user_request
        == "Analyze Verizon customer churn after price increase."
    )


def test_unknown_operator():

    parser = RequestParser()

    request = parser.parse(
        "Analyze market performance."
    )

    assert request.task_type == "analysis"

    assert request.target == ""

    assert request.parameters == {}


def test_default_intent():

    parser = RequestParser()

    request = parser.parse(
        "Verizon customer churn"
    )

    # No explicit "analyze", so default intent
    assert request.task_type == "analysis"

    assert request.target == "verizon"

    assert request.parameters["topic"] == "customer churn"