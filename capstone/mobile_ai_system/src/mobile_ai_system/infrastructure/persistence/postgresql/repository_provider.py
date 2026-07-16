from mobile_ai_system.infrastructure.persistence.postgresql.repositories.episode_repository import (
    EpisodeRepository,
)

from mobile_ai_system.infrastructure.persistence.postgresql.repositories.reflection_repository import (
    ReflectionRepository,
)

from mobile_ai_system.infrastructure.persistence.postgresql.repositories.vector_repository import (
    VectorRepository,
)


class RepositoryProvider:
    """
    Central access point for repositories.
    """

    def __init__(self):

        self.episodes = EpisodeRepository()
        self.reflections = ReflectionRepository()

        # Release 0.3 (now reserved)
        self.vectors = VectorRepository()

        # future stages
        self.semantic = None
        self.execution = None