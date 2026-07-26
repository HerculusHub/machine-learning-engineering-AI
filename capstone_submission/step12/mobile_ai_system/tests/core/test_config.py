"""
Tests for application configuration.

Architecture v2.3 (Frozen)
"""

from mobile_ai_system.core.config import get_settings


def test_settings(monkeypatch):
    """
    Verify that Settings loads correctly and exposes
    the expected configuration values.

    This test temporarily overrides environment variables
    and restores them automatically after completion.
    """

    # ---------------------------------------------------------
    # Ensure a fresh Settings instance
    # ---------------------------------------------------------

    get_settings.cache_clear()

    # ---------------------------------------------------------
    # Required environment variables
    # ---------------------------------------------------------

    monkeypatch.setenv("GOOGLE_API_KEY", "dummy-google-key")
    monkeypatch.setenv("GROQ_API_KEY", "dummy-groq-key")
    monkeypatch.setenv("MONGO_URI", "mongodb://localhost")

    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_DATABASE", "mobile_ai_system")
    monkeypatch.setenv("POSTGRES_USER", "postgres")
    monkeypatch.setenv("POSTGRES_PASSWORD", "password")

    settings = get_settings()

    # ---------------------------------------------------------
    # API Keys
    # ---------------------------------------------------------

    assert settings.google_api_key == "dummy-google-key"
    assert settings.groq_api_key == "dummy-groq-key"

    # ---------------------------------------------------------
    # Default Provider
    # ---------------------------------------------------------

    assert settings.default_llm_provider == "google"

    # ---------------------------------------------------------
    # Agent Provider Mapping
    # ---------------------------------------------------------

    assert settings.information_agent_provider == "google"
    assert settings.impact_agent_provider == "google"
    assert settings.report_agent_provider == "google"
    assert settings.evaluation_agent_provider == "groq"
    assert settings.supervisor_agent_provider == "google"

    # ---------------------------------------------------------
    # Agent Model Mapping
    # ---------------------------------------------------------

    assert settings.information_agent_model == "gemini-2.5-flash"
    assert settings.impact_agent_model == "gemini-2.5-flash"
    assert settings.report_agent_model == "gemini-2.5-flash"
    assert settings.evaluation_agent_model == "llama-3.1-8b-instant"
    assert settings.supervisor_agent_model == "gemini-2.5-flash"

    # ---------------------------------------------------------
    # Backward Compatibility
    # ---------------------------------------------------------

    assert settings.model_name == "gemini-2.5-flash"
    assert settings.provider == "google"

    # ---------------------------------------------------------
    # MongoDB
    # ---------------------------------------------------------

    assert settings.mongo_uri == "mongodb://localhost"
    assert settings.mongo_database == "industry_db"

    # ---------------------------------------------------------
    # PostgreSQL
    # ---------------------------------------------------------

    assert settings.postgres_host == "localhost"
    assert settings.postgres_database == "mobile_ai_system"
    assert settings.postgres_user == "postgres"
    assert settings.postgres_password == "password"

    # ---------------------------------------------------------
    # Logging
    # ---------------------------------------------------------

    assert settings.log_level == "INFO"

    # ---------------------------------------------------------
    # Important:
    # Clear cached Settings so later tests reload the
    # real .env configuration.
    # ---------------------------------------------------------

    get_settings.cache_clear()