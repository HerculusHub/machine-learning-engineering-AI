"""
Application service registry.
"""

from __future__ import annotations

import logging

from mobile_ai_system.core.config import get_settings
from mobile_ai_system.core.container import ServiceContainer


def register_services(
    container: ServiceContainer,
) -> None:
    """
    Register all shared application services.

    Parameters
    ----------
    container:
        Dependency injection container.
    """

    settings = get_settings()

    container.register_instance(
        "settings",
        settings,
    )

    logger = logging.getLogger(
        "mobile_ai_system"
    )

    container.register_instance(
        "logger",
        logger,
    )