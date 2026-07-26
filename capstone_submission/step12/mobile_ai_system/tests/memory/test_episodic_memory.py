from mobile_ai_system.memory.episodic_memory import EpisodicMemory



def test_save_episode():

    memory = EpisodicMemory()

    memory.clear()          # <-- important

    episode_id = memory.save_episode(
        user_request="Analyze Verizon",
        workflow_state={"score": 90},
    )

    assert episode_id is not None
    assert memory.count() == 1


def test_get_episode():

    memory = EpisodicMemory()

    episode_id = memory.save_episode(
        "test",
        {"a": 1},
    )

    episode = memory.get_episode(
        episode_id
    )

    assert episode["user_request"] == "test"


def test_latest():

    memory = EpisodicMemory()

    for i in range(10):

        memory.save_episode(
            str(i),
            {},
        )

    assert len(
        memory.latest(3)
    ) == 3


def test_clear():

    memory = EpisodicMemory()

    memory.save_episode(
        "abc",
        {},
    )

    memory.clear()

    assert memory.count() == 0