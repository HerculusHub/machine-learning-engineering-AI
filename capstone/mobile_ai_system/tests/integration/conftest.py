import pytest

from mobile_ai_system.application.bootstrap import Bootstrap


@pytest.fixture(scope="session")
def container():
    """
    Build the application container once for all
    integration tests.
    """
    bootstrap = Bootstrap()
    return bootstrap.build()