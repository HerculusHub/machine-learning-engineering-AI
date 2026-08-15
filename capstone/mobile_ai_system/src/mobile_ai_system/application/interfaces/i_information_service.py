from abc import ABC
from abc import abstractmethod

from mobile_ai_system.application.models.request_model import Request
from mobile_ai_system.application.models.information_result import (
    InformationResult,
)


class IInformationService(ABC):

    @abstractmethod
    def retrieve(
        self,
        request: Request,
    ) -> InformationResult:
        pass