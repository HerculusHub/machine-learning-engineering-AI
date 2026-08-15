"""
Unit tests for MongoInformationRepository.

Architecture v2.3 (Frozen MVP)

Tests the MongoDB repository boundary without requiring
a live MongoDB database.
"""

from __future__ import annotations

from unittest.mock import MagicMock

from mobile_ai_system.application.models.information_result import (
    InformationResult,
)
from mobile_ai_system.application.models.request_model import (
    Request,
)
from mobile_ai_system.infrastructure.persistence.mongodb.mongo_information_repository import (
    MongoInformationRepository,
)


def test_search_returns_information_result():
    """
    search() should execute the generated MongoDB query
    and return an InformationResult.
    """

    collection = MagicMock()

    collection.find.return_value = [
        {
            "event_id": "EVT-001",
            "operator_name": "Verizon",
        },
        {
            "event_id": "EVT-002",
            "operator_name": "Verizon",
        },
    ]

    repository = MongoInformationRepository(
        collection,
    )

    request = Request(
        user_request="Analyze Verizon",
        operators=[
            "Verizon",
        ],
    )

    result = repository.search(
        request,
    )

    assert isinstance(
        result,
        InformationResult,
    )

    assert result.total_records == 2

    assert result.records[0][
        "event_id"
    ] == "EVT-001"

    assert result.records[1][
        "event_id"
    ] == "EVT-002"

    collection.find.assert_called_once()


def test_find_by_event_id():
    """
    find_by_event_id() should query MongoDB using
    the event identifier.
    """

    collection = MagicMock()

    expected = {
        "event_id": "EVT-001",
        "operator_name": "Verizon",
    }

    collection.find_one.return_value = expected

    repository = MongoInformationRepository(
        collection,
    )

    result = repository.find_by_event_id(
        "EVT-001"
    )

    assert result == expected

    collection.find_one.assert_called_once_with(
        {
            "event_id": "EVT-001",
        }
    )


def test_find_by_operator():
    """
    find_by_operator() should query by operator,
    sort newest first, and apply the requested limit.
    """

    collection = MagicMock()

    cursor = MagicMock()

    collection.find.return_value = cursor

    cursor.sort.return_value = cursor
    cursor.limit.return_value = [
        {
            "event_id": "EVT-001",
            "operator_name": "Verizon",
        }
    ]

    repository = MongoInformationRepository(
        collection,
    )

    result = repository.find_by_operator(
        "Verizon",
        limit=10,
    )

    collection.find.assert_called_once_with(
        {
            "operator_name": "Verizon",
        }
    )

    cursor.sort.assert_called_once_with(
        "event_date",
        -1,
    )

    cursor.limit.assert_called_once_with(
        10
    )

    assert len(result) == 1

    assert result[0][
        "operator_name"
    ] == "Verizon"


def test_find_recent():
    """
    find_recent() should query events newer than
    the calculated cutoff and apply ordering/limit.
    """

    collection = MagicMock()

    cursor = MagicMock()

    collection.find.return_value = cursor

    cursor.sort.return_value = cursor
    cursor.limit.return_value = [
        {
            "event_id": "EVT-RECENT",
        }
    ]

    repository = MongoInformationRepository(
        collection,
    )

    result = repository.find_recent(
        days=30,
        limit=5,
    )

    collection.find.assert_called_once()

    query = collection.find.call_args.args[0]

    assert "event_date" in query

    assert "$gte" in query[
        "event_date"
    ]

    cursor.sort.assert_called_once_with(
        "event_date",
        -1,
    )

    cursor.limit.assert_called_once_with(
        5
    )

    assert len(result) == 1

    assert result[0][
        "event_id"
    ] == "EVT-RECENT"


def test_count():
    """
    count() should return the collection document count.
    """

    collection = MagicMock()

    collection.count_documents.return_value = 5250

    repository = MongoInformationRepository(
        collection,
    )

    result = repository.count()

    assert result == 5250

    collection.count_documents.assert_called_once_with(
        {}
    )


def test_search_returns_empty_result():
    """
    search() should return an empty InformationResult
    when MongoDB finds no matching documents.
    """

    collection = MagicMock()

    collection.find.return_value = []

    repository = MongoInformationRepository(
        collection,
    )

    request = Request(
        user_request="Analyze unknown operator",
        operators=[
            "Unknown Operator",
        ],
    )

    result = repository.search(
        request,
    )

    assert isinstance(
        result,
        InformationResult,
    )

    assert result.records == []

    assert result.total_records == 0

    assert "query" in result.metadata