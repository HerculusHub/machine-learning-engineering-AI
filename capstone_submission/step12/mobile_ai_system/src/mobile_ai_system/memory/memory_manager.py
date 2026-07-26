"""
Memory Manager

Architecture v2.3 (Frozen)

Responsibilities
----------------
Provides one unified interface for every
persistent memory subsystem.

Current
-------
- Reflection Memory
- Episode Memory

Future
------
- Semantic Memory
- Execution Memory
- Vector Memory

Agents never access repositories directly.
"""

from __future__ import annotations

from mobile_ai_system.infrastructure.logging.logger import get_logger
from mobile_ai_system.infrastructure.persistence.postgresql.repository_provider import (
    RepositoryProvider,
)

logger = get_logger(__name__)


class MemoryManager:
    """
    Central memory service.

    Coordinates all persistent memories.
    """

    def __init__(
        self,
        repositories: RepositoryProvider | None = None,
    ):

        self.repositories = repositories or RepositoryProvider()

    # ==========================================================
    # Reflection Memory
    # ==========================================================

    def save_reflection(
        self,
        lesson: str,
        source: str | None = None,
        score: float | None = None,
        metadata: dict | None = None,
    ) -> str:

        logger.debug("Saving reflection.")

        return self.repositories.reflections.save(
            lesson=lesson,
            source=source,
            score=score,
            metadata=metadata,
        )

    def get_reflection(
        self,
        reflection_id: str,
    ):

        return self.repositories.reflections.get(
            reflection_id
        )

    def latest_reflections(
        self,
        n: int = 5,
        limit: int | None = None,
    ):
        """
        Return latest reflections.

        Accepts both n and limit for compatibility.
        """

        if limit is not None:
            n = limit

        return self.repositories.reflections.latest(n)

    def reflection_count(self) -> int:

        return self.repositories.reflections.count()

    def clear_reflections(self):

        self.repositories.reflections.clear()

    # ==========================================================
    # Episode Memory
    # ==========================================================

    def save_episode(
        self,
        user_request: str,
        workflow_state: dict,
        evaluation_score: float | None = None,
    ) -> str:

        logger.debug("Saving episode.")

        return self.repositories.episodes.save(
            user_request=user_request,
            workflow_state=workflow_state,
            evaluation_score=evaluation_score,
        )

    def get_episode(
        self,
        episode_id: str,
    ):

        return self.repositories.episodes.get(
            episode_id
        )

    def latest_episodes(
        self,
        limit: int = 5,
    ):

        return self.repositories.episodes.latest(limit)

    def episode_count(self) -> int:

        return self.repositories.episodes.count()

    def clear_episodes(self):

        self.repositories.episodes.clear()