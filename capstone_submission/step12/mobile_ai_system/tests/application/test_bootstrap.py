from mobile_ai_system.application.bootstrap import (
    bootstrap_application,
)


def test_bootstrap():

    container = bootstrap_application()

    assert container.contains(
        "settings"
    )

    assert container.contains(
        "logger"
    )