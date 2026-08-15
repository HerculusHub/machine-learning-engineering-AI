"""
lobal configuration.

Architecture v2.3 (Frozen)

Responsibilities
----------------
- Load environment variables
- Provide application configuration
- Configure external services

Does NOT
---------
- Instantiate clients
- Perform dependency injection
"""

from functools import lru_cache

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):

    # ==========================================================
    # Google Gemini
    # ==========================================================

    google_api_key: str

    # ==========================================================
    # OpenAI
    # ==========================================================

    openai_api_key: str | None = None

    # ==========================================================
    # Groq
    # ==========================================================

    groq_api_key: str | None = None

    # ==========================================================
    # Anthropic
    # ==========================================================

    anthropic_api_key: str | None = None

    # ==========================================================
    # Default LLM Provider
    # ==========================================================

    default_llm_provider: str = "google"

    # ==========================================================
    # Agent → Provider Mapping
    # ==========================================================

    information_agent_provider: str = "google"
    impact_agent_provider: str = "google"
    report_agent_provider: str = "google"
    evaluation_agent_provider: str = "groq"
    supervisor_agent_provider: str = "google"

    # ==========================================================
    # Agent → Model Mapping
    # ==========================================================

    information_agent_model: str = "gemini-2.5-flash"
    impact_agent_model: str = "gemini-2.5-flash"
    report_agent_model: str = "gemini-2.5-flash"
    evaluation_agent_model: str = "llama-3.1-8b-instant"
    supervisor_agent_model: str = "gemini-2.5-flash"

   
    # ==========================================================
    # MongoDB
    # ==========================================================

    mongo_uri: str

    mongo_database: str = "industry_db"

    mongo_collection: str = "operator_events"

    business_data_path: str = "./data/business/customer_churn.csv"

    # ==========================================================
    # PostgreSQL
    # ==========================================================

    postgres_host: str = "localhost"

    postgres_port: int = 5432

    postgres_database: str = "mobile_ai_system"

    postgres_user: str = "postgres"

    postgres_password: str

    postgres_pool_size: int = 10

    postgres_connect_timeout: int = 10

    postgres_command_timeout: int = 30

    # ==========================================================
    # Vector Database
    # ==========================================================

    vector_db_path: str = "./data/vector_db"

    # ==========================================================
    # Logging
    # ==========================================================

    log_level: str = "INFO"

    # ==========================================================
    # Pydantic
    # ==========================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


    # ---------------------------------------------------------
    # Runtime analytics model artifacts
    # ---------------------------------------------------------

    churn_calibrated_model_path: str = (
        "data/synthetic/models/"
        "churn_calibrated_model.joblib"
    )

    churn_sensitivity_model_path: str = (
        "data/synthetic/models/"
        "churn_sensitivity_model.joblib"
    )


@lru_cache
def get_settings() -> Settings:
    """
    Lazily create and cache the Settings object.
    """
    return Settings()


# Backward compatibility
settings = get_settings()