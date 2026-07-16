"""
Application service registry.
"""

from __future__ import annotations

from mobile_ai_system.core.config import get_settings
from mobile_ai_system.core.container import ServiceContainer
from mobile_ai_system.infrastructure.logging import get_logger


def register_services(
    container: ServiceContainer,
) -> None:
    """
    Register shared application services.
    """

    settings = get_settings()

    container.register_instance(
        "settings",
        settings,
    )

    # Create the shared application logger
    logger = get_logger("mobile_ai_system")

    container.register_instance(
        "logger",
        logger,
    )