from mobile_ai_system.memory.semantic_memory import SemanticMemory


def test_add():

    memory = SemanticMemory()

    memory.add(
        "company",
        "Verizon"
    )

    assert memory.count() == 1


def test_get():

    memory = SemanticMemory()

    memory.add(
        "technology",
        "5G"
    )

    assert memory.get(
        "technology"
    )[0] == "5G"


def test_categories():

    memory = SemanticMemory()

    memory.add(
        "company",
        "AT&T"
    )

    memory.add(
        "technology",
        "Open RAN"
    )

    cats = memory.categories()

    assert "company" in cats

    assert "technology" in cats


def test_clear():

    memory = SemanticMemory()

    memory.add(
        "company",
        "Verizon"
    )

    memory.clear()

    assert memory.count() == 0