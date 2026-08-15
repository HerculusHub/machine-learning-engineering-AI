"""
Tests for application configuration.

Architecture v2.3 (Frozen)

Step 11D
--------
Adds regression coverage for runtime analytics
model-artifact configuration.
"""

from __future__ import annotations

from mobile_ai_system.core.config import (
    Settings,
    get_settings,
)


def test_settings(monkeypatch):
    """
    Verify that Settings loads correctly and exposes
    the expected Architecture v2.3 configuration values.

    Environment variables are temporarily overridden
    and automatically restored by pytest.
    """

    # ---------------------------------------------------------
    # Fresh cached Settings instance
    # ---------------------------------------------------------

    get_settings.cache_clear()

    # ---------------------------------------------------------
    # Required environment variables
    # ---------------------------------------------------------

    monkeypatch.setenv(
        "GOOGLE_API_KEY",
        "dummy-google-key",
    )

    monkeypatch.setenv(
        "GROQ_API_KEY",
        "dummy-groq-key",
    )

    monkeypatch.setenv(
        "MONGO_URI",
        "mongodb://localhost",
    )

    monkeypatch.setenv(
        "POSTGRES_HOST",
        "localhost",
    )

    monkeypatch.setenv(
        "POSTGRES_DATABASE",
        "mobile_ai_system",
    )

    monkeypatch.setenv(
        "POSTGRES_USER",
        "postgres",
    )

    monkeypatch.setenv(
        "POSTGRES_PASSWORD",
        "password",
    )

    settings = get_settings()

    # ---------------------------------------------------------
    # Type
    # ---------------------------------------------------------

    assert isinstance(
        settings,
        Settings,
    )

    # ---------------------------------------------------------
    # API Keys
    # ---------------------------------------------------------

    assert settings.google_api_key == (
        "dummy-google-key"
    )

    assert settings.groq_api_key == (
        "dummy-groq-key"
    )

    assert settings.openai_api_key is None

    assert settings.anthropic_api_key is None

    # ---------------------------------------------------------
    # Default LLM Provider
    # ---------------------------------------------------------

    assert (
        settings.default_llm_provider
        ==
        "google"
    )

    # ---------------------------------------------------------
    # Agent Provider Mapping
    # ---------------------------------------------------------

    assert (
        settings.information_agent_provider
        ==
        "google"
    )

    assert (
        settings.impact_agent_provider
        ==
        "google"
    )

    assert (
        settings.report_agent_provider
        ==
        "google"
    )

    assert (
        settings.evaluation_agent_provider
        ==
        "groq"
    )

    assert (
        settings.supervisor_agent_provider
        ==
        "google"
    )

    # ---------------------------------------------------------
    # Agent Model Mapping
    # ---------------------------------------------------------

    assert settings.information_agent_model == (
        "gemini-2.5-flash"
    )

    assert settings.impact_agent_model == (
        "gemini-2.5-flash"
    )

    assert settings.report_agent_model == (
        "gemini-2.5-flash"
    )

    assert settings.evaluation_agent_model == (
        "llama-3.1-8b-instant"
    )

    assert settings.supervisor_agent_model == (
        "gemini-2.5-flash"
    )

    # ---------------------------------------------------------
    # MongoDB
    # ---------------------------------------------------------

    assert settings.mongo_uri == (
        "mongodb://localhost"
    )

    assert settings.mongo_database == (
        "industry_db"
    )

    assert settings.mongo_collection == (
        "operator_events"
    )

    # ---------------------------------------------------------
    # Business Data
    # ---------------------------------------------------------

    assert settings.business_data_path == (
        "./data/business/customer_churn.csv"
    )

    # ---------------------------------------------------------
    # Runtime Analytics Model Artifacts
    # ---------------------------------------------------------

    assert (
        settings.churn_calibrated_model_path
        ==
        (
            "data/synthetic/models/"
            "churn_calibrated_model.joblib"
        )
    )

    assert (
        settings.churn_sensitivity_model_path
        ==
        (
            "data/synthetic/models/"
            "churn_sensitivity_model.joblib"
        )
    )

    # ---------------------------------------------------------
    # PostgreSQL
    # ---------------------------------------------------------

    assert settings.postgres_host == (
        "localhost"
    )

    assert settings.postgres_port == 5432

    assert settings.postgres_database == (
        "mobile_ai_system"
    )

    assert settings.postgres_user == (
        "postgres"
    )

    assert settings.postgres_password == (
        "password"
    )

    assert settings.postgres_pool_size == 10

    assert (
        settings.postgres_connect_timeout
        ==
        10
    )

    assert (
        settings.postgres_command_timeout
        ==
        30
    )

    # ---------------------------------------------------------
    # Vector Database
    # ---------------------------------------------------------

    assert settings.vector_db_path == (
        "./data/vector_db"
    )

    # ---------------------------------------------------------
    # Logging
    # ---------------------------------------------------------

    assert settings.log_level == (
        "INFO"
    )

    # ---------------------------------------------------------
    # Cleanup
    # ---------------------------------------------------------

    get_settings.cache_clear()


def test_get_settings_is_cached(
    monkeypatch,
):
    """
    get_settings() should return the same cached
    Settings instance until the cache is cleared.
    """

    get_settings.cache_clear()

    monkeypatch.setenv(
        "GOOGLE_API_KEY",
        "dummy-google-key",
    )

    monkeypatch.setenv(
        "MONGO_URI",
        "mongodb://localhost",
    )

    monkeypatch.setenv(
        "POSTGRES_PASSWORD",
        "password",
    )

    first = get_settings()

    second = get_settings()

    assert first is second

    get_settings.cache_clear()


def test_agent_configuration_is_explicit(
    monkeypatch,
):
    """
    Architecture v2.3 uses explicit provider/model
    mappings for each agent rather than generic
    provider or model_name fields.
    """

    get_settings.cache_clear()

    monkeypatch.setenv(
        "GOOGLE_API_KEY",
        "dummy-google-key",
    )

    monkeypatch.setenv(
        "MONGO_URI",
        "mongodb://localhost",
    )

    monkeypatch.setenv(
        "POSTGRES_PASSWORD",
        "password",
    )

    settings = get_settings()

    assert hasattr(
        settings,
        "information_agent_provider",
    )

    assert hasattr(
        settings,
        "information_agent_model",
    )

    assert not hasattr(
        settings,
        "provider",
    )

    assert not hasattr(
        settings,
        "model_name",
    )

    get_settings.cache_clear()


def test_analytics_artifact_configuration(
    monkeypatch,
):
    """
    Step 11D runtime analytics artifact paths should be
    explicit application configuration.

    These settings belong to the runtime Configuration Layer,
    not scripts.synthetic_data.
    """

    # ---------------------------------------------------------
    # Fresh configuration
    # ---------------------------------------------------------

    get_settings.cache_clear()

    # ---------------------------------------------------------
    # Minimal required environment
    # ---------------------------------------------------------

    monkeypatch.setenv(
        "GOOGLE_API_KEY",
        "dummy-google-key",
    )

    monkeypatch.setenv(
        "MONGO_URI",
        "mongodb://localhost",
    )

    monkeypatch.setenv(
        "POSTGRES_PASSWORD",
        "password",
    )

    settings = get_settings()

    # ---------------------------------------------------------
    # Explicit configuration fields
    # ---------------------------------------------------------

    assert hasattr(
        settings,
        "churn_calibrated_model_path",
    )

    assert hasattr(
        settings,
        "churn_sensitivity_model_path",
    )

    # ---------------------------------------------------------
    # Non-empty values
    # ---------------------------------------------------------

    assert (
        settings.churn_calibrated_model_path
    )

    assert (
        settings.churn_sensitivity_model_path
    )

    # ---------------------------------------------------------
    # Expected artifact names
    # ---------------------------------------------------------

    assert (
        "churn_calibrated_model.joblib"
        in
        settings.churn_calibrated_model_path
    )

    assert (
        "churn_sensitivity_model.joblib"
        in
        settings.churn_sensitivity_model_path
    )

    # ---------------------------------------------------------
    # Runtime location
    # ---------------------------------------------------------

    assert (
        settings.churn_calibrated_model_path
        .startswith(
            "data/synthetic/models/"
        )
    )

    assert (
        settings.churn_sensitivity_model_path
        .startswith(
            "data/synthetic/models/"
        )
    )

    # ---------------------------------------------------------
    # Configuration separation
    # ---------------------------------------------------------
    #
    # The runtime application only sees artifact paths.
    #
    # It does not import scripts.synthetic_data.config.
    # ---------------------------------------------------------

    assert (
        "scripts.synthetic_data"
        not in
        settings.churn_calibrated_model_path
    )

    assert (
        "scripts.synthetic_data"
        not in
        settings.churn_sensitivity_model_path
    )

    # ---------------------------------------------------------
    # Cleanup
    # ---------------------------------------------------------

    get_settings.cache_clear()


def test_analytics_artifact_paths_can_be_overridden(
    monkeypatch,
):
    """
    Runtime analytics artifact paths should support normal
    Settings environment overrides.

    This preserves deployment flexibility while retaining
    stable project-relative defaults.
    """

    get_settings.cache_clear()

    # ---------------------------------------------------------
    # Required environment
    # ---------------------------------------------------------

    monkeypatch.setenv(
        "GOOGLE_API_KEY",
        "dummy-google-key",
    )

    monkeypatch.setenv(
        "MONGO_URI",
        "mongodb://localhost",
    )

    monkeypatch.setenv(
        "POSTGRES_PASSWORD",
        "password",
    )

    # ---------------------------------------------------------
    # Analytics overrides
    # ---------------------------------------------------------

    monkeypatch.setenv(
        "CHURN_CALIBRATED_MODEL_PATH",
        "runtime/models/calibrated.joblib",
    )

    monkeypatch.setenv(
        "CHURN_SENSITIVITY_MODEL_PATH",
        "runtime/models/sensitivity.joblib",
    )

    settings = get_settings()

    # ---------------------------------------------------------
    # Overrides should win
    # ---------------------------------------------------------

    assert (
        settings.churn_calibrated_model_path
        ==
        "runtime/models/calibrated.joblib"
    )

    assert (
        settings.churn_sensitivity_model_path
        ==
        "runtime/models/sensitivity.joblib"
    )

    # ---------------------------------------------------------
    # Cleanup
    # ---------------------------------------------------------

    get_settings.cache_clear()