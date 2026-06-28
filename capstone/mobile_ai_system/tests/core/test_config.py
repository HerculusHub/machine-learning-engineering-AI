import os

from mobile_ai_system.core.config import get_settings


def test_settings():

    os.environ["GOOGLE_API_KEY"] = "dummy"

    os.environ["MONGO_URI"] = "mongodb://localhost"

    os.environ["POSTGRES_HOST"] = "localhost"

    os.environ["POSTGRES_DB"] = "db"

    os.environ["POSTGRES_USER"] = "postgres"

    os.environ["POSTGRES_PASSWORD"] = "password"

    settings = get_settings()

    assert settings.model_name == "gemini-2.5-pro"