
"""
Unit tests for ReportAgent.

Architecture v2.3 (Frozen MVP)

Tests the ReportAgent pipeline boundary:

    InformationResult
        +
    ImpactResult
        ↓
    ReportAgent
        ↓
    LLM Tool
        ↓
    PipelineContext.report_result
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from mobile_ai_system.agents.report_agent import (
    ReportAgent,
)
from mobile_ai_system.application.models.information_result import (
    InformationResult,
)
from mobile_ai_system.application.models.pipeline_context import (
    PipelineContext,
)
from mobile_ai_system.impact.models.causal_result import (
    CausalResult,
)
from mobile_ai_system.impact.models.churn_result import (
    ChurnResult,
)
from mobile_ai_system.impact.models.feature_vector import (
    FeatureVector,
)
from mobile_ai_system.impact.models.financial_result import (
    FinancialResult,
)
from mobile_ai_system.impact.models.impact_result import (
    ImpactResult,
)
from mobile_ai_system.impact.models.sensitivity_result import (
    SensitivityResult,
)


class FakeLLMTool:
    """
    Minimal fake LLM tool used by ReportAgent tests.
    """

    def __init__(
        self,
        response: str = "Generated executive report.",
    ) -> None:
        self.response = response

        self.calls: list[dict] = []

    def generate(
        self,
        provider: str,
        model: str,
        prompt: str,
    ) -> str:
        """
        Simulate report generation.
        """

        self.calls.append(
            {
                "provider": provider,
                "model": model,
                "prompt": prompt,
            }
        )

        return self.response


def build_information_result() -> InformationResult:
    """
    Build minimal InformationResult input.
    """

    return InformationResult(
        records=[
            {
                "event_id": "EVENT-001",
                "operator_name": "Verizon",
                "event_category": "pricing",
                "key_points": [
                    "Competitor reduced prices."
                ],
            },
            {
                "event_id": "EVENT-002",
                "operator_name": "AT&T",
                "event_category": "promotion",
                "key_points": [
                    "Competitor launched a promotion."
                ],
            },
        ],
        metadata={
            "fixture": "report-agent",
        },
    )


def build_impact_result() -> ImpactResult:
    """
    Build minimal typed ImpactResult input.
    """

    churn = ChurnResult(
        predicted_churn_rate=0.10,
        confidence=0.80,
        feature_vector=FeatureVector(
            features={
                "event_count": 2.0,
            },
            metadata={
                "fixture": True,
            },
        ),
        metadata={
            "model": "test_churn_model",
        },
    )

    sensitivity = SensitivityResult(
        features=[],
        model_name="test_churn_model",
        metadata={
            "fixture": True,
        },
    )

    causal = CausalResult(
        confidence=0.75,
        metadata={
            "fixture": True,
        },
    )

    financial = FinancialResult(
        predicted_churn_rate=0.10,
        lost_customers=100_000.0,
        monthly_revenue_loss=6_000_000.0,
        annual_revenue_loss=72_000_000.0,
        monthly_profit_loss=2_100_000.0,
        annual_profit_loss=25_200_000.0,
        market_share_loss=0.10,
        customer_base=1_000_000,
        arpu=60.0,
        gross_margin=0.35,
        confidence=0.75,
        metadata={
            "fixture": True,
        },
    )

    return ImpactResult(
        churn=churn,
        sensitivity=sensitivity,
        causal=causal,
        financial=financial,
        metadata={
            "fixture": True,
        },
    )


def build_context() -> PipelineContext:
    """
    Build a valid reporting pipeline context.
    """

    return PipelineContext(
        information_result=build_information_result(),
        impact_result=build_impact_result(),
        metadata={
            "user_request": (
                "Analyze competitor impact on customer churn."
            ),
        },
    )


def build_agent_with_llm(
    response: str = "Generated executive report.",
):
    """
    Build ReportAgent with a fake LLM tool.

    ReportAgent currently retrieves tools from ``self.tools``.
    The unit test injects the minimal tool collection required
    by that contract.
    """

    agent = ReportAgent()

    fake_llm = FakeLLMTool(
        response=response,
    )

    agent.tools = {
        "llm": fake_llm,
    }

    return agent, fake_llm


def test_agent_name():
    """
    ReportAgent should identify itself as the report stage.
    """

    agent = ReportAgent()

    assert agent.name == "report"


def test_execute_generates_report():
    """
    ReportAgent should call the configured LLM tool and
    store its output in report_result.
    """

    agent, fake_llm = build_agent_with_llm(
        response="Executive telecom impact report."
    )

    context = build_context()

    with patch(
        "mobile_ai_system.agents.report_agent.load_agent_prompts",
        return_value=(
            "Request: {user_request}\n"
            "Events: {retrieved_events}\n"
            "Impact: {impact_result}"
        ),
    ):
        result = agent.execute(
            context,
        )

    assert result is context

    assert result.report_result == (
        "Executive telecom impact report."
    )

    assert len(fake_llm.calls) == 1


def test_execute_passes_information_and_impact_to_prompt():
    """
    Generated prompt should contain Information and Impact
    Layer outputs.
    """

    agent, fake_llm = build_agent_with_llm()

    context = build_context()

    with patch(
        "mobile_ai_system.agents.report_agent.load_agent_prompts",
        return_value=(
            "REQUEST={user_request}\n"
            "EVENTS={retrieved_events}\n"
            "IMPACT={impact_result}"
        ),
    ):
        agent.execute(
            context,
        )

    assert len(fake_llm.calls) == 1

    prompt = fake_llm.calls[0][
        "prompt"
    ]

    assert (
        "Analyze competitor impact on customer churn."
        in prompt
    )

    assert "EVENT-001" in prompt

    assert "EVENT-002" in prompt

    assert "predicted_churn_rate" in prompt


def test_execute_preserves_pipeline_results():
    """
    ReportAgent should not replace InformationResult or
    ImpactResult.
    """

    agent, _ = build_agent_with_llm()

    context = build_context()

    information = context.information_result
    impact = context.impact_result

    with patch(
        "mobile_ai_system.agents.report_agent.load_agent_prompts",
        return_value=(
            "{user_request}\n"
            "{retrieved_events}\n"
            "{impact_result}"
        ),
    ):
        result = agent.execute(
            context,
        )

    assert result.information_result is information

    assert result.impact_result is impact


def test_execute_without_information_raises():
    """
    Reporting must not execute before InformationResult exists.
    """

    agent, fake_llm = build_agent_with_llm()

    context = PipelineContext(
        impact_result=build_impact_result(),
    )

    with pytest.raises(
        RuntimeError,
        match="no InformationResult",
    ):
        agent.execute(
            context,
        )

    assert fake_llm.calls == []


def test_execute_without_impact_raises():
    """
    Reporting must not execute before ImpactResult exists.
    """

    agent, fake_llm = build_agent_with_llm()

    context = PipelineContext(
        information_result=build_information_result(),
    )

    with pytest.raises(
        RuntimeError,
        match="no ImpactResult",
    ):
        agent.execute(
            context,
        )

    assert fake_llm.calls == []


def test_execute_without_llm_uses_fallback():
    """
    Frozen MVP should produce a deterministic fallback
    when no LLM tool is available.
    """

    agent = ReportAgent()

    agent.tools = {}

    context = build_context()

    with patch(
        "mobile_ai_system.agents.report_agent.load_agent_prompts",
        return_value=(
            "{user_request}\n"
            "{retrieved_events}\n"
            "{impact_result}"
        ),
    ):
        result = agent.execute(
            context,
        )

    assert result.report_result == "LLM unavailable."


def test_llm_receives_configured_provider_and_model():
    """
    ReportAgent should use configured report-agent
    provider and model settings.
    """

    agent, fake_llm = build_agent_with_llm()

    context = build_context()

    with patch(
        "mobile_ai_system.agents.report_agent.load_agent_prompts",
        return_value=(
            "{user_request}\n"
            "{retrieved_events}\n"
            "{impact_result}"
        ),
    ):
        agent.execute(
            context,
        )

    call = fake_llm.calls[0]

    assert call["provider"] is not None

    assert call["provider"] == (
        agent_module_settings().report_agent_provider
    )

    assert call["model"] == (
        agent_module_settings().report_agent_model
    )


def agent_module_settings():
    """
    Return the settings object used by report_agent.py.

    Importing through the module ensures this test checks
    the same settings instance used by ReportAgent.
    """

    from mobile_ai_system.agents import report_agent

    return report_agent.settings
