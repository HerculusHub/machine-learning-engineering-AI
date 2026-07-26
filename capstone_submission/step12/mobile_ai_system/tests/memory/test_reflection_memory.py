from mobile_ai_system.memory.reflection_memory import (
    ReflectionMemory,
)


def test_add():

    memory = ReflectionMemory()

    memory.add(
        "Compare competitors."
    )

    assert memory.count() == 1


def test_latest():

    memory = ReflectionMemory()

    for i in range(10):

        memory.add(
            f"Lesson {i}"
        )

    latest = memory.latest(3)

    assert len(latest) == 3

    assert latest[-1]["lesson"] == "Lesson 9"


def test_clear():

    memory = ReflectionMemory()

    memory.add("ABC")

    memory.clear()

    assert memory.count() == 0