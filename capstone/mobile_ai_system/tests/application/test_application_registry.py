"""
Application Registry Tests

Architecture v2.3 (Frozen MVP)

Tests shared application-level service registration.
"""

from __future__ import annotations

from mobile_ai_system.application.registry import (
    register_services,
)
from mobile_ai_system.core.container import (
    Container,
)


def test_registry_registers_settings():
    """
    register_services() should register application settings.
    """

    container = Container()

    register_services(
        container,
    )

    assert container.contains(
        "settings"
    )

    assert container.resolve(
        "settings"
    ) is not None


def test_registry_registers_logger():
    """
    register_services() should register the shared logger.
    """

    container = Container()

    register_services(
        container,
    )

    assert container.contains(
        "logger"
    )

    assert container.resolve(
        "logger"
    ) is not None


def test_registry_registers_both_services():
    """
    Registry should register the complete shared
    application-service set.
    """

    container = Container()

    register_services(
        container,
    )

    assert container.contains(
        "settings"
    )

    assert container.contains(
        "logger"
    )