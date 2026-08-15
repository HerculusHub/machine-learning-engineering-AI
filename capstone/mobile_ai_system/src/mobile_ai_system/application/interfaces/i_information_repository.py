"""
Information Repository Interface

Architecture v2.3 (Frozen MVP)

Defines the persistence contract used by the
InformationService.

Infrastructure implementations (MongoDB, PostgreSQL,
etc.) must implement this interface.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from mobile_ai_system.application.models.information_result import (
    InformationResult,
)
from mobile_ai_system.application.models.request_model import (
    Request,
)


class IInformationRepository(ABC):
    """
    Repository abstraction for retrieving
    industry information.
    """

    @abstractmethod
    def search(
        self,
        request: Request,
    ) -> InformationResult:
        """
        Execute a search using the supplied request.
        """
        raise NotImplementedError

    @abstractmethod
    def find_by_event_id(
        self,
        event_id: str,
    ) -> dict | None:
        """
        Retrieve one event by its unique event ID.
        """
        raise NotImplementedError

    @abstractmethod
    def find_by_operator(
        self,
        operator: str,
        limit: int = 20,
    ) -> list[dict]:
        """
        Retrieve recent events for one operator.
        """
        raise NotImplementedError

    @abstractmethod
    def find_recent(
        self,
        days: int = 30,
        limit: int = 20,
    ) -> list[dict]:
        """
        Retrieve recent industry events.
        """
        raise NotImplementedError

    @abstractmethod
    def count(self) -> int:
        """
        Return the total number of stored events.
        """
        raise NotImplementedError