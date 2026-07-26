"""
Bootstrap the application.
"""

from __future__ import annotations

from mobile_ai_system.core.container import ServiceContainer

from .registry import register_services


def bootstrap_application() -> ServiceContainer:
    """
    Initialize the dependency container.

    Returns
    -------
    ServiceContainer
        Initialized container.
    """

    container = ServiceContainer()

    register_services(
        container
    )

    return container