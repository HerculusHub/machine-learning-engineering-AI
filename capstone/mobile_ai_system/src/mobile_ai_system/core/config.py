from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    google_api_key: str

    model_name: str = "gemini-2.5-pro"

    temperature: float = 0.2

    mongo_uri: str

    mongo_database: str = "industry_db"

    postgres_host: str

    postgres_port: int = 5432

    postgres_db: str

    postgres_user: str

    postgres_password: str

    vector_db_path: str = "./data/vector_db"

    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    """
    Lazily create and cache the Settings object.
    """
    return Settings()