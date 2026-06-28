from mobile_ai_system.core.container import ServiceContainer


def test_register_instance():

    c = ServiceContainer()

    c.register_instance(
        "number",
        10
    )

    assert c.resolve("number") == 10


def test_factory():

    c = ServiceContainer()

    c.register_factory(
        "value",
        lambda: 100
    )

    assert c.resolve("value") == 100


def test_contains():

    c = ServiceContainer()

    c.register_instance(
        "x",
        1
    )

    assert c.contains("x")