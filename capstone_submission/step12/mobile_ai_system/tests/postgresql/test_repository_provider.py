from mobile_ai_system.infrastructure.persistence.postgresql.repository_provider import (
    RepositoryProvider,
)

from mobile_ai_system.infrastructure.persistence.postgresql.repositories.episode_repository import (
    EpisodeRepository,
)

from mobile_ai_system.infrastructure.persistence.postgresql.repositories.reflection_repository import (
    ReflectionRepository,
)

from mobile_ai_system.infrastructure.persistence.postgresql.repositories.vector_repository import (
    VectorRepository,
)


def test_provider():

    provider = RepositoryProvider()

    assert isinstance(provider.episodes, EpisodeRepository)

    assert isinstance(provider.reflections, ReflectionRepository)

    assert isinstance(provider.vectors, VectorRepository)

    assert provider.semantic is None

    assert provider.execution is None