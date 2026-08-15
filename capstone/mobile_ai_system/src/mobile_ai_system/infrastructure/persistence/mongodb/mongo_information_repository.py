"""
Mongo Information Repository

Architecture v2.3 (Frozen MVP)

MongoDB implementation of the
IInformationRepository interface.

Responsibilities
----------------
- Execute MongoDB queries.
- Convert MongoDB documents into application models.
- Hide MongoDB from the application layer.

Does NOT
---------
- Build business logic.
- Perform LLM reasoning.
- Parse user requests.
"""

from __future__ import annotations

from datetime import datetime
from datetime import timedelta
from typing import Any

from pymongo.collection import Collection

from mobile_ai_system.application.interfaces.i_information_repository import (
    IInformationRepository,
)
from mobile_ai_system.application.models.information_result import (
    InformationResult,
)
from mobile_ai_system.application.models.request_model import (
    Request,
)
from mobile_ai_system.infrastructure.persistence.mongodb.mongo_query_builder import (
    MongoQueryBuilder,
)


class MongoInformationRepository(IInformationRepository):
    """
    MongoDB implementation of the information repository.
    """

    def __init__(
        self,
        collection: Collection,
    ) -> None:

        self._collection = collection
        self._query_builder = MongoQueryBuilder()

    # ---------------------------------------------------------
    # Main search
    # ---------------------------------------------------------

    def search(
        self,
        request: Request,
    ) -> InformationResult:
        """
        Execute a MongoDB search using the Request model.
        """

        query = self._query_builder.build(request)

        documents = list(
            self._collection.find(query)
        )

        return InformationResult(
            records=documents,
            metadata={
               "query": query,
            },
        )

    # ---------------------------------------------------------
    # Lookup by event id
    # ---------------------------------------------------------

    def find_by_event_id(
        self,
        event_id: str,
    ) -> dict[str, Any] | None:
        """
        Retrieve one event.
        """

        return self._collection.find_one(
            {
                "event_id": event_id,
            }
        )

    # ---------------------------------------------------------
    # Lookup by operator
    # ---------------------------------------------------------

    def find_by_operator(
        self,
        operator: str,
        limit: int = 20,
    ) -> list[dict]:
        """
        Retrieve recent events for one operator.
        """

        cursor = (
            self._collection
            .find(
                {
                    "operator_name": operator,
                }
            )
            .sort(
                "event_date",
                -1,
            )
            .limit(limit)
        )

        return list(cursor)

    # ---------------------------------------------------------
    # Recent events
    # ---------------------------------------------------------

    def find_recent(
        self,
        days: int = 30,
        limit: int = 20,
    ) -> list[dict]:
        """
        Retrieve events newer than N days.
        """

        cutoff = datetime.utcnow() - timedelta(
            days=days,
        )

        cursor = (
            self._collection
            .find(
                {
                    "event_date": {
                        "$gte": cutoff,
                    }
                }
            )
            .sort(
                "event_date",
                -1,
            )
            .limit(limit)
        )

        return list(cursor)

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def count(
        self,
    ) -> int:
        """
        Return total document count.
        """

        return self._collection.count_documents(
            {}
        )