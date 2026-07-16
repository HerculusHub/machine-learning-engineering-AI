from mobile_ai_system.infrastructure.logging.logger import get_logger
from mobile_ai_system.utils.prompt_loader import load_agent_prompts
from mobile_ai_system.core.config import get_settings

from .base_agent import BaseAgent

settings = get_settings()

logger = get_logger(__name__)


class ReportAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "ReportAgent"

    def run(self, state):

        logger.info("%s started", self.name)

        # =====================================================
        # Retrieve workflow results
        # =====================================================

        user_request = state.get(
            "user_request",
            "",
        )

        events = state.get(
            "retrieved_events",
            [],
        )

        impact = state.get(
            "impact_result",
            {},
        )

        logger.info(
            "Generating report from %d events",
            len(events),
        )

        # =====================================================
        # Load Prompt Package
        # =====================================================

        template = load_agent_prompts(
            "report",
        )

        prompt = template.format(

            user_request=user_request,

            retrieved_events=events,

            impact_result=impact,

        )

        # =====================================================
        # Generate Report via LLM
        # =====================================================

        llm = self.tools.get("llm")

        if llm is None:
            logger.warning(
                "LLMTool is unavailable."
            ) 

            report = "LLM unavailable."

        else:

            report = llm.generate(
                provider=settings.report_agent_provider,

                model=settings.report_agent_model,

                prompt=prompt,

            )

        # =====================================================
        # Save Result
        # =====================================================

        state["report"] = report

        logger.info(

            "Report generated (%d chars)",

            len(report),

        )

        logger.info("%s finished", self.name)

        return state