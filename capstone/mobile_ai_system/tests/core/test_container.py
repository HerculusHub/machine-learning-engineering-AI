"""
Tests for Container.
"""

from mobile_ai_system.core.container import Container


def test_register_factory():

    container = Container()

    container.register_factory(
        "number",
        lambda: 123,
    )

    assert container.resolve("number") == 123


def test_registered_services():

    container = Container()

    container.register_instance(
        "A",
        object(),
    )

    container.register_instance(
        "B",
        object(),
    )

    services = container.registered_services()

    assert "A" in services
    assert "B" in services