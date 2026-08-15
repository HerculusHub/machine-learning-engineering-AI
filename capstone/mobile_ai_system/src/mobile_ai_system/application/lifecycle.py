"""
Application Lifecycle

Architecture v2.3 (Frozen MVP)

Manages application initialization,
health checks, and shutdown.
"""

from __future__ import annotations

from mobile_ai_system.application.bootstrap import (
    Bootstrap,
)
from mobile_ai_system.core.container import (
    Container,
)


class ApplicationLifecycle:
    """
    Manage application startup and shutdown.
    """

    def __init__(
        self,
    ) -> None:
        self.container: Container | None = None

    # ---------------------------------------------------------
    # Initialization
    # ---------------------------------------------------------

    def initialize(
        self,
    ) -> None:
        """
        Initialize the application dependency graph.
        """

        if self.container is not None:
            return

        self.container = Bootstrap().build()

    # ---------------------------------------------------------
    # Health
    # ---------------------------------------------------------

    def health_check(
        self,
    ) -> dict:
        """
        Return basic application lifecycle status.
        """

        initialized = (
            self.container is not None
        )

        return {
            "status": (
                "healthy"
                if initialized
                else "not_initialized"
            ),
            "initialized": initialized,
        }

    # ---------------------------------------------------------
    # Shutdown
    # ---------------------------------------------------------

    def shutdown(
        self,
    ) -> None:
        """
        Release the application container.
        """

        self.container = None