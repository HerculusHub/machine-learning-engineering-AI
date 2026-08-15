"""
Tests for InformationService

Architecture v2.3 (Frozen MVP)
"""

from unittest.mock import MagicMock

from mobile_ai_system.application.models.information_result import (
    InformationResult,
)
from mobile_ai_system.application.models.request_model import (
    Request,
)
from mobile_ai_system.application.services.information_service import (
    InformationService,
)


def make_service():

    repository = MagicMock()

    service = InformationService(repository)

    return service, repository


# ---------------------------------------------------------
# search()
# ---------------------------------------------------------

def test_search():

    service, repository = make_service()

    repository.search.return_value = InformationResult(
        records=[
            {
                "event_id": "1",
            }
        ]
    )

    request = Request(
        user_request="Analyze Verizon",
        intent="analysis",
    )

    result = service.search(request)

    assert result.total_records == 1

    repository.search.assert_called_once_with(request)


# ---------------------------------------------------------
# find_by_event_id()
# ---------------------------------------------------------

def test_find_by_event_id():

    service, repository = make_service()

    repository.find_by_event_id.return_value = {
        "event_id": "ABC",
    }

    result = service.find_by_event_id(
        "ABC",
    )

    assert result["event_id"] == "ABC"

    repository.find_by_event_id.assert_called_once_with(
        "ABC",
    )


# ---------------------------------------------------------
# find_by_operator()
# ---------------------------------------------------------

def test_find_by_operator():

    service, repository = make_service()

    repository.find_by_operator.return_value = [
        {
            "operator_name": "Verizon",
        }
    ]

    result = service.find_by_operator(
        "Verizon",
    )

    assert len(result) == 1

    repository.find_by_operator.assert_called_once_with(
        "Verizon",
    )


# ---------------------------------------------------------
# find_recent()
# ---------------------------------------------------------

def test_find_recent():

    service, repository = make_service()

    repository.find_recent.return_value = [
        {
            "event_id": "RECENT",
        }
    ]

    result = service.find_recent(
        days=30,
    )

    assert len(result) == 1

    repository.find_recent.assert_called_once_with(
        days=30,
    )


# ---------------------------------------------------------
# count()
# ---------------------------------------------------------

def test_count():

    service, repository = make_service()

    repository.count.return_value = 5250

    total = service.count()

    assert total == 5250

    repository.count.assert_called_once()


# ---------------------------------------------------------
# empty result
# ---------------------------------------------------------

def test_empty_search():

    service, repository = make_service()

    repository.search.return_value = InformationResult()

    request = Request(
        user_request="Nothing",
        intent="analysis",
    )

    result = service.search(request)

    assert result.is_empty