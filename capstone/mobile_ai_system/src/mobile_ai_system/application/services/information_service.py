"""
Information Service

Architecture v2.3 (Frozen MVP)

Responsibilities
----------------
- Collect structured business information
- Aggregate memory context
- Prepare evidence for downstream agents

Does NOT
---------
- Generate reports
- Call an LLM
- Modify workflow state
- Decide execution order
"""

from __future__ import annotations

from mobile_ai_system.application.models.information_result import (
    InformationResult,
)


class InformationService:
    """
    Collect structured information for downstream agents.
    """

    def __init__(
        self,
        mongo_tool=None,
        llm_tool=None,
        web_tool=None,
        memory_manager=None,
    ) -> None:

        self.mongo_tool = mongo_tool
        self.llm_tool = llm_tool          # Reserved for future use
        self.web_tool = web_tool
        self.memory_manager = memory_manager

    # ==========================================================
    # Public API
    # ==========================================================

    def collect_information(self, state: dict) -> InformationResult:
        """
        Collect all structured information required by later agents.

        Release 0.1:
            - Working memory
            - Episodic memory
            - Reflection memory

        Future releases:
            - MongoDB
            - Web search
            - Vector retrieval
        """

        query = self._extract_query(state)

        memory = self._retrieve_memory(query)

        evidence = []

        if memory["episodes"]:
            evidence.extend(memory["episodes"])

        if memory["reflections"]:
            evidence.extend(memory["reflections"])

        return InformationResult(
            query=query,
            summary="",
            evidence=evidence,
            sources=["memory"],
            confidence=1.0,
            metadata={
                "memory": memory,
            },
        )

    # ==========================================================
    # Internal helpers
    # ==========================================================

    def _extract_query(self, state: dict) -> str:
        """
        Extract the user request from workflow state.
        """

        return state.get("user_request", "")

    # ----------------------------------------------------------
    # Memory
    # ----------------------------------------------------------

    def _retrieve_memory(self, query: str) -> dict:

        return {
            "working": self._retrieve_working_memory(query),
            "semantic": self._retrieve_semantic_memory(query),
            "episodes": self._retrieve_episode_memory(query),
            "reflections": self._retrieve_reflection_memory(query),
        }

    def _retrieve_working_memory(self, query: str) -> dict:
        """
        Runtime working memory.

        Release 0.1 keeps this inside the workflow state.
        """

        return {
            "query": query,
            "context": [],
        }

    def _retrieve_semantic_memory(self, query: str):

        # Reserved for Knowledge Layer (Release 0.2)

        return []

    def _retrieve_episode_memory(self, query: str):

        if self.memory_manager is None:
            return []

        try:
            return self.memory_manager.latest_episodes(limit=5)

        except Exception:
            return []

    def _retrieve_reflection_memory(self, query: str):

        if self.memory_manager is None:
            return []

        try:
            return self.memory_manager.latest_reflections(limit=5)

        except Exception:
            return []

    # ----------------------------------------------------------
    # Future Retrieval Sources
    # ----------------------------------------------------------

    def _retrieve_mongodb(self, query: str):

        raise NotImplementedError

    def _retrieve_web(self, query: str):

        raise NotImplementedError

    def _retrieve_vector(self, query: str):

        raise NotImplementedError

    # ----------------------------------------------------------
    # Future Processing
    # ----------------------------------------------------------

    def _merge_evidence(self, *sources):

        raise NotImplementedError

    def _rank_evidence(self, evidence):

        raise NotImplementedError

