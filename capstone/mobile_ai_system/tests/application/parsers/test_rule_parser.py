"""
Tests for RuleParser.

Architecture v2.3 (Frozen Release 0.1)
"""

from mobile_ai_system.application.parsers.rule_parser import RuleParser


def test_parse_complete_request():

    parser = RuleParser()

    request = parser.parse(
        "Analyze Verizon customer churn after price increase."
    )

    assert request.intent == "analysis"

    assert request.operators == [
        "verizon",
    ]

    assert request.topics == [
        "customer churn",
    ]

    assert request.events == [
        "price increase",
    ]


def test_parse_unknown_operator():

    parser = RuleParser()

    request = parser.parse(
        "Analyze market performance."
    )

    assert request.intent == "analysis"

    assert request.operators == []

    assert request.topics == []

    assert request.events == []


def test_default_intent():

    parser = RuleParser()

    request = parser.parse(
        "Verizon customer churn"
    )

    assert request.intent == "analysis"

    assert request.operators == [
        "verizon",
    ]

    assert request.topics == [
        "customer churn",
    ]


def test_compare_request():

    parser = RuleParser()

    request = parser.parse(
        "Compare Verizon and AT&T pricing."
    )

    assert request.intent == "comparison"

    assert set(request.operators) == {
        "verizon",
        "at&t",
    }

    assert request.topics == [
        "pricing",
    ]


def test_compare_request_alias():

    parser = RuleParser()

    request = parser.parse(
        "Compare Verizon and ATT pricing."
    )

    assert request.intent == "comparison"

    assert set(request.operators) == {
        "verizon",
        "at&t",
    }


def test_report_request():

    parser = RuleParser()

    request = parser.parse(
        "Report Verizon subscriber growth."
    )

    assert request.intent == "report"

    assert request.operators == [
        "verizon",
    ]

    assert request.topics == [
        "subscriber growth",
    ]


def test_multiple_events():

    parser = RuleParser()

    request = parser.parse(
        "Analyze Verizon promotion after outage."
    )

    assert request.intent == "analysis"

    assert request.operators == [
        "verizon",
    ]

    assert set(request.events) == {
        "promotion",
        "outage",
    }


def test_no_matches():

    parser = RuleParser()

    request = parser.parse(
        "Hello, how are you today?"
    )

    assert request.intent == "analysis"

    assert request.operators == []

    assert request.topics == []

    assert request.events == []