"""
Application Bootstrap

Architecture v2.3 (Frozen MVP)

Responsibilities
----------------
Construct and wire the singleton components required
by the Mobile AI System MVP.

Bootstrap performs dependency composition only.

Business logic belongs in services, agents, engines,
repositories, and other dedicated components.

Step 11D
--------
Runtime analytics capabilities are composed here:

    ChurnPredictionService
        ↓
    ChurnPredictionTool

    ChurnSensitivityService
        ↓
    ChurnSensitivityTool
        ↓
    TelecomScenarioService
        ↓
    TelecomScenarioTool

    FinancialImpactService
        ↓
    FinancialImpactTool

The analytics services and tools are registered in the
existing dependency container.

Important analytics boundary
----------------------------
The Step 11 analytics services remain separate from the
frozen event-level Impact Layer for Release 0.1.

In particular:

    ChurnPredictionService

expects the customer-level engineered feature schema,

while:

    FeatureBuilder -> ChurnEngine

operates on event-level InformationResult features.

Therefore ChurnPredictionService is NOT injected into the
event-level ChurnEngine.

Step 12D
--------
The evaluation pipeline handler performs:

    draft report
        ↓
    EvaluationAgent
        ↓
    refinement required?
        │
        ├── no
        │     ↓
        │   accept draft as final_response
        │
        └── yes
              ↓
          ReportAgent.refine()
              ↓
          final_response

There is intentionally only ONE refinement pass.

Release 0.1 LLM wiring
----------------------
The existing ToolRegistry owns the shared LLMTool.

Bootstrap supplies the registered tools to:

    ReportAgent
    EvaluationAgent

Both agents therefore use the existing provider/model
configuration without introducing another LLM abstraction.

Important
---------
This file does NOT:

- train models
- calibrate models
- implement prediction logic
- implement sensitivity logic
- implement scenario logic
- implement financial logic
- implement report-writing logic
- implement evaluation logic
- import scripts.synthetic_data.*

Runtime model artifacts are supplied through the normal
application configuration layer.
"""

from __future__ import annotations

from mobile_ai_system.agents.evaluation_agent import (
    EvaluationAgent,
)
from mobile_ai_system.agents.impact.impact_agent import (
    ImpactAgent,
)
from mobile_ai_system.agents.information.information_agent import (
    InformationAgent,
)
from mobile_ai_system.agents.report_agent import (
    ReportAgent,
)
from mobile_ai_system.agents.supervisor.supervisor_agent import (
    SupervisorAgent,
)

from mobile_ai_system.application.models.pipeline_context import (
    PipelineContext,
)
from mobile_ai_system.application.parsers.request_parser import (
    RequestParser,
)
from mobile_ai_system.application.registry import (
    CHURN_PREDICTION_SERVICE,
    CHURN_PREDICTION_TOOL,
    CHURN_SENSITIVITY_SERVICE,
    CHURN_SENSITIVITY_TOOL,
    FINANCIAL_IMPACT_SERVICE,
    FINANCIAL_IMPACT_TOOL,
    SETTINGS,
    TELECOM_SCENARIO_SERVICE,
    TELECOM_SCENARIO_TOOL,
)
from mobile_ai_system.application.runner import (
    ApplicationRunner,
)
from mobile_ai_system.application.services.information_service import (
    InformationService,
)

from mobile_ai_system.core.config import (
    get_settings,
)
from mobile_ai_system.core.container import (
    Container,
)

from mobile_ai_system.impact import (
    impact_module,
)

from mobile_ai_system.infrastructure.persistence.mongodb.mongo_client_manager import (
    MongoClientManager,
)
from mobile_ai_system.infrastructure.persistence.mongodb.mongo_config import (
    MongoConfig,
)
from mobile_ai_system.infrastructure.persistence.mongodb.mongo_information_repository import (
    MongoInformationRepository,
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
from mobile_ai_system.tools.tool_registry import (
    ToolRegistry,
)


# =============================================================
# Analytics composition
# =============================================================


def _register_analytics(
    container: Container,
    settings,
) -> None:
    """
    Construct and register runtime analytics services/tools.

    Parameters
    ----------
    container
        Application dependency-injection container.

    settings
        Runtime application settings.

    Dependency graph
    ----------------
    ChurnPredictionService
        ↓
    ChurnPredictionTool


    ChurnSensitivityService
        ↓
    ChurnSensitivityTool


    ChurnSensitivityService
        ↓
    TelecomScenarioService
        ↓
    TelecomScenarioTool


    FinancialImpactService
        ↓
    FinancialImpactTool

    Notes
    -----
    Model artifacts are loaded lazily by the analytics
    services. Bootstrap only provides artifact paths.

    Therefore application startup does not train or
    recalibrate any model.

    The analytics services remain separate from the
    frozen event-level Impact pipeline.
    """

    # =========================================================
    # Runtime artifact paths
    # =========================================================

    churn_calibrated_model_path = (
        settings.churn_calibrated_model_path
    )

    churn_sensitivity_model_path = (
        settings.churn_sensitivity_model_path
    )

    # =========================================================
    # Analytics Services
    # =========================================================

    churn_prediction_service = (
        ChurnPredictionService(
            model_path=(
                churn_calibrated_model_path
            )
        )
    )

    churn_sensitivity_service = (
        ChurnSensitivityService(
            model_path=(
                churn_sensitivity_model_path
            )
        )
    )

    telecom_scenario_service = (
        TelecomScenarioService(
            sensitivity_service=(
                churn_sensitivity_service
            )
        )
    )

    financial_impact_service = (
        FinancialImpactService()
    )

    # =========================================================
    # Register analytics services
    # =========================================================

    container.register_instance(
        CHURN_PREDICTION_SERVICE,
        churn_prediction_service,
    )

    container.register_instance(
        CHURN_SENSITIVITY_SERVICE,
        churn_sensitivity_service,
    )

    container.register_instance(
        TELECOM_SCENARIO_SERVICE,
        telecom_scenario_service,
    )

    container.register_instance(
        FINANCIAL_IMPACT_SERVICE,
        financial_impact_service,
    )

    # =========================================================
    # Analytics Tools
    # =========================================================

    churn_prediction_tool = (
        ChurnPredictionTool(
            service=(
                churn_prediction_service
            )
        )
    )

    churn_sensitivity_tool = (
        ChurnSensitivityTool(
            service=(
                churn_sensitivity_service
            )
        )
    )

    telecom_scenario_tool = (
        TelecomScenarioTool(
            service=(
                telecom_scenario_service
            )
        )
    )

    financial_impact_tool = (
        FinancialImpactTool(
            service=(
                financial_impact_service
            )
        )
    )

    # =========================================================
    # Register analytics tools
    # =========================================================

    container.register_instance(
        CHURN_PREDICTION_TOOL,
        churn_prediction_tool,
    )

    container.register_instance(
        CHURN_SENSITIVITY_TOOL,
        churn_sensitivity_tool,
    )

    container.register_instance(
        TELECOM_SCENARIO_TOOL,
        telecom_scenario_tool,
    )

    container.register_instance(
        FINANCIAL_IMPACT_TOOL,
        financial_impact_tool,
    )


# =============================================================
# Bootstrap
# =============================================================


class Bootstrap:
    """
    Build the application dependency graph.

    Architecture v2.3 intentionally uses the project's
    lightweight Container rather than a third-party
    dependency-injection framework.
    """

    def build(
        self,
    ) -> Container:
        """
        Build and return the application container.
        """

        # =====================================================
        # Configuration
        # =====================================================

        settings = get_settings()

        container = Container()

        container.register_instance(
            SETTINGS,
            settings,
        )

        # =====================================================
        # MongoDB
        # =====================================================

        mongo_config = (
            MongoConfig.from_settings(
                settings,
            )
        )

        mongo_manager = (
            MongoClientManager(
                mongo_config.connection_string,
            )
        )

        collection = (
            mongo_manager.collection(
                mongo_config.database_name,
                mongo_config.collection_name,
            )
        )

        information_repository = (
            MongoInformationRepository(
                collection,
            )
        )

        # =====================================================
        # Information Service
        # =====================================================

        information_service = (
            InformationService(
                information_repository,
            )
        )

        # =====================================================
        # Analytics Runtime Layer
        # =====================================================
        #
        # Register the four analytics services and four
        # Analysis-Agent-facing tools.
        #
        # These services remain available independently of
        # the frozen event-level Impact Layer.
        # =====================================================

        _register_analytics(
            container=container,
            settings=settings,
        )

        # =====================================================
        # Shared Tool Registry
        # =====================================================
        #
        # ToolRegistry already owns the project's standard
        # built-in tools:
        #
        #   mongo
        #   postgres
        #   vector
        #   web
        #   llm
        #
        # ReportAgent and EvaluationAgent receive these tools
        # later in the composition process.
        # =====================================================

        tool_registry = ToolRegistry()

        container.register_instance(
            "tool_registry",
            tool_registry,
        )

        # =====================================================
        # Agents
        # =====================================================

        information_agent = (
            InformationAgent(
                information_service,
            )
        )

        supervisor_agent = (
            SupervisorAgent()
        )

        # =====================================================
        # Parser
        # =====================================================

        parser = RequestParser()

        # =====================================================
        # Runner
        # =====================================================

        runner = ApplicationRunner()

        # =====================================================
        # Pipeline handlers
        # =====================================================

        runner.register(
            "information",
            information_agent.execute,
        )

        # =====================================================
        # Core / Application Registrations
        # =====================================================

        container.register_instance(
            "mongo_config",
            mongo_config,
        )

        container.register_instance(
            "mongo_manager",
            mongo_manager,
        )

        container.register_instance(
            "information_repository",
            information_repository,
        )

        container.register_instance(
            "information_service",
            information_service,
        )

        container.register_instance(
            "information_agent",
            information_agent,
        )

        container.register_instance(
            "supervisor_agent",
            supervisor_agent,
        )

        container.register_instance(
            "request_parser",
            parser,
        )

        container.register_instance(
            "runner",
            runner,
        )

        # =====================================================
        # Impact Layer
        # =====================================================
        #
        # Impact-specific construction belongs to
        # impact_module.
        #
        # The module remains responsible for registering:
        #
        #   FeatureBuilder
        #   ChurnEngine
        #   SensitivityEngine
        #   CausalEngine
        #   FinancialEngine
        #   ImpactService
        #
        # Important Release 0.1 boundary:
        #
        # The customer-level ChurnPredictionService is NOT
        # injected into the event-level ChurnEngine.
        #
        # The two layers use different feature contracts:
        #
        # impact_module
        #     event-level InformationResult features
        #
        # services.analytics
        #     customer-level engineered ML features
        #
        # Keeping them separate prevents invalid feature
        # fabrication and preserves truthful runtime behavior.
        # =====================================================

        impact_module.register(
            container,
        )

        # =====================================================
        # Impact Agent
        # =====================================================

        impact_service = (
            container.resolve(
                "impact_service"
            )
        )

        impact_agent = (
            ImpactAgent(
                impact_service=(
                    impact_service
                ),
            )
        )

        container.register_instance(
            "impact_agent",
            impact_agent,
        )

        runner.register(
            "impact",
            impact_agent.execute,
        )

        # =====================================================
        # Shared Agent Tools
        # =====================================================
        #
        # all() returns a shallow dictionary copy.
        #
        # The underlying tool objects remain shared, so both
        # ReportAgent and EvaluationAgent receive the exact
        # same LLMTool instance.
        # =====================================================

        agent_tools = (
            tool_registry.all()
        )

        # =====================================================
        # Report Agent
        # =====================================================

        report_agent = (
            ReportAgent()
        )

        report_agent.tools = (
            dict(
                agent_tools
            )
        )

        container.register_instance(
            "report_agent",
            report_agent,
        )

        runner.register(
            "report",
            report_agent.execute,
        )

        # =====================================================
        # Evaluation Agent
        # =====================================================

        evaluation_agent = (
            EvaluationAgent()
        )

        evaluation_agent.tools = (
            dict(
                agent_tools
            )
        )

        container.register_instance(
            "evaluation_agent",
            evaluation_agent,
        )

        # =====================================================
        # Step 12D
        # Evaluation + single refinement/finalization
        # =====================================================

        def evaluate_and_finalize(
            context: PipelineContext,
        ) -> PipelineContext:
            """
            Evaluate the draft report and perform at most one
            report-refinement pass.

            Execution flow
            --------------

            report_result
                ↓
            EvaluationAgent.execute()
                ↓
            requires_report_refinement?
                │
                ├── False
                │      ↓
                │   final_response already populated
                │
                └── True
                       ↓
                   ReportAgent.refine()
                       ↓
                   final_response

            Important
            ---------
            There is intentionally:

            - no recursive refinement
            - no second evaluation
            - no retry loop
            - no new pipeline step

            This keeps the Frozen MVP execution path small
            and deterministic.
            """

            # -------------------------------------------------
            # Evaluate draft
            # -------------------------------------------------

            context = (
                evaluation_agent.execute(
                    context
                )
            )

            # -------------------------------------------------
            # Refinement decision
            # -------------------------------------------------

            requires_refinement = bool(
                context.metadata.get(
                    "requires_report_refinement",
                    False,
                )
            )

            # -------------------------------------------------
            # Passing report
            #
            # EvaluationAgent already copied report_result
            # into final_response.
            # -------------------------------------------------

            if not requires_refinement:

                context.metadata[
                    "report_refinement_performed"
                ] = False

                context.metadata[
                    "report_refinement_count"
                ] = 0

                return context

            # -------------------------------------------------
            # No draft available
            #
            # There is nothing to refine.
            # -------------------------------------------------

            if context.report_result is None:

                context.metadata[
                    "report_refinement_performed"
                ] = False

                context.metadata[
                    "report_refinement_count"
                ] = 0

                return context

            # -------------------------------------------------
            # Exactly ONE refinement pass
            # -------------------------------------------------

            context = (
                report_agent.refine(
                    context=context,
                    feedback=(
                        context.evaluation_result
                    ),
                )
            )

            # -------------------------------------------------
            # Refinement audit metadata
            # -------------------------------------------------

            context.metadata[
                "report_refinement_performed"
            ] = True

            context.metadata[
                "report_refinement_count"
            ] = 1

            return context

        # -----------------------------------------------------
        # Register combined evaluation/finalization handler
        # -----------------------------------------------------

        runner.register(
            "evaluation",
            evaluate_and_finalize,
        )

        # =====================================================
        # Complete
        # =====================================================

        return container