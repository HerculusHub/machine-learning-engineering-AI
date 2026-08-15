"""
Unit tests for EvaluationAgent.

Architecture v2.3 (Frozen MVP)

Tests the EvaluationAgent pipeline boundary:

    PipelineContext.report_result
        ↓
    EvaluationAgent
        ↓
    evaluation_result
    evaluation_score
    reflections
"""

from __future__ import annotations

import json

import pytest

from mobile_ai_system.agents.evaluation_agent import (
    EvaluationAgent,
)
from mobile_ai_system.application.models.pipeline_context import (
    PipelineContext,
)


class FakeLLMTool:
    """
    Deterministic fake LLM tool for EvaluationAgent tests.
    """

    def __init__(
        self,
        response,
    ) -> None:
        self.response = response
        self.calls: list[dict] = []

    def generate(
        self,
        provider: str,
        model: str,
        prompt: str,
    ):
        self.calls.append(
            {
                "provider": provider,
                "model": model,
                "prompt": prompt,
            }
        )

        return self.response


class FakeMemory:
    """
    Minimal fake memory object used to verify
    reflection persistence.
    """

    def __init__(
        self,
    ) -> None:
        self.saved_reflections: list[dict] = []

    def save_reflection(
        self,
        lesson: str,
        source: str,
        score: float,
    ) -> None:
        self.saved_reflections.append(
            {
                "lesson": lesson,
                "source": source,
                "score": score,
            }
        )


def build_context(
    report: str = "A complete analytical telecom report.",
) -> PipelineContext:
    """
    Build a PipelineContext containing a report.
    """

    return PipelineContext(
        report_result=report,
        metadata={},
    )


def build_agent_with_llm(
    response,
):
    """
    Build EvaluationAgent with FakeLLMTool.
    """

    agent = EvaluationAgent()

    fake_llm = FakeLLMTool(
        response=response,
    )

    agent.tools = {
        "llm": fake_llm,
    }

    return agent, fake_llm


def test_agent_name():
    """
    EvaluationAgent should identify itself
    as the evaluation stage.
    """

    agent = EvaluationAgent()

    assert agent.name == "evaluation"


def test_execute_with_json_llm_response():
    """
    EvaluationAgent should parse a valid
    JSON string returned by the LLM.
    """

    response = json.dumps(
        {
            "score": 0.90,
            "strengths": [
                "Clear analysis",
            ],
            "weaknesses": [
                "Limited scenario analysis",
            ],
            "suggestions": [
                "Add scenario analysis",
            ],
        }
    )

    agent, fake_llm = build_agent_with_llm(
        response=response,
    )

    context = build_context(
        report=(
            "This is a detailed telecom competitive "
            "intelligence report."
        ),
    )

    result = agent.execute(
        context,
    )

    assert result is context

    assert result.evaluation_result == {
        "score": 0.90,
        "strengths": [
            "Clear analysis",
        ],
        "weaknesses": [
            "Limited scenario analysis",
        ],
        "suggestions": [
            "Add scenario analysis",
        ],
    }

    assert result.metadata[
        "evaluation_score"
    ] == pytest.approx(
        0.90
    )

    assert len(fake_llm.calls) == 1


def test_execute_with_dict_llm_response():
    """
    EvaluationAgent should accept a dictionary
    directly from the LLM tool.
    """

    response = {
        "score": 0.85,
        "strengths": [
            "Good causal reasoning",
        ],
        "weaknesses": [],
        "suggestions": [
            "Add more financial context",
        ],
    }

    agent, fake_llm = build_agent_with_llm(
        response=response,
    )

    context = build_context()

    result = agent.execute(
        context,
    )

    assert result.evaluation_result[
        "score"
    ] == pytest.approx(
        0.85
    )

    assert result.evaluation_result[
        "strengths"
    ] == [
        "Good causal reasoning",
    ]

    assert len(fake_llm.calls) == 1


def test_execute_without_llm_uses_heuristic():
    """
    EvaluationAgent should use the Frozen MVP
    heuristic when LLMTool is unavailable.
    """

    agent = EvaluationAgent()

    agent.tools = {}

    context = build_context(
        report=(
            "A" * 100
        ),
    )

    result = agent.execute(
        context,
    )

    assert result.evaluation_result[
        "score"
    ] == pytest.approx(
        1.0
    )

    assert result.metadata[
        "evaluation_score"
    ] == pytest.approx(
        1.0
    )


def test_short_report_heuristic_score():
    """
    Short reports should receive the MVP
    heuristic score of 0.5.
    """

    agent = EvaluationAgent()

    agent.tools = {}

    context = build_context(
        report="Short report.",
    )

    result = agent.execute(
        context,
    )

    assert result.evaluation_result[
        "score"
    ] == pytest.approx(
        0.5
    )


def test_invalid_llm_response_uses_fallback():
    """
    Invalid JSON from the LLM should produce
    the deterministic evaluation fallback.
    """

    agent, fake_llm = build_agent_with_llm(
        response="not valid JSON",
    )

    context = build_context()

    result = agent.execute(
        context,
    )

    assert len(
        fake_llm.calls
    ) == 1

    assert result.evaluation_result[
        "score"
    ] == pytest.approx(
        0.5
    )

    assert result.evaluation_result[
        "weaknesses"
    ] == [
        "LLM evaluation failed."
    ]

    assert result.evaluation_result[
        "suggestions"
    ] == [
        "Retry evaluation."
    ]


def test_score_is_normalized_above_one():
    """
    Evaluation scores above 1.0 should be clamped.
    """

    agent, _ = build_agent_with_llm(
        response={
            "score": 5.0,
            "strengths": [],
            "weaknesses": [],
            "suggestions": [],
        },
    )

    result = agent.execute(
        build_context(),
    )

    assert result.evaluation_result[
        "score"
    ] == pytest.approx(
        1.0
    )


def test_score_is_normalized_below_zero():
    """
    Negative evaluation scores should be clamped.
    """

    agent, _ = build_agent_with_llm(
        response={
            "score": -3.0,
            "strengths": [],
            "weaknesses": [],
            "suggestions": [],
        },
    )

    result = agent.execute(
        build_context(),
    )

    assert result.evaluation_result[
        "score"
    ] == pytest.approx(
        0.0
    )


def test_reflection_is_added_to_metadata():
    """
    Evaluation suggestions should become
    a reflection lesson.
    """

    agent, _ = build_agent_with_llm(
        response={
            "score": 0.75,
            "strengths": [
                "Clear structure",
            ],
            "weaknesses": [
                "Limited evidence",
            ],
            "suggestions": [
                "Add more evidence",
                "Improve recommendations",
            ],
        },
    )

    context = build_context()

    result = agent.execute(
        context,
    )

    reflections = result.metadata[
        "reflections"
    ]

    assert len(
        reflections
    ) == 1

    reflection = reflections[0]

    assert reflection[
        "score"
    ] == pytest.approx(
        0.75
    )

    assert reflection[
        "strengths"
    ] == [
        "Clear structure",
    ]

    assert reflection[
        "weaknesses"
    ] == [
        "Limited evidence",
    ]

    assert reflection[
        "suggestions"
    ] == [
        "Add more evidence",
        "Improve recommendations",
    ]

    assert reflection[
        "lesson"
    ] == (
        "Add more evidence\n"
        "Improve recommendations"
    )


def test_reflection_without_suggestions():
    """
    Evaluation without suggestions should produce
    the default reflection lesson.
    """

    agent, _ = build_agent_with_llm(
        response={
            "score": 1.0,
            "strengths": [],
            "weaknesses": [],
            "suggestions": [],
        },
    )

    result = agent.execute(
        build_context(),
    )

    reflection = result.metadata[
        "reflections"
    ][0]

    assert reflection[
        "lesson"
    ] == "No improvement suggestions."


def test_reflection_is_saved_to_memory():
    """
    EvaluationAgent should persist reflection when
    a compatible memory object is present.
    """

    memory = FakeMemory()

    agent, _ = build_agent_with_llm(
        response={
            "score": 0.70,
            "strengths": [],
            "weaknesses": [],
            "suggestions": [
                "Improve financial analysis",
            ],
        },
    )

    context = PipelineContext(
        report_result="Report for memory test.",
        metadata={
            "memory": memory,
        },
    )

    agent.execute(
        context,
    )

    assert len(
        memory.saved_reflections
    ) == 1

    saved = memory.saved_reflections[
        0
    ]

    assert saved[
        "lesson"
    ] == "Improve financial analysis"

    assert saved[
        "source"
    ] == "evaluation"

    assert saved[
        "score"
    ] == pytest.approx(
        0.70
    )


def test_missing_report_returns_zero_evaluation():
    """
    Missing report should produce a zero-score
    evaluation without calling the LLM.
    """

    agent, fake_llm = build_agent_with_llm(
        response={
            "score": 1.0,
        },
    )

    context = PipelineContext()

    result = agent.execute(
        context,
    )

    assert result is context

    assert result.evaluation_result[
        "score"
    ] == pytest.approx(
        0.0
    )

    assert result.metadata[
        "evaluation_score"
    ] == pytest.approx(
        0.0
    )

    assert result.evaluation_result[
        "weaknesses"
    ] == [
        "No report available for evaluation."
    ]

    assert fake_llm.calls == []


def test_execute_preserves_report_result():
    """
    EvaluationAgent should not modify the report.
    """

    agent = EvaluationAgent()

    agent.tools = {}

    report = "Original report content."

    context = PipelineContext(
        report_result=report,
    )

    result = agent.execute(
        context,
    )

    assert result.report_result == report


def test_llm_receives_report_in_prompt():
    """
    The evaluation prompt should contain
    the complete report text.
    """

    report = (
        "Telecom churn increased because of "
        "competitor pricing pressure."
    )

    agent, fake_llm = build_agent_with_llm(
        response={
            "score": 0.80,
            "strengths": [],
            "weaknesses": [],
            "suggestions": [],
        },
    )

    agent.execute(
        build_context(
            report=report,
        ),
    )

    assert len(
        fake_llm.calls
    ) == 1

    prompt = fake_llm.calls[
        0
    ][
        "prompt"
    ]

    assert report in prompt

    assert "Completeness" in prompt
    assert "Accuracy" in prompt
    assert "Logical coherence" in prompt
    assert "Actionability" in prompt


def test_llm_receives_configured_provider_and_model():
    """
    EvaluationAgent should use its configured
    provider and model.
    """

    agent, fake_llm = build_agent_with_llm(
        response={
            "score": 0.80,
            "strengths": [],
            "weaknesses": [],
            "suggestions": [],
        },
    )

    agent.execute(
        build_context(),
    )

    assert len(
        fake_llm.calls
    ) == 1

    call = fake_llm.calls[
        0
    ]

    assert call[
        "provider"
    ] is not None

    assert call[
        "model"
    ] is not None

    assert call[
        "provider"
    ] == agent_module_settings().evaluation_agent_provider

    assert call[
        "model"
    ] == agent_module_settings().evaluation_agent_model


def agent_module_settings():
    """
    Return the exact settings object used by
    evaluation_agent.py.
    """

    from mobile_ai_system.agents import (
        evaluation_agent,
    )

    return evaluation_agent.settings