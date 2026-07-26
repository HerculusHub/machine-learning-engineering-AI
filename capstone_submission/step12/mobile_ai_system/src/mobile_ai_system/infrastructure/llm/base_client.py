"""
Base LLM Client

Architecture v2.3 (Frozen)

Responsibilities
----------------
- Define the common interface for all LLM providers.
- Ensure every provider exposes the same API.

Does NOT
---------
- Contain SDK-specific code.
- Choose providers.
- Perform routing.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseClient(ABC):
    """
    Abstract base class for all LLM provider clients.
    """

    @abstractmethod
    def health_check(self) -> bool:
        """
        Return whether the client is available.
        """
        ...

    @abstractmethod
    def generate(
        self,
        *,
        model: str,
        prompt: str,
        temperature: float = 0.2,
    ) -> str:
        """
        Generate a completion from the specified model.
        """
        ...