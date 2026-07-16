"""
Episode Repository

Architecture v2.0 (Frozen)
"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from psycopg.types.json import Json

from mobile_ai_system.infrastructure.logging.logger import get_logger
from mobile_ai_system.infrastructure.persistence.postgresql.repositories.base_repository import (
    BaseRepository,
)

logger = get_logger(__name__)


class EpisodeRepository(BaseRepository):
    """
    Repository for workflow episodes.
    """

    # ---------------------------------------------------------
    # Create
    # ---------------------------------------------------------

    def save(
        self,
        user_request: str,
        workflow_state: dict,
        evaluation_score: float | None = None,
    ) -> str:

        episode_id = str(uuid4())
        created_at = datetime.utcnow()

        sql = """
        INSERT INTO episodes (
            episode_id,
            created_at,
            user_request,
            workflow_state,
            evaluation_score
        )
        VALUES (%s, %s, %s, %s, %s);
        """

        with self.session() as session:
            client = self.client(session)

            client.execute_non_query(
                sql,
                (
                    episode_id,
                    created_at,
                    user_request,
                    Json(workflow_state),
                    evaluation_score,
                ),
            )

        logger.info("Episode saved: %s", episode_id)

        return episode_id

    # ---------------------------------------------------------
    # Read
    # ---------------------------------------------------------

    def get(self, episode_id: str):

        sql = """
        SELECT *
        FROM episodes
        WHERE episode_id = %s;
        """

        with self.session() as session:
            client = self.client(session)

            return client.fetch_one(sql, (episode_id,))

    # ---------------------------------------------------------
    # Latest
    # ---------------------------------------------------------

    def latest(self, limit: int = 5):

        sql = """
        SELECT *
        FROM episodes
        ORDER BY created_at DESC
        LIMIT %s;
        """

        with self.session() as session:
            client = self.client(session)

            return client.fetch_all(sql, (limit,))

    # ---------------------------------------------------------
    # Count
    # ---------------------------------------------------------

    def count(self) -> int:

        sql = """
        SELECT COUNT(*) AS total
        FROM episodes;
        """

        with self.session() as session:
            client = self.client(session)

            row = client.fetch_one(sql)

        return row["total"]

    # ---------------------------------------------------------
    # Delete
    # ---------------------------------------------------------

    def clear(self):

        sql = "DELETE FROM episodes;"

        with self.session() as session:
            client = self.client(session)

            client.execute_non_query(sql)

        logger.info("Episode table cleared.")