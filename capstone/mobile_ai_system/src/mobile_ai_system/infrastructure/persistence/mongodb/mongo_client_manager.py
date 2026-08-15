"""
Mongo Client Manager

Architecture v2.3 (Frozen MVP)

Responsibilities
----------------
- Own exactly one MongoClient instance.
- Provide database and collection access.
- Verify connectivity.
- Cleanly close the connection.

Does NOT
---------
- Read environment variables.
- Know about application configuration.
- Perform dependency injection.
- Execute database queries.
"""

from __future__ import annotations

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError


class MongoClientManager:
    """
    Central MongoDB connection manager.

    A single instance should be shared across the application.
    """

    def __init__(
        self,
        connection_string: str,
        *,
        server_selection_timeout_ms: int = 5000,
    ) -> None:

        self._client = MongoClient(
            connection_string,
            serverSelectionTimeoutMS=server_selection_timeout_ms,
        )

    @property
    def client(self) -> MongoClient:
        """
        Return the underlying MongoClient.
        """
        return self._client

    @property
    def connected(self) -> bool:
        """
        Return True if the MongoDB server is reachable.
        """

        try:
            self._client.admin.command("ping")
            return True

        except PyMongoError:
            return False

    def ping(self) -> bool:
        """
        Verify MongoDB connectivity.
        """

        return self.connected

    def database(
        self,
        database_name: str,
    ) -> Database:
        """
        Return a MongoDB database.
        """

        return self._client[database_name]

    def collection(
        self,
        database_name: str,
        collection_name: str,
    ) -> Collection:
        """
        Return a MongoDB collection.
        """

        return self.database(
            database_name,
        )[collection_name]

    def close(self) -> None:
        """
        Close the MongoDB client.
        """

        try:
            self._client.close()

        except Exception:
            # PyMongo close() is normally safe,
            # but never allow shutdown to fail.
            pass