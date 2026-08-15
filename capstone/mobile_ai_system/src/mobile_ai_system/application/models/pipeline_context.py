"""
Pipeline Context

Architecture v2.3 (Frozen MVP)

Shared execution state passed between agents.

MVP execution flow
------------------
parse_result
    ↓
execution_plan
    ↓
information_result
    ↓
impact_result
    ↓
report_result
    ↓
evaluation_result
    ↓
final_response

The context is intentionally lightweight.

It carries pipeline state only and contains no
business or orchestration logic.
"""

from __future__ import annotations

from dataclasses import (
    dataclass,
    field,
)
from typing import Any


@dataclass
class PipelineContext:
    """
    Shared state for the execution pipeline.
    """

    # ---------------------------------------------------------
    # Request parsing / planning
    # ---------------------------------------------------------

    parse_result: Any | None = None

    execution_plan: Any | None = None

    # ---------------------------------------------------------
    # Information Layer
    # ---------------------------------------------------------

    information_result: Any | None = None

    # ---------------------------------------------------------
    # Impact Layer
    # ---------------------------------------------------------

    impact_result: Any | None = None

    # ---------------------------------------------------------
    # Report Layer
    #
    # Draft report generated from InformationResult +
    # ImpactResult.
    # ---------------------------------------------------------

    report_result: Any | None = None

    # ---------------------------------------------------------
    # Evaluation Layer
    #
    # Evaluation score, issues, and improvement feedback.
    # ---------------------------------------------------------

    evaluation_result: Any | None = None

    # ---------------------------------------------------------
    # Final output
    #
    # Either:
    #
    #   - the accepted draft report
    #
    # or:
    #
    #   - the single refined report after evaluator feedback.
    # ---------------------------------------------------------

    final_response: str | None = None

    # ---------------------------------------------------------
    # Shared metadata
    # ---------------------------------------------------------

    metadata: dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )