from mobile_ai_system.memory.working_memory import WorkingMemory


def test_set_and_get():

    memory = WorkingMemory()

    memory.set(
        "score",
        95
    )

    assert memory.get(
        "score"
    ) == 95


def test_append():

    memory = WorkingMemory()

    memory.append(
        "messages",
        "hello"
    )

    memory.append(
        "messages",
        "world"
    )

    assert len(
        memory.get("messages")
    ) == 2


def test_clear():

    memory = WorkingMemory()

    memory.set(
        "abc",
        123
    )

    memory.clear()

    assert memory.get("abc") is None


def test_artifact():

    memory = WorkingMemory()

    memory.update_artifact(
        "report",
        "report.md"
    )

    assert memory.get_artifact("report") == "report.md"