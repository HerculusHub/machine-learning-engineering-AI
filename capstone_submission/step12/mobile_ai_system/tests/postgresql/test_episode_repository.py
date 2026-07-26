from mobile_ai_system.infrastructure.persistence.postgresql.repositories.episode_repository import (
    EpisodeRepository,
)
from mobile_ai_system.infrastructure.persistence.postgresql.schema import (
    SchemaManager,
)


def test_save_episode():

    SchemaManager().initialize()

    repo = EpisodeRepository()

    repo.clear()

    episode_id = repo.save(

        user_request="Analyze Verizon",

        workflow_state={

            "score": 91

        },

        evaluation_score=0.95,

    )

    assert episode_id is not None

    assert repo.count() == 1