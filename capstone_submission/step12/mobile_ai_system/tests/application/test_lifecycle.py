from mobile_ai_system.application.lifecycle import (
    ApplicationLifecycle,
)


def test_initialize():

    app = ApplicationLifecycle()

    app.initialize()

    assert app.container is not None


def test_health():

    app = ApplicationLifecycle()

    app.initialize()

    health = app.health_check()

    assert health["status"] == "healthy"


def test_shutdown():

    app = ApplicationLifecycle()

    app.initialize()

    app.shutdown()

    assert app.container is None