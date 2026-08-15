"""
Analytics Dependency-Injection Wiring Tests

Architecture v2.3 (Frozen MVP)

Step 11D
--------

Purpose
-------
Verify that Bootstrap correctly composes and registers the
runtime analytics service/tool dependency graph.

These tests verify composition only.

They do NOT test:

- churn model behavior
- sensitivity calculations
- telecom scenario calculations
- financial calculations

Those capabilities are already tested independently in the
service and tool suites.
"""

from __future__ import annotations

from mobile_ai_system.application.bootstrap import (
    Bootstrap,
)

from mobile_ai_system.application.registry import (
    CHURN_PREDICTION_SERVICE,
    CHURN_PREDICTION_TOOL,
    CHURN_SENSITIVITY_SERVICE,
    CHURN_SENSITIVITY_TOOL,
    FINANCIAL_IMPACT_SERVICE,
    FINANCIAL_IMPACT_TOOL,
    TELECOM_SCENARIO_SERVICE,
    TELECOM_SCENARIO_TOOL,
)

from mobile_ai_system.services.analytics import (
    ChurnPredictionService,
    ChurnSensitivityService,
    FinancialImpactService,
    TelecomScenarioService,
)

from mobile_ai_system.tools.analytics import (
    ChurnPredictionTool,
    ChurnSensitivityTool,
    FinancialImpactTool,
    TelecomScenarioTool,
)


# =============================================================
# Helpers
# =============================================================


def build_container():
    """
    Build a fresh application container.
    """

    return Bootstrap().build()


# =============================================================
# Analytics services
# =============================================================


def test_bootstrap_registers_churn_prediction_service():
    """
    Bootstrap should register ChurnPredictionService.
    """

    container = build_container()

    service = container.resolve(
        CHURN_PREDICTION_SERVICE
    )

    assert isinstance(
        service,
        ChurnPredictionService,
    )


def test_bootstrap_registers_churn_sensitivity_service():
    """
    Bootstrap should register ChurnSensitivityService.
    """

    container = build_container()

    service = container.resolve(
        CHURN_SENSITIVITY_SERVICE
    )

    assert isinstance(
        service,
        ChurnSensitivityService,
    )


def test_bootstrap_registers_telecom_scenario_service():
    """
    Bootstrap should register TelecomScenarioService.
    """

    container = build_container()

    service = container.resolve(
        TELECOM_SCENARIO_SERVICE
    )

    assert isinstance(
        service,
        TelecomScenarioService,
    )


def test_bootstrap_registers_financial_impact_service():
    """
    Bootstrap should register FinancialImpactService.
    """

    container = build_container()

    service = container.resolve(
        FINANCIAL_IMPACT_SERVICE
    )

    assert isinstance(
        service,
        FinancialImpactService,
    )


# =============================================================
# Analytics tools
# =============================================================


def test_bootstrap_registers_churn_prediction_tool():
    """
    Bootstrap should register ChurnPredictionTool.
    """

    container = build_container()

    tool = container.resolve(
        CHURN_PREDICTION_TOOL
    )

    assert isinstance(
        tool,
        ChurnPredictionTool,
    )


def test_bootstrap_registers_churn_sensitivity_tool():
    """
    Bootstrap should register ChurnSensitivityTool.
    """

    container = build_container()

    tool = container.resolve(
        CHURN_SENSITIVITY_TOOL
    )

    assert isinstance(
        tool,
        ChurnSensitivityTool,
    )


def test_bootstrap_registers_telecom_scenario_tool():
    """
    Bootstrap should register TelecomScenarioTool.
    """

    container = build_container()

    tool = container.resolve(
        TELECOM_SCENARIO_TOOL
    )

    assert isinstance(
        tool,
        TelecomScenarioTool,
    )


def test_bootstrap_registers_financial_impact_tool():
    """
    Bootstrap should register FinancialImpactTool.
    """

    container = build_container()

    tool = container.resolve(
        FINANCIAL_IMPACT_TOOL
    )

    assert isinstance(
        tool,
        FinancialImpactTool,
    )


# =============================================================
# Service identity
# =============================================================


def test_churn_prediction_tool_uses_registered_service():
    """
    ChurnPredictionTool must use the exact
    ChurnPredictionService instance registered in DI.
    """

    container = build_container()

    service = container.resolve(
        CHURN_PREDICTION_SERVICE
    )

    tool = container.resolve(
        CHURN_PREDICTION_TOOL
    )

    assert (
        tool.service
        is
        service
    )


def test_churn_sensitivity_tool_uses_registered_service():
    """
    ChurnSensitivityTool must use the exact
    ChurnSensitivityService instance registered in DI.
    """

    container = build_container()

    service = container.resolve(
        CHURN_SENSITIVITY_SERVICE
    )

    tool = container.resolve(
        CHURN_SENSITIVITY_TOOL
    )

    assert (
        tool.service
        is
        service
    )


def test_telecom_scenario_tool_uses_registered_service():
    """
    TelecomScenarioTool must use the exact
    TelecomScenarioService instance registered in DI.
    """

    container = build_container()

    service = container.resolve(
        TELECOM_SCENARIO_SERVICE
    )

    tool = container.resolve(
        TELECOM_SCENARIO_TOOL
    )

    assert (
        tool.service
        is
        service
    )


def test_financial_impact_tool_uses_registered_service():
    """
    FinancialImpactTool must use the exact
    FinancialImpactService instance registered in DI.
    """

    container = build_container()

    service = container.resolve(
        FINANCIAL_IMPACT_SERVICE
    )

    tool = container.resolve(
        FINANCIAL_IMPACT_TOOL
    )

    assert (
        tool.service
        is
        service
    )


# =============================================================
# Cross-service dependency identity
# =============================================================


def test_telecom_scenario_service_uses_registered_sensitivity_service():
    """
    TelecomScenarioService must use the exact
    ChurnSensitivityService instance registered in DI.

    Dependency identity:

        container[
            CHURN_SENSITIVITY_SERVICE
        ]

                is

        TelecomScenarioService
            ._sensitivity_service
    """

    container = build_container()

    sensitivity_service = (
        container.resolve(
            CHURN_SENSITIVITY_SERVICE
        )
    )

    scenario_service = (
        container.resolve(
            TELECOM_SCENARIO_SERVICE
        )
    )

    assert (
        scenario_service
        ._sensitivity_service
        is
        sensitivity_service
    )


# =============================================================
# Singleton identity
# =============================================================


def test_analytics_service_resolution_is_stable():
    """
    Container resolution should return the registered
    singleton analytics service instance.
    """

    container = build_container()

    first = container.resolve(
        CHURN_PREDICTION_SERVICE
    )

    second = container.resolve(
        CHURN_PREDICTION_SERVICE
    )

    assert first is second


def test_analytics_tool_resolution_is_stable():
    """
    Container resolution should return the registered
    singleton analytics tool instance.
    """

    container = build_container()

    first = container.resolve(
        CHURN_PREDICTION_TOOL
    )

    second = container.resolve(
        CHURN_PREDICTION_TOOL
    )

    assert first is second


# =============================================================
# Registry-key separation
# =============================================================


def test_analytics_service_keys_are_distinct():
    """
    Each analytics service must have a unique DI key.
    """

    keys = {
        CHURN_PREDICTION_SERVICE,
        CHURN_SENSITIVITY_SERVICE,
        TELECOM_SCENARIO_SERVICE,
        FINANCIAL_IMPACT_SERVICE,
    }

    assert len(
        keys
    ) == 4


def test_analytics_tool_keys_are_distinct():
    """
    Each analytics tool must have a unique DI key.
    """

    keys = {
        CHURN_PREDICTION_TOOL,
        CHURN_SENSITIVITY_TOOL,
        TELECOM_SCENARIO_TOOL,
        FINANCIAL_IMPACT_TOOL,
    }

    assert len(
        keys
    ) == 4


def test_service_and_tool_keys_do_not_overlap():
    """
    Service keys and tool keys must occupy distinct DI
    namespaces.
    """

    service_keys = {
        CHURN_PREDICTION_SERVICE,
        CHURN_SENSITIVITY_SERVICE,
        TELECOM_SCENARIO_SERVICE,
        FINANCIAL_IMPACT_SERVICE,
    }

    tool_keys = {
        CHURN_PREDICTION_TOOL,
        CHURN_SENSITIVITY_TOOL,
        TELECOM_SCENARIO_TOOL,
        FINANCIAL_IMPACT_TOOL,
    }

    assert (
        service_keys
        .isdisjoint(
            tool_keys
        )
    )