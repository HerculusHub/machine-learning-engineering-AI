from mobile_ai_system.application.parsers.rule_parser import RuleParser


def test_att_alias():

    parser = RuleParser()

    request = parser.parse(
        "Analyze ATT pricing."
    )

    assert request.operators == [
        "at&t",
    ]


def test_att_duplicate():

    parser = RuleParser()

    request = parser.parse(
        "Analyze ATT and AT&T pricing."
    )

    assert request.operators == [
        "at&t",
    ]


def test_tmobile_alias():

    parser = RuleParser()

    request = parser.parse(
        "Analyze TMobile promotion."
    )

    assert request.operators == [
        "t-mobile",
    ]


def test_multiple_topics():

    parser = RuleParser()

    request = parser.parse(
        "Analyze Verizon pricing and customer churn."
    )

    assert set(request.topics) == {
        "pricing",
        "customer churn",
    }


def test_multiple_events():

    parser = RuleParser()

    request = parser.parse(
        "Analyze Verizon promotion after outage."
    )

    assert set(request.events) == {
        "promotion",
        "outage",
    }