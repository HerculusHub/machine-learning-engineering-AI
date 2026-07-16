"""
MongoDB Tool

Architecture v2.3 (Frozen)

Provides MongoDB event retrieval capability.
"""

from __future__ import annotations

from mobile_ai_system.tools.base import BaseTool
from mobile_ai_system.infrastructure.persistence.mongodb.client import (
    MongoDBClient,
)


class MongoTool(BaseTool):
    """
    Tool wrapper for MongoDB.
    """

    NAME = "mongo"

    def __init__(self) -> None:

        self._client: MongoDBClient | None = None

        self._connected = False

    # ---------------------------------------------------------
    # Properties
    # ---------------------------------------------------------

    @property
    def name(self) -> str:

        return "MongoTool"
    
    def health_check(self):
        return True

    # ---------------------------------------------------------
    # Connection
    # ---------------------------------------------------------

    def connect(self) -> None:
        """
        Initialize the MongoDB client.
        """

        if self._client is None:

            self._client = MongoDBClient()

        self._connected = True

    def health_check(self) -> bool:
        """
        Placeholder health check.

        MongoDB connectivity is tested separately.
        """
        return True

    # ---------------------------------------------------------
    # Execute
    # ---------------------------------------------------------

    def execute(
        self,
        query: str,
        limit: int = 20,
    ):
        """
        Standard execution entry point.
        """

        if not self._connected:

            self.connect()

        return self.search(
            query=query,
            limit=limit,
        )

    # ---------------------------------------------------------
    # Search
    # ---------------------------------------------------------

    def search(
        self,
        query: str,
        limit: int = 20,
    ):
        """
        Generic search interface.
        """

        if not self._connected:

            self.connect()

        return self._client.search_events(
            query=query,
            limit=limit,
        )

    def search_events(
        self,
        query: str,
        limit: int = 20,
    ):
        """
        Compatibility wrapper.
        """

        return self.search(
            query=query,
            limit=limit,
        )

    # ---------------------------------------------------------
    # Close
    # ---------------------------------------------------------

    def close(self) -> None:

        if self._client is not None:

            self._client.close()

        self._connected = False