"""
Mongo Query Builder

Architecture v2.3 (Frozen MVP)

Converts a Request model into a MongoDB query.

Responsibilities
----------------
- Translate Request -> Mongo query
- Hide MongoDB query syntax
- Produce plain Python dictionaries

Does NOT
---------
- Execute queries
- Access MongoDB
- Perform business logic
"""

from __future__ import annotations

from datetime import datetime
from datetime import timedelta

from mobile_ai_system.application.models.request_model import (
    Request,
)


class MongoQueryBuilder:
    """
    Builds MongoDB queries from Request objects.
    """

    def build(
        self,
        request: Request,
    ) -> dict:
        """
        Build a MongoDB query.

        Empty request returns {}.
        """

        query: dict = {}

        # --------------------------------------------
        # Operator filter
        # --------------------------------------------

        if request.operators:

            query["operator_name"] = {
                "$in": request.operators,
            }

        # --------------------------------------------
        # Topic filter
        # --------------------------------------------

        if request.topics:

            query["keywords"] = {
                "$in": request.topics,
            }

        # --------------------------------------------
        # Event filter
        # --------------------------------------------

        if request.events:

            query["event_category"] = {
                "$in": request.events,
            }

        # --------------------------------------------
        # Date range
        # --------------------------------------------

        days = request.parameters.get("days")

        if days is not None:

            cutoff = datetime.utcnow() - timedelta(
                days=days,
            )

            query["event_date"] = {
                "$gte": cutoff,
            }

        return query