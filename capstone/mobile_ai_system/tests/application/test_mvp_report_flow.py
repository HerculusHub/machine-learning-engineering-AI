"""
End-to-End MVP Report Flow Tests

Architecture v2.3 (Frozen MVP)

Step 12E
--------

Purpose
-------
Verify the complete report-producing portion of the MVP:

    InformationResult
        ↓
    ImpactResult
        ↓
    ReportAgent
        ↓
    draft report
        ↓
    EvaluationAgent
        ↓
    accept OR refine once
        ↓
    PipelineContext.final_response

These tests intentionally avoid:

- MongoDB
- persisted ML artifacts
- external LLM APIs
- network access

The Information and Impact stages are represented by
deterministic handlers because their internal behavior is
already covered by their own test suites.

The real components exercised here are:

- ApplicationRunner
- PipelineContext
- ReportAgent
- EvaluationAgent
- Step 12D single-refinement orchestration
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any

import pytest

from mobile_ai_system.agents.evaluation_agent import (
    EvaluationAgent,
)
from mobile_ai_system.agents.report_agent import (
    ReportAgent,
)
from mobile_ai_system.application.models.pipeline_context import (
    PipelineContext,
)
from mobile_ai_system.application.runner import (
    ApplicationRunner,
)


# =============================================================
# Lightweight execution plan
# =============================================================


class FakeExecutionPlan:
    """
    Minimal ExecutionPlan-compatible object for integration
    testing.

    ApplicationRunner only requires:

        plan.steps
        plan.is_enabled(step_name)

    so no additional planning behavior is needed here.
    """

    def __init__(
        self,
        steps: list[str],
    ) -> None:

        self.steps = list(
            steps
        )

    def is_enabled(
        self,
        step_name: str,
    ) -> bool:
        """
        Every supplied step is enabled.
        """

        return (
            step_name
            in
            self.steps
        )


# =============================================================
# Upstream result fixtures
# =============================================================


@dataclass
class FakeInformationResult:
    """
    Minimal InformationResult-like object.

    Enough structure is provided for ReportAgent to serialize
    upstream evidence into its LLM prompt.
    """

    records: list[dict[str, Any]]

    total_records: int

    metadata: dict[str, Any]


@dataclass
class FakeImpactResult:
    """
    Minimal ImpactResult-like object.

    The real Impact Layer is independently regression-tested;
    this object represents its completed output at the report
    boundary.
    """

    churn: dict[str, Any]

    sensitivity: dict[str, Any]

    causal: dict[str, Any]

    financial: dict[str, Any]

    metadata: dict[str, Any]


# =============================================================
# Fake LLM
# =============================================================


class FakeLLM:
    """
    Deterministic queue-based LLM test double.

    Each generate() call consumes one configured response.
    """

    def __init__(
        self,
        responses: list[Any],
    ) -> None:

        self._responses = list(
            responses
        )

        self.calls: list[
            dict[str, Any]
        ] = []

    def generate(
        self,
        *,
        provider: str,
        model: str,
        prompt: str,
    ) -> Any:
        """
        Return the next configured response.
        """

        self.calls.append(
            {
                "provider": provider,
                "model": model,
                "prompt": prompt,
            }
        )

        if not self._responses:

            raise AssertionError(
                "FakeLLM received more generate() calls "
                "than expected."
            )

        return self._responses.pop(
            0
        )


# =============================================================
# Common data
# =============================================================


def build_information_result(
) -> FakeInformationResult:
    """
    Create deterministic Information Agent output.
    """

    records = [
        {
            "operator": "Competitor A",
            "event": "Aggressive price promotion",
            "market": "California",
            "importance_score": 8.5,
        },
        {
            "operator": "Competitor B",
            "event": "Network expansion",
            "market": "California",
            "importance_score": 7.8,
        },
    ]

    return FakeInformationResult(
        records=records,
        total_records=len(
            records
        ),
        metadata={
            "source": "test",
        },
    )


def build_impact_result(
) -> FakeImpactResult:
    """
    Create deterministic Impact Agent output.
    """

    return FakeImpactResult(
        churn={
            "predicted_churn_rate": 0.025,
            "confidence": 0.85,
        },

        sensitivity={
            "primary_driver": (
                "competitor pricing pressure"
            ),
        },

        causal={
            "conclusion": (
                "Causal evidence is not sufficient "
                "for a definitive claim."
            ),
        },

        financial={
            "estimated_revenue_impact": -250000.0,
        },

        metadata={
            "service": "ImpactService",
        },
    )


# =============================================================
# Pipeline handlers
# =============================================================


def information_handler(
    context: PipelineContext,
) -> PipelineContext:
    """
    Deterministic Information Agent boundary.
    """

    context.information_result = (
        build_information_result()
    )

    return context


def impact_handler(
    context: PipelineContext,
) -> PipelineContext:
    """
    Deterministic Impact Agent boundary.
    """

    assert (
        context.information_result
        is not None
    )

    context.impact_result = (
        build_impact_result()
    )

    return context


# =============================================================
# Step 12D evaluation/finalization composition
# =============================================================


def build_evaluation_handler(
    *,
    evaluation_agent: EvaluationAgent,
    report_agent: ReportAgent,
):
    """
    Build the same single-refinement composition used by
    Bootstrap Step 12D.

    This is deliberately kept in the test rather than adding
    another production module merely for orchestration tests.
    """

    def evaluate_and_finalize(
        context: PipelineContext,
    ) -> PipelineContext:
        """
        Evaluate draft and perform at most one refinement.
        """

        # -----------------------------------------------------
        # Evaluate draft
        # -----------------------------------------------------

        context = (
            evaluation_agent.execute(
                context
            )
        )

        # -----------------------------------------------------
        # Read evaluation routing decision
        # -----------------------------------------------------

        requires_refinement = bool(
            context.metadata.get(
                "requires_report_refinement",
                False,
            )
        )

        # -----------------------------------------------------
        # Passing draft
        # -----------------------------------------------------

        if not requires_refinement:

            context.metadata[
                "report_refinement_performed"
            ] = False

            context.metadata[
                "report_refinement_count"
            ] = 0

            return context

        # -----------------------------------------------------
        # Nothing to refine
        # -----------------------------------------------------

        if context.report_result is None:

            context.metadata[
                "report_refinement_performed"
            ] = False

            context.metadata[
                "report_refinement_count"
            ] = 0

            return context

        # -----------------------------------------------------
        # Exactly one refinement
        # -----------------------------------------------------

        context = (
            report_agent.refine(
                context=context,
                feedback=(
                    context.evaluation_result
                ),
            )
        )

        context.metadata[
            "report_refinement_performed"
        ] = True

        context.metadata[
            "report_refinement_count"
        ] = 1

        return context

    return evaluate_and_finalize


# =============================================================
# Runner construction
# =============================================================


def build_runner(
    *,
    report_agent: ReportAgent,
    evaluation_agent: EvaluationAgent,
) -> ApplicationRunner:
    """
    Construct the MVP pipeline used by these integration tests.
    """

    runner = ApplicationRunner()

    runner.register(
        "information",
        information_handler,
    )

    runner.register(
        "impact",
        impact_handler,
    )

    runner.register(
        "report",
        report_agent.execute,
    )

    runner.register(
        "evaluation",
        build_evaluation_handler(
            evaluation_agent=(
                evaluation_agent
            ),
            report_agent=(
                report_agent
            ),
        ),
    )

    return runner


def build_plan(
) -> FakeExecutionPlan:
    """
    Return the complete MVP execution sequence.
    """

    return FakeExecutionPlan(
        steps=[
            "information",
            "impact",
            "report",
            "evaluation",
        ]
    )


# =============================================================
# Prompt patch
# =============================================================


@pytest.fixture
def report_prompt(
    monkeypatch,
):
    """
    Replace report prompt loading with a deterministic template.

    This keeps Step 12E focused on pipeline integration rather
    than filesystem prompt loading.
    """

    template = (
        "USER REQUEST\n"
        "{user_request}\n\n"
        "INFORMATION RESULT\n"
        "{information_result}\n\n"
        "RETRIEVED EVENTS\n"
        "{retrieved_events}\n\n"
        "IMPACT RESULT\n"
        "{impact_result}\n\n"
        "Write the executive report."
    )

    monkeypatch.setattr(
        (
            "mobile_ai_system.agents."
            "report_agent.load_agent_prompts"
        ),
        lambda _: template,
    )

    return template


# =============================================================
# Branch A
# Passing draft
# =============================================================


def test_end_to_end_passing_report_becomes_final_response(
    report_prompt,
):
    """
    A report scoring at or above the quality threshold should:

        Information
            ↓
        Impact
            ↓
        Draft Report
            ↓
        Evaluation PASS
            ↓
        final_response = draft

    ReportAgent.refine() must not execute.
    """

    draft_report = (
        "Executive Telecom Competitive Intelligence Report\n\n"
        "Competitor A introduced aggressive pricing pressure "
        "in the California market. The available impact "
        "analysis indicates elevated churn risk and potential "
        "revenue exposure. Management should monitor affected "
        "segments and consider targeted retention actions."
    )

    # ---------------------------------------------------------
    # Report LLM
    #
    # Only ONE call is permitted:
    # initial report generation.
    # ---------------------------------------------------------

    report_llm = FakeLLM(
        responses=[
            draft_report,
        ]
    )

    report_agent = ReportAgent()

    report_agent.tools = {
        "llm": report_llm,
    }

    # ---------------------------------------------------------
    # Evaluation LLM
    # ---------------------------------------------------------

    evaluation_llm = FakeLLM(
        responses=[
            json.dumps(
                {
                    "score": 0.90,
                    "strengths": [
                        "Clear executive summary.",
                        "Recommendations follow the analysis.",
                    ],
                    "weaknesses": [],
                    "suggestions": [],
                }
            )
        ]
    )

    evaluation_agent = (
        EvaluationAgent()
    )

    evaluation_agent.tools = {
        "llm": evaluation_llm,
    }

    # ---------------------------------------------------------
    # Pipeline
    # ---------------------------------------------------------

    runner = build_runner(
        report_agent=report_agent,
        evaluation_agent=(
            evaluation_agent
        ),
    )

    context = PipelineContext(
        metadata={
            "user_request": (
                "Assess recent competitor activity "
                "and its impact."
            )
        }
    )

    result = runner.run(
        plan=build_plan(),
        context=context,
    )

    # ---------------------------------------------------------
    # Complete pipeline
    # ---------------------------------------------------------

    assert (
        result
        is
        context
    )

    assert (
        result.information_result
        is not None
    )

    assert (
        result.impact_result
        is not None
    )

    assert (
        result.report_result
        ==
        draft_report
    )

    assert (
        result.evaluation_result
        is not None
    )

    # ---------------------------------------------------------
    # Evaluation passed
    # ---------------------------------------------------------

    assert (
        result.evaluation_result[
            "score"
        ]
        ==
        pytest.approx(
            0.90
        )
    )

    assert (
        result.metadata[
            "requires_report_refinement"
        ]
        is False
    )

    # ---------------------------------------------------------
    # Draft becomes final
    # ---------------------------------------------------------

    assert (
        result.final_response
        ==
        draft_report
    )

    # ---------------------------------------------------------
    # Absolutely no refinement call
    # ---------------------------------------------------------

    assert (
        len(
            report_llm.calls
        )
        ==
        1
    )

    assert (
        result.metadata[
            "report_refinement_performed"
        ]
        is False
    )

    assert (
        result.metadata[
            "report_refinement_count"
        ]
        ==
        0
    )


# =============================================================
# Branch B
# Exactly one refinement
# =============================================================


def test_end_to_end_failed_report_is_refined_exactly_once(
    report_prompt,
):
    """
    A report below the quality threshold should:

        Information
            ↓
        Impact
            ↓
        Draft Report
            ↓
        Evaluation FAIL
            ↓
        ReportAgent.refine()
            ↓
        final_response

    The report LLM must be called exactly twice:

        call 1 = draft
        call 2 = refinement

    There must be no second evaluation and no recursive
    refinement.
    """

    draft_report = (
        "Competitors are increasing market pressure. "
        "The company should respond."
    )

    refined_report = (
        "Executive Telecom Competitive Intelligence Report\n\n"
        "Competitor activity indicates heightened competitive "
        "pressure in the California market, led by aggressive "
        "pricing activity and network investment. The Impact "
        "analysis indicates increased churn exposure and "
        "potential revenue risk.\n\n"
        "Recommended actions include targeted retention for "
        "high-risk customers, closer monitoring of competitor "
        "pricing, and prioritized service recovery in exposed "
        "segments. Causal conclusions should remain qualified "
        "where the available evidence is insufficient."
    )

    # ---------------------------------------------------------
    # Report LLM
    #
    # Exactly TWO responses:
    #
    # 1. initial draft
    # 2. one refinement
    # ---------------------------------------------------------

    report_llm = FakeLLM(
        responses=[
            draft_report,
            refined_report,
        ]
    )

    report_agent = ReportAgent()

    report_agent.tools = {
        "llm": report_llm,
    }

    # ---------------------------------------------------------
    # Evaluation LLM
    #
    # Exactly ONE response.
    # ---------------------------------------------------------

    evaluation_llm = FakeLLM(
        responses=[
            {
                "score": 0.60,
                "strengths": [
                    "The draft identifies competitive risk."
                ],
                "weaknesses": [
                    (
                        "The report lacks supporting impact "
                        "detail."
                    )
                ],
                "suggestions": [
                    (
                        "Add churn and financial implications "
                        "and provide more actionable "
                        "recommendations."
                    )
                ],
            }
        ]
    )

    evaluation_agent = (
        EvaluationAgent()
    )

    evaluation_agent.tools = {
        "llm": evaluation_llm,
    }

    # ---------------------------------------------------------
    # Pipeline
    # ---------------------------------------------------------

    runner = build_runner(
        report_agent=report_agent,
        evaluation_agent=(
            evaluation_agent
        ),
    )

    context = PipelineContext(
        metadata={
            "user_request": (
                "Assess competitor threats and recommend "
                "countermeasures."
            )
        }
    )

    result = runner.run(
        plan=build_plan(),
        context=context,
    )

    # ---------------------------------------------------------
    # Draft preserved
    # ---------------------------------------------------------

    assert (
        result.report_result
        ==
        draft_report
    )

    # ---------------------------------------------------------
    # Evaluation failed
    # ---------------------------------------------------------

    assert (
        result.evaluation_result[
            "score"
        ]
        ==
        pytest.approx(
            0.60
        )
    )

    assert (
        result.metadata[
            "requires_report_refinement"
        ]
        is True
    )

    # ---------------------------------------------------------
    # Refined report becomes final
    # ---------------------------------------------------------

    assert (
        result.final_response
        ==
        refined_report
    )

    assert (
        result.final_response
        !=
        result.report_result
    )

    # ---------------------------------------------------------
    # Exactly one refinement
    # ---------------------------------------------------------

    assert (
        len(
            report_llm.calls
        )
        ==
        2
    )

    assert (
        result.metadata[
            "report_refinement_performed"
        ]
        is True
    )

    assert (
        result.metadata[
            "report_refinement_count"
        ]
        ==
        1
    )

    # ---------------------------------------------------------
    # Exactly one evaluation
    #
    # Critical MVP regression:
    # refinement does NOT trigger another evaluation.
    # ---------------------------------------------------------

    assert (
        len(
            evaluation_llm.calls
        )
        ==
        1
    )


# =============================================================
# Refinement prompt integrity
# =============================================================


def test_refinement_receives_evaluator_feedback_and_upstream_evidence(
    report_prompt,
):
    """
    The single refinement call should receive:

    - original draft
    - evaluator feedback
    - InformationResult
    - ImpactResult

    This proves that refinement is evidence-aware rather than
    simply asking the LLM to rewrite blindly.
    """

    draft_report = (
        "Short initial draft."
    )

    refined_report = (
        "Complete refined executive report."
    )

    report_llm = FakeLLM(
        responses=[
            draft_report,
            refined_report,
        ]
    )

    report_agent = ReportAgent()

    report_agent.tools = {
        "llm": report_llm,
    }

    suggestion = (
        "Add financial implications and clearer "
        "countermeasures."
    )

    evaluation_llm = FakeLLM(
        responses=[
            {
                "score": 0.50,
                "strengths": [],
                "weaknesses": [
                    "Insufficient detail."
                ],
                "suggestions": [
                    suggestion
                ],
            }
        ]
    )

    evaluation_agent = (
        EvaluationAgent()
    )

    evaluation_agent.tools = {
        "llm": evaluation_llm,
    }

    runner = build_runner(
        report_agent=report_agent,
        evaluation_agent=(
            evaluation_agent
        ),
    )

    result = runner.run(
        plan=build_plan(),
        context=PipelineContext(
            metadata={
                "user_request": (
                    "Assess competitive impact."
                )
            }
        ),
    )

    assert (
        result.final_response
        ==
        refined_report
    )

    assert (
        len(
            report_llm.calls
        )
        ==
        2
    )

    refinement_prompt = (
        report_llm.calls[
            1
        ][
            "prompt"
        ]
    )

    # ---------------------------------------------------------
    # Draft
    # ---------------------------------------------------------

    assert (
        draft_report
        in
        refinement_prompt
    )

    # ---------------------------------------------------------
    # Evaluation feedback
    # ---------------------------------------------------------

    assert (
        suggestion
        in
        refinement_prompt
    )

    # ---------------------------------------------------------
    # Information evidence
    # ---------------------------------------------------------

    assert (
        "Competitor A"
        in
        refinement_prompt
    )

    # ---------------------------------------------------------
    # Impact evidence
    # ---------------------------------------------------------

    assert (
        "predicted_churn_rate"
        in
        refinement_prompt
    )

    assert (
        "estimated_revenue_impact"
        in
        refinement_prompt
    )


# =============================================================
# Final-response invariant
# =============================================================


@pytest.mark.parametrize(
    (
        "evaluation_score",
        "expected_report_calls",
    ),
    [
        (
            0.80,
            1,
        ),
        (
            0.95,
            1,
        ),
        (
            0.79,
            2,
        ),
        (
            0.20,
            2,
        ),
    ],
)
def test_completed_report_pipeline_always_produces_final_response(
    report_prompt,
    evaluation_score,
    expected_report_calls,
):
    """
    Every completed report/evaluation pipeline must produce a
    final_response.

    Scores at or above 0.80:
        accept draft

    Scores below 0.80:
        refine exactly once
    """

    draft_report = (
        "Initial telecom report with enough analytical "
        "content for integration testing."
    )

    refined_report = (
        "Refined final telecom report."
    )

    report_responses = [
        draft_report
    ]

    if (
        evaluation_score
        <
        EvaluationAgent.QUALITY_THRESHOLD
    ):

        report_responses.append(
            refined_report
        )

    report_llm = FakeLLM(
        responses=report_responses
    )

    report_agent = ReportAgent()

    report_agent.tools = {
        "llm": report_llm,
    }

    evaluation_llm = FakeLLM(
        responses=[
            {
                "score": (
                    evaluation_score
                ),
                "strengths": [],
                "weaknesses": [],
                "suggestions": [
                    (
                        "Improve report."
                    )
                ],
            }
        ]
    )

    evaluation_agent = (
        EvaluationAgent()
    )

    evaluation_agent.tools = {
        "llm": evaluation_llm,
    }

    runner = build_runner(
        report_agent=report_agent,
        evaluation_agent=(
            evaluation_agent
        ),
    )

    result = runner.run(
        plan=build_plan(),
        context=PipelineContext(),
    )

    # ---------------------------------------------------------
    # Core MVP invariant
    # ---------------------------------------------------------

    assert (
        result.final_response
        is not None
    )

    assert isinstance(
        result.final_response,
        str,
    )

    assert (
        len(
            result.final_response
        )
        >
        0
    )

    # ---------------------------------------------------------
    # Correct call count
    # ---------------------------------------------------------

    assert (
        len(
            report_llm.calls
        )
        ==
        expected_report_calls
    )

    # ---------------------------------------------------------
    # Evaluation is always exactly once
    # ---------------------------------------------------------

    assert (
        len(
            evaluation_llm.calls
        )
        ==
        1
    )