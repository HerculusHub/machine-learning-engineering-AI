"""
Information Service

Architecture v2.3 (Frozen MVP)
"""

from __future__ import annotations

from mobile_ai_system.application.interfaces.i_information_repository import (
    IInformationRepository,
)
from mobile_ai_system.application.models.information_result import (
    InformationResult,
)
from mobile_ai_system.application.models.request_model import (
    Request,
)


class InformationService:
    """
    Application service for information retrieval.
    """

    def __init__(
        self,
        repository: IInformationRepository,
    ) -> None:

        self._repository = repository

    def search(
        self,
        request: Request,
    ) -> InformationResult:

        return self._repository.search(request)

    def find_by_event_id(
        self,
        event_id: str,
    ):

        return self._repository.find_by_event_id(event_id)

    def find_by_operator(
        self,
        operator: str,
    ):

        return self._repository.find_by_operator(operator)

    def find_recent(
        self,
        days: int = 30,
    ):

        return self._repository.find_recent(
        days=days,
    )

    def count(self) -> int:

        return self._repository.count()