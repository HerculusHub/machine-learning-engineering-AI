from __future__ import annotations

from mobile_ai_system.infrastructure.logging.logger import get_logger
from mobile_ai_system.infrastructure.persistence.postgresql.repositories.base_repository import (
    BaseRepository,
)

logger = get_logger(__name__)


class VectorRepository(BaseRepository):
    """
    Stage 0.3:
    Placeholder repository for vector embeddings.

    No real pgvector logic yet.
    Only interface reservation.
    """

    def save_embedding(self, *args, **kwargs):
        raise NotImplementedError(
            "VectorRepository will be implemented in Release 0.8 (pgvector stage)."
        )

    def get_embedding(self, *args, **kwargs):
        raise NotImplementedError(
            "VectorRepository will be implemented in Release 0.8."
        )

    def similarity_search(self, *args, **kwargs):
        raise NotImplementedError(
            "VectorRepository will be implemented in Release 1.0."
        )