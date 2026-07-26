from __future__ import annotations

"""
Reflection Repository

Architecture v2.2 (Frozen)

Responsible for persisting reflection memory.
"""


from mobile_ai_system.infrastructure.persistence.postgresql.repositories.base_repository import (
    BaseRepository,
)

from datetime import datetime
from uuid import uuid4

from psycopg.types.json import Json

from mobile_ai_system.infrastructure.logging.logger import get_logger


logger = get_logger(__name__)


class ReflectionRepository(BaseRepository):
    """
    Repository for reflection memory.
    """

    # ---------------------------------------------------------
    # Create
    # ---------------------------------------------------------

    def save(
        self,
        lesson: str,
        source: str | None = None,
        score: float | None = None,
        metadata: dict | None = None,
    ) -> str:
        """
        Save one reflection.

        Returns
        -------
        reflection_id
        """

        reflection_id = str(uuid4())

        created_at = datetime.utcnow()

        sql = """
        INSERT INTO reflections (

            reflection_id,

            created_at,

            lesson,

            source,

            score,

            metadata

        )

        VALUES (

            %s,

            %s,

            %s,

            %s,

            %s,

            %s

        );
        """

        with self.session() as session:

            client = self.client(session)

            client.execute_non_query(

                sql,

                (

                    reflection_id,

                    created_at,

                    lesson,

                    source,

                    score,

                    Json(metadata or {}),

                ),

            )

        logger.info(
            "Reflection saved: %s",
            reflection_id,
        )

        return reflection_id

    # ---------------------------------------------------------
    # Read
    # ---------------------------------------------------------

    def get(
        self,
        reflection_id: str,
    ):

        sql = """
        SELECT *

        FROM reflections

        WHERE reflection_id = %s;
        """

        with self.session() as session:

            client = self.client(session)

            return client.fetch_one(

                sql,

                (

                    reflection_id,

                ),

            )

    # ---------------------------------------------------------
    # Latest
    # ---------------------------------------------------------

    def latest(
        self,
        limit: int = 5,
    ):

        sql = """
        SELECT *

        FROM reflections

        ORDER BY created_at DESC

        LIMIT %s;
        """

        with self.session() as session:

            client = self.client(session)

            return client.fetch_all(

                sql,

                (

                    limit,

                ),

            )

    # ---------------------------------------------------------
    # Count
    # ---------------------------------------------------------

    def count(self) -> int:

        sql = """
        SELECT COUNT(*) AS total

        FROM reflections;
        """

        with self.session() as session:

            client = self.client(session)

            row = client.fetch_one(sql)

        return row["total"]

    # ---------------------------------------------------------
    # Delete All
    # ---------------------------------------------------------

    def clear(self):

        sql = """
        DELETE FROM reflections;
        """

        with self.session() as session:

            client = self.client(session)

            client.execute_non_query(sql)

        logger.info(
            "Reflection table cleared."
        )