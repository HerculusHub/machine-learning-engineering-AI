"""
Unit tests for MongoInformationRepository.

Architecture v2.3 (Frozen MVP)
"""

from __future__ import annotations

from mobile_ai_system.application.models.information_result import (
    InformationResult,
)
from mobile_ai_system.application.models.request_model import (
    Request,
)
from mobile_ai_system.infrastructure.persistence.mongodb.mongo_information_repository import (
    MongoInformationRepository,
)


class FakeCollection:
    """
    Minimal fake MongoDB collection.
    """

    def find(
        self,
        query,
    ):
        return [
            {
                "operator_name": "Verizon",
                "topic": "customer churn",
            }
        ]


def test_repository_search():
    """
    Repository search should accept a Request
    and return InformationResult.
    """

    repo = MongoInformationRepository(
        FakeCollection(),
    )

    request = Request(
        user_request="Analyze Verizon churn",
        operators=[
            "Verizon",
        ],
    )

    result = repo.search(
        request,
    )

    assert isinstance(
        result,
        InformationResult,
    )

    assert result.total_records == 1

    assert result.records[0][
        "operator_name"
    ] == "Verizon"

    assert "query" in result.metadata