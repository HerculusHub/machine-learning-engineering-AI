"""
Impact Agent

Architecture v2.3 (Frozen MVP)

Responsibilities
----------------
Receive InformationResult from PipelineContext.

Call ImpactService.

Store ImpactResult back into PipelineContext.

No business logic belongs in this agent.
"""

from __future__ import annotations

from mobile_ai_system.agents.base_agent import (
    BaseAgent,
)
from mobile_ai_system.application.models.pipeline_context import (
    PipelineContext,
)
from mobile_ai_system.impact.interfaces.i_impact_service import (
    IImpactService,
)


class ImpactAgent(BaseAgent):
    """
    Pipeline adapter for the Impact Layer.
    """

    def __init__(
        self,
        impact_service: IImpactService,
    ) -> None:
        self._impact_service = impact_service

    # ---------------------------------------------------------
    # Identity
    # ---------------------------------------------------------

    @property
    def name(self) -> str:
        """
        Return the pipeline-stage name.
        """

        return "impact"

    # ---------------------------------------------------------
    # Execution
    # ---------------------------------------------------------

    def execute(
        self,
        context: PipelineContext,
    ) -> PipelineContext:
        """
        Execute Impact Layer analysis.

        Parameters
        ----------
        context
            Shared pipeline context.

        Returns
        -------
        PipelineContext
            Same context instance with impact_result populated.

        Raises
        ------
        RuntimeError
            If information_result has not been populated.
        """

        information = context.information_result

        if information is None:
            raise RuntimeError(
                "PipelineContext has no InformationResult."
            )

        impact_result = self._impact_service.evaluate(
            information,
        )

        context.impact_result = impact_result

        return context