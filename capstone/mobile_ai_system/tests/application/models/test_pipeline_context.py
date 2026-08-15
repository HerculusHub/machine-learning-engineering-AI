"""
Unit tests for PipelineContext.

Architecture v2.3 (Frozen MVP)

PipelineContext is the shared execution state passed
between application pipeline stages.

Current canonical fields:

    parse_result
    execution_plan
    information_result
    impact_result
    report_result
    evaluation_result
    metadata
"""

from __future__ import annotations

from mobile_ai_system.application.models.pipeline_context import (
    PipelineContext,
)


def test_default_context():
    """
    A new PipelineContext should start with
    empty pipeline-stage results.
    """

    context = PipelineContext()

    assert context.parse_result is None

    assert context.execution_plan is None

    assert context.information_result is None

    assert context.impact_result is None

    assert context.report_result is None

    assert context.evaluation_result is None

    assert context.metadata == {}


def test_context_can_store_pipeline_results():
    """
    PipelineContext should allow pipeline stages
    to populate their result fields.
    """

    context = PipelineContext()

    parse_result = object()
    execution_plan = object()
    information_result = object()
    impact_result = object()
    report_result = object()
    evaluation_result = object()

    context.parse_result = parse_result
    context.execution_plan = execution_plan
    context.information_result = information_result
    context.impact_result = impact_result
    context.report_result = report_result
    context.evaluation_result = evaluation_result

    assert context.parse_result is parse_result

    assert context.execution_plan is execution_plan

    assert context.information_result is information_result

    assert context.impact_result is impact_result

    assert context.report_result is report_result

    assert context.evaluation_result is evaluation_result


def test_metadata_can_store_pipeline_state():
    """
    metadata should hold optional execution state
    without expanding the core context schema.
    """

    context = PipelineContext(
        metadata={
            "user_request": "Analyze Verizon",
            "evaluation_score": 0.90,
        }
    )

    assert context.metadata[
        "user_request"
    ] == "Analyze Verizon"

    assert context.metadata[
        "evaluation_score"
    ] == 0.90


def test_context_instances_do_not_share_metadata():
    """
    PipelineContext instances should not share
    the default metadata dictionary.
    """

    first = PipelineContext()

    second = PipelineContext()

    first.metadata[
        "source"
    ] = "first"

    assert first.metadata == {
        "source": "first",
    }

    assert second.metadata == {}


def test_context_can_be_initialized_with_results():
    """
    PipelineContext should support initialization
    with existing pipeline results.
    """

    information = {
        "records": [
            "EVENT-001",
        ],
    }

    impact = {
        "score": 0.25,
    }

    context = PipelineContext(
        information_result=information,
        impact_result=impact,
    )

    assert context.information_result is information

    assert context.impact_result is impact


def test_context_preserves_stage_handoff():
    """
    Later pipeline stages should not overwrite
    earlier stage results unless explicitly changed.
    """

    information = object()
    impact = object()
    report = "Executive report."

    context = PipelineContext(
        information_result=information,
        impact_result=impact,
    )

    context.report_result = report

    assert context.information_result is information

    assert context.impact_result is impact

    assert context.report_result == report

def test_pipeline_context_supports_complete_report_flow():
    """
    PipelineContext should carry the complete MVP report flow.
    """

    context = PipelineContext()

    assert context.information_result is None
    assert context.impact_result is None
    assert context.report_result is None
    assert context.evaluation_result is None
    assert context.final_response is None

    context.information_result = "information"
    context.impact_result = "impact"
    context.report_result = "draft"

    context.evaluation_result = {
        "score": 85,
        "feedback": "Improve recommendations.",
    }

    context.final_response = "final report"

    assert (
        context.information_result
        ==
        "information"
    )

    assert (
        context.impact_result
        ==
        "impact"
    )

    assert (
        context.report_result
        ==
        "draft"
    )

    assert (
        context.evaluation_result[
            "score"
        ]
        ==
        85
    )

    assert (
        context.final_response
        ==
        "final report"
    )