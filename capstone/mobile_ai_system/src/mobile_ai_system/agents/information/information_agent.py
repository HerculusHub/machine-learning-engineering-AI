"""
Information Agent

Architecture v2.3 (Frozen MVP)

Responsibilities
----------------
Retrieve structured information through InformationService.

Runtime pipeline mode
---------------------
Receive PipelineContext, read ParseResult, perform retrieval,
store InformationResult back into PipelineContext, and return
the same PipelineContext.

Legacy compatibility mode
-------------------------
Receive ParseResult directly and return InformationResult.

This compatibility path preserves the existing Architecture
v2.3 unit-test contract while allowing ApplicationRunner to
use the agent as a normal pipeline adapter.

This agent never calls an LLM.
"""

from __future__ import annotations

from typing import Any

from mobile_ai_system.agents.base_agent import (
    BaseAgent,
)
from mobile_ai_system.application.models.information_result import (
    InformationResult,
)
from mobile_ai_system.application.models.pipeline_context import (
    PipelineContext,
)
from mobile_ai_system.application.parsers.parse_result import (
    ParseResult,
)


class InformationAgent(BaseAgent):
    """
    Information retrieval agent.

    Supported execution modes
    -------------------------

    Runtime pipeline:

        PipelineContext
            ↓
        ParseResult
            ↓
        InformationService
            ↓
        InformationResult
            ↓
        PipelineContext

    Legacy direct invocation:

        ParseResult
            ↓
        InformationService
            ↓
        InformationResult
    """

    def __init__(
        self,
        service: Any,
    ) -> None:

        self._service = service

    # =========================================================
    # Identity
    # =========================================================

    @property
    def name(self) -> str:
        """
        Return the agent name / pipeline stage name.
        """

        return "information"

    # =========================================================
    # Execution
    # =========================================================

    def execute(
        self,
        input_value: PipelineContext | ParseResult,
    ) -> PipelineContext | InformationResult:
        """
        Execute information retrieval.

        Parameters
        ----------
        input_value
            Either:

            - PipelineContext for normal application execution
            - ParseResult for backward-compatible direct use

        Returns
        -------
        PipelineContext | InformationResult
            PipelineContext when called by ApplicationRunner.

            InformationResult when called directly with a
            ParseResult.

        Raises
        ------
        RuntimeError
            If required request state is missing.

        TypeError
            If an unsupported input type is supplied or the
            service returns an invalid result.
        """

        # =====================================================
        # Runtime pipeline mode
        # =====================================================

        if isinstance(
            input_value,
            PipelineContext,
        ):

            return self._execute_pipeline(
                input_value
            )

        # =====================================================
        # Legacy direct-agent mode
        # =====================================================

        if isinstance(
            input_value,
            ParseResult,
        ):

            return self._execute_parse_result(
                input_value
            )

        # =====================================================
        # Invalid invocation
        # =====================================================

        raise TypeError(
            "InformationAgent.execute() expected "
            "PipelineContext or ParseResult; "
            f"received {type(input_value).__name__}."
        )

    # =========================================================
    # Pipeline execution
    # =========================================================

    def _execute_pipeline(
        self,
        context: PipelineContext,
    ) -> PipelineContext:
        """
        Execute the Information stage through PipelineContext.
        """

        parse_result = (
            context.parse_result
        )

        if parse_result is None:

            raise RuntimeError(
                "PipelineContext has no ParseResult."
            )

        information_result = (
            self._execute_parse_result(
                parse_result
            )
        )

        context.information_result = (
            information_result
        )

        return context

    # =========================================================
    # Direct ParseResult execution
    # =========================================================

    def _execute_parse_result(
        self,
        parse_result: ParseResult,
    ) -> InformationResult:
        """
        Retrieve information from a ParseResult.

        This is also the compatibility path used by existing
        direct InformationAgent unit tests.
        """

        request = getattr(
            parse_result,
            "request",
            None,
        )

        if request is None:

            raise RuntimeError(
                "ParseResult has no Request."
            )

        information_result = (
            self._retrieve_information(
                request
            )
        )

        if not isinstance(
            information_result,
            InformationResult,
        ):

            raise TypeError(
                "Information service returned "
                f"{type(information_result).__name__}; "
                "expected InformationResult."
            )

        return information_result

    # =========================================================
    # Service delegation
    # =========================================================

    def _retrieve_information(
        self,
        request: Any,
    ) -> InformationResult:
        """
        Delegate retrieval to InformationService.

        Preferred current service contract
        ----------------------------------
        search(request)

        Legacy compatibility contract
        -----------------------------
        retrieve(request)

        ``search`` is preferred because it is the API exposed
        by the current concrete InformationService.
        """

        # -----------------------------------------------------
        # Current production service API
        # -----------------------------------------------------

        search = getattr(
            self._service,
            "search",
            None,
        )

        if callable(
            search
        ):

            return search(
                request
            )

        # -----------------------------------------------------
        # Legacy test/service API
        # -----------------------------------------------------

        retrieve = getattr(
            self._service,
            "retrieve",
            None,
        )

        if callable(
            retrieve
        ):

            return retrieve(
                request
            )

        raise RuntimeError(
            "Information service exposes neither "
            "search() nor retrieve()."
        )

    # =========================================================
    # Dependency access
    # =========================================================

    @property
    def service(
        self,
    ) -> Any:
        """
        Return the configured InformationService.
        """

        return self._service