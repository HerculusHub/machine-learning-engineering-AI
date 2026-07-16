"""
Base Tool

Architecture v2.3 (Frozen)

Defines the common interface for every tool.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseTool(ABC):

    NAME = "base"

    @property
    def name(self) -> str:
        return self.NAME

    @abstractmethod
    def connect(self) -> None:
        ...

    @abstractmethod
    def health_check(self) -> bool:
        ...

    @abstractmethod
    def execute(self, *args, **kwargs):
        ...