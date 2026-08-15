"""
Base Agent

Architecture v2.3 (Frozen MVP)
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from mobile_ai_system.application.models.pipeline_context import (
    PipelineContext,
)


class BaseAgent(ABC):
    """
    Base class for every execution agent.

    Every agent receives the PipelineContext,
    updates it,
    and returns it.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable agent name."""

    @abstractmethod
    def execute(
        self,
        context: PipelineContext,
    ) -> PipelineContext:
        """
        Execute one pipeline stage.
        """
        raise NotImplementedError