"""
Application entry point.

Architecture v2.3 (Frozen MVP)

Responsibilities
----------------
Initialize the application.

Accept user requests from the command line.

Parse the request.

Ask SupervisorAgent to build the deterministic
ExecutionPlan.

Execute the plan through ApplicationRunner.

Print the final report returned through PipelineContext.

The CLI contains no analytical business logic.
"""

from __future__ import annotations

from mobile_ai_system.application.lifecycle import (
    ApplicationLifecycle,
)
from mobile_ai_system.application.models.pipeline_context import (
    PipelineContext,
)
from mobile_ai_system.infrastructure.logging import (
    get_logger,
)


logger = get_logger(
    __name__
)


# =============================================================
# Request execution
# =============================================================


def execute_request(
    app: ApplicationLifecycle,
    user_input: str,
) -> str:
    """
    Execute one user request through the complete MVP pipeline.

    Runtime flow
    ------------
    user_input
        ↓
    RequestParser
        ↓
    ParseResult
        ↓
    SupervisorAgent
        ↓
    ExecutionPlan
        ↓
    ApplicationRunner
        ↓
    InformationAgent
        ↓
    ImpactAgent
        ↓
    ReportAgent
        ↓
    EvaluationAgent
        ↓
    optional single refinement
        ↓
    final_response

    Parameters
    ----------
    app
        Initialized ApplicationLifecycle.

    user_input
        Raw CLI request.

    Returns
    -------
    str
        Final generated report.

    Raises
    ------
    RuntimeError
        If the application has not been initialized or
        required runtime components are unavailable.
    """

    # =========================================================
    # Application container
    # =========================================================

    container = app.container

    if container is None:
        raise RuntimeError(
            "Application is not initialized."
        )

    # =========================================================
    # Resolve application components
    # =========================================================

    parser = container.resolve(
        "request_parser"
    )

    supervisor = container.resolve(
        "supervisor_agent"
    )

    runner = container.resolve(
        "runner"
    )

    # =========================================================
    # Parse request
    # =========================================================

    parse_result = parser.parse(
        user_input
    )

    # =========================================================
    # Supervisor planning
    # =========================================================

    execution_plan = supervisor.plan(
        parse_result
    )

    # =========================================================
    # Pipeline context
    # =========================================================

    context = PipelineContext(
        parse_result=parse_result,
        execution_plan=execution_plan,
        metadata={
            "user_request": user_input,
        },
    )

    # =========================================================
    # Execute pipeline
    # =========================================================

    context = runner.run(
        execution_plan,
        context,
    )

    # =========================================================
    # Final response
    # =========================================================

    final_response = (
        context.final_response
    )

    # ---------------------------------------------------------
    # Defensive MVP fallback
    #
    # In a normal information → impact → report → evaluation
    # pipeline, final_response should always be populated.
    #
    # report_result is retained as a safe fallback in case a
    # custom ExecutionPlan intentionally omits evaluation.
    # ---------------------------------------------------------

    if not final_response:
        final_response = (
            context.report_result
        )

    if not final_response:
        raise RuntimeError(
            "Pipeline completed without generating "
            "a final report."
        )

    return str(
        final_response
    )


# =============================================================
# CLI
# =============================================================


def main() -> None:
    """
    Start the application CLI.
    """

    app = ApplicationLifecycle()

    logger.info(
        "Initializing application..."
    )

    app.initialize()

    print()

    print(
        "=" * 60
    )

    print(
        " Mobile AI Strategic Intelligence Platform "
    )

    print(
        "=" * 60
    )

    print()

    print(
        "Type 'exit' to quit."
    )

    try:

        while True:

            user_input = input(
                "\nUser > "
            )

            # -------------------------------------------------
            # Normalize input
            # -------------------------------------------------

            user_input = (
                user_input.strip()
            )

            # -------------------------------------------------
            # Exit
            # -------------------------------------------------

            if (
                user_input.lower()
                ==
                "exit"
            ):
                break

            # -------------------------------------------------
            # Ignore empty input
            # -------------------------------------------------

            if not user_input:

                print(
                    "\nPlease enter a request."
                )

                continue

            # -------------------------------------------------
            # Execute complete MVP pipeline
            # -------------------------------------------------

            try:

                final_response = (
                    execute_request(
                        app=app,
                        user_input=user_input,
                    )
                )

            except Exception as exc:

                logger.exception(
                    "Request execution failed."
                )

                print()

                print(
                    "Request failed:"
                )

                print(
                    str(
                        exc
                    )
                )

                continue

            # -------------------------------------------------
            # Output
            # -------------------------------------------------

            print()

            print(
                "-" * 60
            )

            print(
                "Final Report"
            )

            print(
                "-" * 60
            )

            print()

            print(
                final_response
            )

    finally:

        logger.info(
            "Application shutting down..."
        )

        app.shutdown()


if __name__ == "__main__":

    main()