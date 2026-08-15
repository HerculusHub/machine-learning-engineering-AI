"""
Bootstrap tests.

Architecture v2.3 (Frozen MVP)
"""


from mobile_ai_system.application.bootstrap import (
    Bootstrap,
)

from mobile_ai_system.agents.impact.impact_agent import (
    ImpactAgent,
)

from mobile_ai_system.impact.engines.causal_engine import (
    CausalEngine,
)
from mobile_ai_system.impact.engines.churn_engine import (
    ChurnEngine,
)
from mobile_ai_system.impact.engines.financial_engine import (
    FinancialEngine,
)
from mobile_ai_system.impact.engines.sensitivity_engine import (
    SensitivityEngine,
)
from mobile_ai_system.impact.services.impact_service import (
    ImpactService,
)
from mobile_ai_system.agents.report_agent import (
    ReportAgent,
)
from mobile_ai_system.agents.evaluation_agent import (
    EvaluationAgent,
)


def test_bootstrap_builds_container():
    """
    Bootstrap should build the application container.
    """

    bootstrap = Bootstrap()

    container = bootstrap.build()

    assert container is not None


def test_bootstrap_registers_core_services():
    """
    Bootstrap should register the core MVP services.
    """

    container = Bootstrap().build()

    assert container.contains(
        "settings"
    )

    assert container.contains(
        "mongo_config"
    )

    assert container.contains(
        "mongo_manager"
    )

    assert container.contains(
        "information_repository"
    )

    assert container.contains(
        "information_service"
    )

    assert container.contains(
        "information_agent"
    )

    assert container.contains(
        "supervisor_agent"
    )

    assert container.contains(
        "request_parser"
    )

    assert container.contains(
        "runner"
    )


def test_bootstrap_registers_impact_service():
    """
    Bootstrap should register the new ImpactService.
    """

    container = Bootstrap().build()

    assert container.contains(
        "impact_service"
    )

    service = container.resolve(
        "impact_service"
    )

    assert isinstance(
        service,
        ImpactService,
    )


def test_bootstrap_registers_churn_engine():
    """
    Bootstrap should register ChurnEngine.
    """

    container = Bootstrap().build()

    assert container.contains(
        "churn_engine"
    )

    engine = container.resolve(
        "churn_engine"
    )

    assert isinstance(
        engine,
        ChurnEngine,
    )


def test_bootstrap_registers_sensitivity_engine():
    """
    Bootstrap should register SensitivityEngine.
    """

    container = Bootstrap().build()

    assert container.contains(
        "sensitivity_engine"
    )

    engine = container.resolve(
        "sensitivity_engine"
    )

    assert isinstance(
        engine,
        SensitivityEngine,
    )


def test_bootstrap_registers_causal_engine():
    """
    Bootstrap should register CausalEngine.
    """

    container = Bootstrap().build()

    assert container.contains(
        "causal_engine"
    )

    engine = container.resolve(
        "causal_engine"
    )

    assert isinstance(
        engine,
        CausalEngine,
    )


def test_bootstrap_registers_financial_engine():
    """
    Bootstrap should register FinancialEngine.
    """

    container = Bootstrap().build()

    assert container.contains(
        "financial_engine"
    )

    engine = container.resolve(
        "financial_engine"
    )

    assert isinstance(
        engine,
        FinancialEngine,
    )


def test_bootstrap_impact_service_uses_registered_engines():
    """
    ImpactService should be wired to the same engine
    instances registered in the container.
    """

    container = Bootstrap().build()

    service = container.resolve(
        "impact_service"
    )

    assert service.churn_engine is container.resolve(
        "churn_engine"
    )

    assert service.sensitivity_engine is container.resolve(
        "sensitivity_engine"
    )

    assert service.causal_engine is container.resolve(
        "causal_engine"
    )

    assert service.financial_engine is container.resolve(
        "financial_engine"
    )

def test_bootstrap_registers_impact_agent():
    container = Bootstrap().build()

    assert container.contains(
        "impact_agent"
    )

    impact_agent = container.resolve(
        "impact_agent"
    )

    assert isinstance(
        impact_agent,
        ImpactAgent,
    )


def test_runner_registers_impact_handler():
    container = Bootstrap().build()

    runner = container.resolve(
        "runner"
    )

    assert runner.has_handler(
        "impact"
    )

def test_bootstrap_registers_report_agent():
    container = Bootstrap().build()

    assert container.contains(
        "report_agent"
    )

    report_agent = container.resolve(
        "report_agent"
    )

    assert isinstance(
        report_agent,
        ReportAgent,
    )


def test_runner_registers_report_handler():
    container = Bootstrap().build()

    runner = container.resolve(
        "runner"
    )

    assert runner.has_handler(
        "report"
    )



def test_bootstrap_registers_evaluation_agent():
    container = Bootstrap().build()

    assert container.contains(
        "evaluation_agent"
    )

    evaluation_agent = container.resolve(
        "evaluation_agent"
    )

    assert isinstance(
        evaluation_agent,
        EvaluationAgent,
    )


def test_runner_registers_evaluation_handler():
    container = Bootstrap().build()

    runner = container.resolve(
        "runner"
    )

    assert runner.has_handler(
        "evaluation"
    )