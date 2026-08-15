"""
Application Service Registry

Architecture v2.3 (Frozen MVP)

Purpose
-------
Provide stable dependency-injection registry keys and register
lightweight shared application-level services.

Responsibilities
----------------
This module owns:

- stable DI registry keys
- shared application-level service registration
- settings registration
- logger registration

Infrastructure-, analytics-, agent-, and domain-specific object
composition belongs to Bootstrap or dedicated composition modules.

Architecture Rule
-----------------
This module must remain lightweight.

It must NOT:

- load ML model artifacts
- instantiate analytics services
- instantiate analytics tools
- instantiate agents
- perform infrastructure initialization
- contain business logic
"""

from __future__ import annotations

from mobile_ai_system.core.config import (
    get_settings,
)
from mobile_ai_system.core.container import (
    Container,
)
from mobile_ai_system.infrastructure.logging import (
    get_logger,
)


# =============================================================
# Core application keys
# =============================================================

SETTINGS = "settings"

LOGGER = "logger"


# =============================================================
# Analytics service keys
# =============================================================

CHURN_PREDICTION_SERVICE = (
    "analytics.churn_prediction_service"
)

CHURN_SENSITIVITY_SERVICE = (
    "analytics.churn_sensitivity_service"
)

TELECOM_SCENARIO_SERVICE = (
    "analytics.telecom_scenario_service"
)

FINANCIAL_IMPACT_SERVICE = (
    "analytics.financial_impact_service"
)


# =============================================================
# Analytics tool keys
# =============================================================

CHURN_PREDICTION_TOOL = (
    "analytics.churn_prediction_tool"
)

CHURN_SENSITIVITY_TOOL = (
    "analytics.churn_sensitivity_tool"
)

TELECOM_SCENARIO_TOOL = (
    "analytics.telecom_scenario_tool"
)

FINANCIAL_IMPACT_TOOL = (
    "analytics.financial_impact_tool"
)


# =============================================================
# Analysis Agent key
# =============================================================

ANALYSIS_AGENT = "agents.analysis"


# =============================================================
# Public key groups
# =============================================================

ANALYTICS_SERVICE_KEYS = (
    CHURN_PREDICTION_SERVICE,
    CHURN_SENSITIVITY_SERVICE,
    TELECOM_SCENARIO_SERVICE,
    FINANCIAL_IMPACT_SERVICE,
)

ANALYTICS_TOOL_KEYS = (
    CHURN_PREDICTION_TOOL,
    CHURN_SENSITIVITY_TOOL,
    TELECOM_SCENARIO_TOOL,
    FINANCIAL_IMPACT_TOOL,
)

ANALYTICS_KEYS = (
    *ANALYTICS_SERVICE_KEYS,
    *ANALYTICS_TOOL_KEYS,
)


# =============================================================
# Shared service registration
# =============================================================

def register_services(
    container: Container,
) -> None:
    """
    Register lightweight shared application services.

    Parameters
    ----------
    container
        Application dependency-injection container.

    Notes
    -----
    Analytics services and analytics tools are intentionally
    not instantiated here.

    Their dependency graph is composed by the application
    Bootstrap layer.

    This preserves the Architecture v2.3 separation:

        Registry
            -> stable keys
            -> shared application services

        Bootstrap
            -> analytics service construction
            -> analytics tool construction
            -> agent construction
            -> dependency wiring
    """

    # ---------------------------------------------------------
    # Settings
    # ---------------------------------------------------------

    settings = get_settings()

    container.register_instance(
        SETTINGS,
        settings,
    )

    # ---------------------------------------------------------
    # Application logger
    # ---------------------------------------------------------

    logger = get_logger(
        "mobile_ai_system"
    )

    container.register_instance(
        LOGGER,
        logger,
    )


# =============================================================
# Public exports
# =============================================================

__all__ = [
    # Registration
    "register_services",

    # Core keys
    "SETTINGS",
    "LOGGER",

    # Analytics service keys
    "CHURN_PREDICTION_SERVICE",
    "CHURN_SENSITIVITY_SERVICE",
    "TELECOM_SCENARIO_SERVICE",
    "FINANCIAL_IMPACT_SERVICE",

    # Analytics tool keys
    "CHURN_PREDICTION_TOOL",
    "CHURN_SENSITIVITY_TOOL",
    "TELECOM_SCENARIO_TOOL",
    "FINANCIAL_IMPACT_TOOL",

    # Agent keys
    "ANALYSIS_AGENT",

    # Key groups
    "ANALYTICS_SERVICE_KEYS",
    "ANALYTICS_TOOL_KEYS",
    "ANALYTICS_KEYS",
]