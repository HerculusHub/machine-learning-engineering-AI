from mobile_ai_system.infrastructure.persistence.postgresql.repositories.reflection_repository import (
    ReflectionRepository,
)
from mobile_ai_system.infrastructure.persistence.postgresql.schema import (
    SchemaManager,
)


def test_save_reflection():

    SchemaManager().initialize()

    repo = ReflectionRepository()

    repo.clear()

    reflection_id = repo.save(

        lesson="Always verify retrieved evidence.",

        source="EvaluationAgent",

        score=0.92,

        metadata={

            "iteration": 1

        },

    )

    row = repo.get(reflection_id)

    assert row is not None

    assert row["lesson"] == "Always verify retrieved evidence."

    assert repo.count() == 1