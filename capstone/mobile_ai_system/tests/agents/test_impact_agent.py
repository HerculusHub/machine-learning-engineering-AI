"""
Unit tests for ImpactAgent.

Architecture v2.3 (Frozen MVP)
"""

from unittest.mock import MagicMock

import pytest

from mobile_ai_system.agents.impact.impact_agent import (
    ImpactAgent,
)
from mobile_ai_system.application.models.information_result import (
    InformationResult,
)
from mobile_ai_system.application.models.pipeline_context import (
    PipelineContext,
)
from mobile_ai_system.impact.models.impact_result import (
    ImpactResult,
)


def build_information_result() -> InformationResult:
    """
    Build minimal InformationResult input.
    """

    return InformationResult(
        records=[
            {
                "event_id": "EVENT-001",
                "operator_name": "Verizon",
            }
        ],
        metadata={
            "fixture": True,
        },
    )


def test_execute_calls_impact_service():
    """
    ImpactAgent should delegate analysis to ImpactService.
    """

    impact_service = MagicMock()

    impact_result = MagicMock(
        spec=ImpactResult,
    )

    impact_service.evaluate.return_value = (
        impact_result
    )

    agent = ImpactAgent(
        impact_service=impact_service,
    )

    information = build_information_result()

    context = PipelineContext(
        information_result=information,
    )

    result_context = agent.execute(
        context,
    )

    impact_service.evaluate.assert_called_once_with(
        information,
    )

    assert result_context is context


def test_execute_stores_impact_result():
    """
    ImpactAgent should store the returned ImpactResult
    in PipelineContext.impact_result.
    """

    impact_service = MagicMock()

    impact_result = MagicMock(
        spec=ImpactResult,
    )

    impact_service.evaluate.return_value = (
        impact_result
    )

    agent = ImpactAgent(
        impact_service=impact_service,
    )

    context = PipelineContext(
        information_result=build_information_result(),
    )

    result_context = agent.execute(
        context,
    )

    assert result_context.impact_result is impact_result

    assert context.impact_result is impact_result


def test_execute_preserves_information_result():
    """
    ImpactAgent should not modify InformationResult.
    """

    impact_service = MagicMock()

    impact_service.evaluate.return_value = MagicMock(
        spec=ImpactResult,
    )

    information = build_information_result()

    context = PipelineContext(
        information_result=information,
    )

    agent = ImpactAgent(
        impact_service=impact_service,
    )

    agent.execute(
        context,
    )

    assert context.information_result is information


def test_execute_without_information_raises():
    """
    ImpactAgent should reject execution when the
    Information Layer has not populated the context.
    """

    impact_service = MagicMock()

    agent = ImpactAgent(
        impact_service=impact_service,
    )

    context = PipelineContext()

    with pytest.raises(
        RuntimeError,
        match="no InformationResult",
    ):
        agent.execute(
            context,
        )

    impact_service.evaluate.assert_not_called()


def test_agent_name():
    """
    ImpactAgent should identify itself as the
    impact pipeline stage.
    """

    agent = ImpactAgent(
        impact_service=MagicMock(),
    )

    assert agent.name == "impact"