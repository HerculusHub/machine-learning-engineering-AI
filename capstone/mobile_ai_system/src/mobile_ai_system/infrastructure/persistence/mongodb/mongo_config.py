"""
MongoDB Configuration

Architecture v2.3 (Frozen MVP)

Immutable configuration object used by the MongoDB
infrastructure layer.
"""

from __future__ import annotations

from dataclasses import dataclass

from mobile_ai_system.core.config import Settings


@dataclass(frozen=True)
class MongoConfig:
    """
    MongoDB configuration used by repositories and
    MongoClientManager.
    """

    connection_string: str

    database_name: str

    collection_name: str

    @classmethod
    def from_settings(
        cls,
        settings: Settings,
    ) -> "MongoConfig":
        """
        Build a MongoConfig from application settings.
        """

        return cls(
            connection_string=settings.mongo_uri,
            database_name=settings.mongo_database,
            collection_name=settings.mongo_collection,
        )