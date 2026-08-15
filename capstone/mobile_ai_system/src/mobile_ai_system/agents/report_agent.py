"""
Report Agent

Architecture v2.3 (Frozen MVP)

Responsibilities
----------------
Receive InformationResult and ImpactResult from
PipelineContext.

Summarize those upstream analytical results into a
prompt-friendly representation.

Generate an executive report through the configured
LLM tool.

Store the generated draft report in PipelineContext.

Support one optional refinement pass using feedback
from EvaluationAgent.

The agent performs report orchestration only.

Analytical business logic belongs to the Information
and Impact layers.
"""

from __future__ import annotations

from dataclasses import (
    asdict,
    is_dataclass,
)
from typing import Any

from mobile_ai_system.agents.base_agent import (
    BaseAgent,
)
from mobile_ai_system.application.models.pipeline_context import (
    PipelineContext,
)
from mobile_ai_system.core.config import (
    get_settings,
)
from mobile_ai_system.infrastructure.logging.logger import (
    get_logger,
)
from mobile_ai_system.utils.prompt_loader import (
    load_agent_prompts,
)


settings = get_settings()

logger = get_logger(
    __name__
)


class ReportAgent(BaseAgent):
    """
    Pipeline Report Agent.

    Converts Information and Impact results into an
    executive telecom competitive-intelligence report.
    """

    # =========================================================
    # Identity
    # =========================================================

    @property
    def name(self) -> str:
        """
        Return the pipeline-stage name.
        """

        return "report"

    # =========================================================
    # Draft generation
    # =========================================================

    def execute(
        self,
        context: PipelineContext,
    ) -> PipelineContext:
        """
        Generate the draft report for the current pipeline
        context.

        Parameters
        ----------
        context
            Shared application pipeline context.

        Returns
        -------
        PipelineContext
            Same context instance with report_result
            populated.

        Raises
        ------
        RuntimeError
            If information_result or impact_result is missing.
        """

        logger.info(
            "%s started",
            self.name,
        )

        # -----------------------------------------------------
        # Required upstream results
        # -----------------------------------------------------

        information = (
            context.information_result
        )

        if information is None:
            raise RuntimeError(
                "PipelineContext has no InformationResult."
            )

        impact = (
            context.impact_result
        )

        if impact is None:
            raise RuntimeError(
                "PipelineContext has no ImpactResult."
            )

        # -----------------------------------------------------
        # Original request
        # -----------------------------------------------------

        user_request = (
            self._get_user_request(
                context
            )
        )

        # -----------------------------------------------------
        # Prompt-friendly summaries
        # -----------------------------------------------------

        information_summary = (
            self._serialize_information(
                information
            )
        )

        impact_summary = (
            self._serialize_impact(
                impact
            )
        )

        logger.info(
            "Generating report from InformationResult "
            "and ImpactResult"
        )

        # -----------------------------------------------------
        # Prompt package
        # -----------------------------------------------------

        template = (
            load_agent_prompts(
                "report",
            )
        )

        prompt = template.format(
            user_request=(
                user_request
            ),

            # Backward-compatible placeholder used by the
            # existing report prompt.
            retrieved_events=(
                information_summary
            ),

            # Preferred explicit names for the MVP report flow.
            information_result=(
                information_summary
            ),

            impact_result=(
                impact_summary
            ),
        )

        # -----------------------------------------------------
        # LLM draft generation
        # -----------------------------------------------------

        report = (
            self._generate_report(
                prompt
            )
        )

        # -----------------------------------------------------
        # Save draft
        # -----------------------------------------------------

        context.report_result = (
            report
        )

        logger.info(
            "Draft report generated (%d chars)",
            len(
                report
            ),
        )

        logger.info(
            "%s finished",
            self.name,
        )

        return context

    # =========================================================
    # Single-pass refinement
    # =========================================================

    def refine(
        self,
        context: PipelineContext,
        feedback: Any | None = None,
    ) -> PipelineContext:
        """
        Refine the existing draft report once.

        This method supports the MVP evaluation flow:

            draft
                ↓
            evaluation feedback
                ↓
            one refinement
                ↓
            final_response

        No iterative or recursive refinement loop is
        implemented in the MVP.

        Parameters
        ----------
        context
            Pipeline context containing the existing draft,
            InformationResult, and ImpactResult.

        feedback
            Evaluator feedback.

            When omitted, context.evaluation_result is used.

        Returns
        -------
        PipelineContext
            Same context with final_response populated.
        """

        logger.info(
            "%s refinement started",
            self.name,
        )

        information = (
            context.information_result
        )

        if information is None:
            raise RuntimeError(
                "PipelineContext has no InformationResult."
            )

        impact = (
            context.impact_result
        )

        if impact is None:
            raise RuntimeError(
                "PipelineContext has no ImpactResult."
            )

        draft = (
            context.report_result
        )

        if draft is None:
            raise RuntimeError(
                "PipelineContext has no report_result."
            )

        if feedback is None:
            feedback = (
                context.evaluation_result
            )

        if feedback is None:
            raise RuntimeError(
                "No evaluation feedback is available."
            )

        user_request = (
            self._get_user_request(
                context
            )
        )

        information_summary = (
            self._serialize_information(
                information
            )
        )

        impact_summary = (
            self._serialize_impact(
                impact
            )
        )

        feedback_summary = (
            self._serialize_value(
                feedback
            )
        )

        # -----------------------------------------------------
        # MVP refinement prompt
        #
        # We intentionally build this locally rather than add
        # another prompt/module dependency.
        # -----------------------------------------------------

        prompt = (
            "You are revising an executive telecom "
            "competitive-intelligence report.\n\n"

            "ORIGINAL USER REQUEST\n"
            f"{user_request}\n\n"

            "INFORMATION ANALYSIS\n"
            f"{information_summary}\n\n"

            "IMPACT ANALYSIS\n"
            f"{impact_summary}\n\n"

            "DRAFT REPORT\n"
            f"{draft}\n\n"

            "EVALUATOR FEEDBACK\n"
            f"{feedback_summary}\n\n"

            "TASK\n"
            "Revise the draft report using the evaluator "
            "feedback.\n"
            "Preserve facts supported by the Information and "
            "Impact results.\n"
            "Do not invent evidence, metrics, causal claims, "
            "or financial values.\n"
            "Correct the identified weaknesses and improve "
            "clarity, completeness, executive usefulness, "
            "and actionability.\n"
            "Return only the final revised report."
        )

        final_report = (
            self._generate_report(
                prompt
            )
        )

        context.final_response = (
            final_report
        )

        logger.info(
            "Final refined report generated (%d chars)",
            len(
                final_report
            ),
        )

        logger.info(
            "%s refinement finished",
            self.name,
        )

        return context

    # =========================================================
    # Accept draft as final
    # =========================================================

    @staticmethod
    def accept_draft(
        context: PipelineContext,
    ) -> PipelineContext:
        """
        Accept the current draft report as the final response.

        Used when EvaluationAgent determines that refinement
        is unnecessary.
        """

        if context.report_result is None:
            raise RuntimeError(
                "PipelineContext has no report_result."
            )

        context.final_response = str(
            context.report_result
        )

        return context

    # =========================================================
    # User request
    # =========================================================

    @staticmethod
    def _get_user_request(
        context: PipelineContext,
    ) -> str:
        """
        Extract the original user request from pipeline
        metadata.

        The Frozen MVP keeps this tolerant because request
        representation remains owned by the Application Layer.
        """

        if (
            context.parse_result
            is not None
        ):

            request = getattr(
                context.parse_result,
                "request",
                None,
            )

            if request is not None:

                text = getattr(
                    request,
                    "text",
                    None,
                )

                if text:
                    return str(
                        text
                    )

        return str(
            context.metadata.get(
                "user_request",
                "",
            )
        )

    # =========================================================
    # Information serialization
    # =========================================================

    @classmethod
    def _serialize_information(
        cls,
        information: Any,
    ) -> Any:
        """
        Convert InformationResult into prompt-friendly data.

        The method deliberately summarizes the structured
        Information Layer output rather than performing new
        analysis.
        """

        # -----------------------------------------------------
        # Explicit to_dict contract
        # -----------------------------------------------------

        to_dict = getattr(
            information,
            "to_dict",
            None,
        )

        if callable(
            to_dict
        ):
            return cls._serialize_value(
                to_dict()
            )

        # -----------------------------------------------------
        # Dataclass
        # -----------------------------------------------------

        if is_dataclass(
            information
        ):
            return cls._serialize_value(
                asdict(
                    information
                )
            )

        # -----------------------------------------------------
        # Existing InformationResult shape
        #
        # Keep only relevant information if available.
        # -----------------------------------------------------

        result: dict[
            str,
            Any,
        ] = {}

        records = getattr(
            information,
            "records",
            None,
        )

        if records is not None:
            result[
                "records"
            ] = cls._serialize_value(
                records
            )

        total_records = getattr(
            information,
            "total_records",
            None,
        )

        if total_records is not None:
            result[
                "total_records"
            ] = total_records

        metadata = getattr(
            information,
            "metadata",
            None,
        )

        if metadata is not None:
            result[
                "metadata"
            ] = cls._serialize_value(
                metadata
            )

        if result:
            return result

        return cls._serialize_value(
            information
        )

    # =========================================================
    # Impact serialization
    # =========================================================

    @classmethod
    def _serialize_impact(
        cls,
        impact: Any,
    ) -> Any:
        """
        Convert ImpactResult into prompt-friendly data.

        If ImpactResult exposes to_dict(), use it.

        Dataclasses are also converted automatically.
        """

        to_dict = getattr(
            impact,
            "to_dict",
            None,
        )

        if callable(
            to_dict
        ):
            return cls._serialize_value(
                to_dict()
            )

        if is_dataclass(
            impact
        ):
            return cls._serialize_value(
                asdict(
                    impact
                )
            )

        return cls._serialize_value(
            impact
        )

    # =========================================================
    # Generic serialization
    # =========================================================

    @classmethod
    def _serialize_value(
        cls,
        value: Any,
    ) -> Any:
        """
        Recursively convert common structured result objects
        into prompt-friendly Python values.

        No analytical transformations are performed.
        """

        if is_dataclass(
            value
        ):
            return cls._serialize_value(
                asdict(
                    value
                )
            )

        if isinstance(
            value,
            dict,
        ):
            return {
                str(
                    key
                ): cls._serialize_value(
                    item
                )
                for key, item in value.items()
            }

        if isinstance(
            value,
            (
                list,
                tuple,
            ),
        ):
            return [
                cls._serialize_value(
                    item
                )
                for item in value
            ]

        return value

    # =========================================================
    # LLM generation
    # =========================================================

    def _generate_report(
        self,
        prompt: str,
    ) -> str:
        """
        Generate report text using the configured LLM tool.
        """

        tools = getattr(
            self,
            "tools",
            None,
        )

        llm = None

        if tools is not None:
            llm = tools.get(
                "llm",
            )

        if llm is None:

            logger.warning(
                "LLMTool is unavailable."
            )

            return "LLM unavailable."

        report = llm.generate(
            provider=(
                settings
                .report_agent_provider
            ),
            model=(
                settings
                .report_agent_model
            ),
            prompt=(
                prompt
            ),
        )

        return str(
            report
        )