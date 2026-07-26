import logging
from typing import Optional

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from mobile_ai_system.core.config import get_settings

logger = logging.getLogger(__name__)


class MongoDBClient:
    """
    MongoDB client for the Industry Database.
    """

    def __init__(self):

        self.settings = get_settings()

        self.client = MongoClient(
            self.settings.mongo_uri,
            serverSelectionTimeoutMS=5000,
        )

        
        self.db = self.client["industry_db"]

    # ----------------------------------------------------
    # Connection
    # ----------------------------------------------------

    def health_check(self) -> bool:

        try:
            self.client.admin.command("ping")
            return True

        except Exception as e:
            logger.exception(e)
            return False

    # ----------------------------------------------------
    # Search
    # ----------------------------------------------------

    def search_events(
        self,
        query: Optional[str] = None,
        operator_name: Optional[str] = None,
        event_category: Optional[str] = None,
        limit: int = 20,
    ):
        """
        Search industry events.

        Parameters
        ----------
        query
            Natural-language keyword search using MongoDB text index.

        operator_name
            Exact operator name filter.

        event_category
            Exact event category filter.

        limit
            Maximum number of returned documents.
        """

        collection = self.db["operator_events"]

        filter_query = {}

        # ---------- full text search ----------

        if query:

            filter_query["$text"] = {
                "$search": query
            }

        # ---------- structured filters ----------

        if operator_name:

            filter_query["operator_name"] = operator_name

        if event_category:

            filter_query["event_category"] = event_category

        try:

            cursor = (
                collection
                .find(filter_query)
                .limit(limit)
            )

            return list(cursor)

        except PyMongoError as e:

            logger.exception(e)

            return []

    # ----------------------------------------------------
    # Utility
    # ----------------------------------------------------

    def count_documents(self) -> int:

        return self.db["operator_events"].count_documents({})

    def close(self):

        self.client.close()