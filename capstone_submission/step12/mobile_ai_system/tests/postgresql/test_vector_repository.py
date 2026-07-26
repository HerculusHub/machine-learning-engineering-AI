import pytest

from mobile_ai_system.infrastructure.persistence.postgresql.repository_provider import (
    RepositoryProvider,
)


def test_vector_repository_placeholder():

    provider = RepositoryProvider()

    assert provider.vectors is not None

    with pytest.raises(NotImplementedError):
        provider.vectors.save_embedding()