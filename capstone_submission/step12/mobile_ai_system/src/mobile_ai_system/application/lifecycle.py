"""
Application lifecycle management.
"""

from __future__ import annotations

from mobile_ai_system.core.container import ServiceContainer

from .bootstrap import bootstrap_application


class ApplicationLifecycle:
    """
    Manage application startup and shutdown.
    """

    def __init__(self):

        self.container: ServiceContainer | None = None

    # ------------------------------------

    def initialize(self) -> None:
        """
        Start the application.
        """

        self.container = bootstrap_application()

    # ------------------------------------

    def health_check(self) -> dict:
        """
        Return basic application status.
        """

        return {
            "status": "healthy",
            "initialized": self.container is not None,
        }

    # ------------------------------------

    def shutdown(self) -> None:
        """
        Shut down application.
        """

        self.container = None