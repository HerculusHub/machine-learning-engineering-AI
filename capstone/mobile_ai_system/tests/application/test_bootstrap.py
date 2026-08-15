"""
Application Bootstrap Tests

Architecture v2.3 (Frozen MVP)
"""

from __future__ import annotations

from mobile_ai_system.application.bootstrap import (
    Bootstrap,
)
from mobile_ai_system.core.container import (
    Container,
)


def test_bootstrap_returns_container():
    """
    Bootstrap.build() should return the application
    dependency container.
    """

    container = Bootstrap().build()

    assert isinstance(
        container,
        Container,
    )


def test_bootstrap_registers_settings():
    """
    Bootstrap should register application settings.
    """

    container = Bootstrap().build()

    assert container.contains(
        "settings"
    )

    assert container.resolve(
        "settings"
    ) is not None


def test_bootstrap_registers_runner():
    """
    Bootstrap should register ApplicationRunner.
    """

    container = Bootstrap().build()

    assert container.contains(
        "runner"
    )


def test_bootstrap_registers_application_agents():
    """
    Bootstrap should register the Frozen MVP
    pipeline agents.
    """

    container = Bootstrap().build()

    assert container.contains(
        "information_agent"
    )

    assert container.contains(
        "impact_agent"
    )

    assert container.contains(
        "report_agent"
    )

    assert container.contains(
        "evaluation_agent"
    )


def test_bootstrap_runner_has_mvp_handlers():
    """
    ApplicationRunner should contain every canonical
    Frozen MVP pipeline stage.
    """

    container = Bootstrap().build()

    runner = container.resolve(
        "runner"
    )

    assert runner.has_handler(
        "information"
    )

    assert runner.has_handler(
        "impact"
    )

    assert runner.has_handler(
        "report"
    )

    assert runner.has_handler(
        "evaluation"
    )