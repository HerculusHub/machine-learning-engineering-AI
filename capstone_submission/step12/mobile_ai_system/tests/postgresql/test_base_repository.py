from mobile_ai_system.infrastructure.persistence.postgresql.repositories.base_repository import (
    BaseRepository,
)


def test_base_repository():

    repo = BaseRepository()

    assert repo is not None