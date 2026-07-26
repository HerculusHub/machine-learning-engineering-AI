from mobile_ai_system.application.registry import (
    register_services,
)

from mobile_ai_system.core.container import (
    ServiceContainer,
)


def test_registry():

    container = ServiceContainer()

    register_services(
        container
    )

    assert container.contains(
        "settings"
    )

    assert container.contains(
        "logger"
    )