"""
Tests for MongoQueryBuilder

Architecture v2.3 (Frozen MVP)
"""

from datetime import datetime

from mobile_ai_system.application.models.request_model import Request
from mobile_ai_system.infrastructure.persistence.mongodb.mongo_query_builder import (
    MongoQueryBuilder,
)


def test_empty_request_returns_empty_query():

    builder = MongoQueryBuilder()

    request = Request(
        user_request="",
        intent="analysis",
    )

    query = builder.build(request)

    assert query == {}


def test_operator_filter():

    builder = MongoQueryBuilder()

    request = Request(
        user_request="Analyze Verizon",
        intent="analysis",
        operators=["Verizon"],
    )

    query = builder.build(request)

    assert query == {
        "operator_name": {
            "$in": ["Verizon"],
        }
    }


def test_topic_filter():

    builder = MongoQueryBuilder()

    request = Request(
        user_request="5G",
        intent="analysis",
        topics=["5G"],
    )

    query = builder.build(request)

    assert query == {
        "keywords": {
            "$in": ["5G"],
        }
    }


def test_event_filter():

    builder = MongoQueryBuilder()

    request = Request(
        user_request="Network outage",
        intent="analysis",
        events=["Network"],
    )

    query = builder.build(request)

    assert query == {
        "event_category": {
            "$in": ["Network"],
        }
    }


def test_date_filter():

    builder = MongoQueryBuilder()

    request = Request(
        user_request="Recent events",
        intent="analysis",
        parameters={
            "days": 30,
        },
    )

    query = builder.build(request)

    assert "event_date" in query
    assert "$gte" in query["event_date"]
    assert isinstance(
        query["event_date"]["$gte"],
        datetime,
    )


def test_combined_query():

    builder = MongoQueryBuilder()

    request = Request(
        user_request="Analyze Verizon 5G",
        intent="analysis",
        operators=["Verizon"],
        topics=["5G"],
        events=["Network"],
        parameters={
            "days": 30,
        },
    )

    query = builder.build(request)

    assert query["operator_name"] == {
        "$in": ["Verizon"],
    }

    assert query["keywords"] == {
        "$in": ["5G"],
    }

    assert query["event_category"] == {
        "$in": ["Network"],
    }

    assert "event_date" in query
    assert "$gte" in query["event_date"]