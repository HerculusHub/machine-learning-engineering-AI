"""
Mongo Repository Factory
"""

from __future__ import annotations

from mobile_ai_system.infrastructure.persistence.mongodb.mongo_information_repository import (
    MongoInformationRepository,
)


class RepositoryFactory:

    @staticmethod
    def create_information_repository(
        collection,
    ) -> MongoInformationRepository:

        return MongoInformationRepository(
            collection,
        )