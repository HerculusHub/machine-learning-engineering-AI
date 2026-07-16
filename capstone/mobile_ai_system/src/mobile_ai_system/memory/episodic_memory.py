"""
Episodic Memory

Architecture v2.2 (Frozen)

Persistent workflow memory.
"""

from __future__ import annotations

from mobile_ai_system.memory.memory_manager import (
    MemoryManager,
)


class EpisodicMemory:
    """
    High-level interface for workflow episodes.

    Delegates persistence to MemoryManager.
    """

    def __init__(
        self,
        memory_manager: MemoryManager | None = None,
    ):

        self.memory_manager = (
            memory_manager
            or MemoryManager()
        )

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    def save_episode(
        self,
        user_request: str,
        workflow_state: dict,
        score: float | None = None,
    ) -> str:

        return self.memory_manager.save_episode(
            user_request=user_request,
            workflow_state=workflow_state,
            evaluation_score=score,
        )

    # ---------------------------------------------------------
    # Read
    # ---------------------------------------------------------

    def get_episode(
        self,
        episode_id: str,
    ):

        return self.memory_manager.get_episode(
            episode_id
        )

    # ---------------------------------------------------------
    # Latest
    # ---------------------------------------------------------

    def latest(
        self,
        n: int = 5,
    ):

        return self.memory_manager.latest_episodes(
            n
        )

    # ---------------------------------------------------------
    # Count
    # ---------------------------------------------------------

    def count(
        self,
    ) -> int:

        return self.memory_manager.episode_count()

    # ---------------------------------------------------------
    # Clear
    # ---------------------------------------------------------

    def clear(self):

        self.memory_manager.clear_episodes()