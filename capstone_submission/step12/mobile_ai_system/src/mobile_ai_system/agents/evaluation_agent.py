from __future__ import annotations

import json

from mobile_ai_system.infrastructure.logging.logger import get_logger
from .base_agent import BaseAgent
from mobile_ai_system.core.config import get_settings

settings = get_settings()

logger = get_logger(__name__)


class EvaluationAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "EvaluationAgent"

    def run(self, state: dict) -> dict:

        logger.info("%s started", self.name)

        report = state.get("report", "")

        if not report:

            logger.warning("No report found for evaluation.")

            state["evaluation_score"] = 0.0

            return state

        # =================================================
        # Obtain LLM Tool
        # =================================================

        llm = self.tools.get("llm")

        if llm is None:

            logger.warning(
                "LLMTool is unavailable. Falling back to heuristic evaluation."
            )

            score = 1.0 if len(report) > 80 else 0.5

            evaluation = {
                "score": score,
                "strengths": [],
                "weaknesses": [],
                "suggestions": [],
            }

        else:

            prompt = f"""
You are evaluating an analytical telecom report.

Evaluate the report using the following criteria:

1. Completeness
2. Accuracy
3. Logical coherence
4. Actionability
5. Overall quality

Return ONLY valid JSON in the following format:

{{
    "score": 0.0,
    "strengths": [
        "...",
        "..."
    ],
    "weaknesses": [
        "...",
        "..."
    ],
    "suggestions": [
        "...",
        "..."
    ]
}}

Report:

{report}
"""

            try:

                response = llm.generate(
                    provider=settings.evaluation_agent_provider,

                    model=settings.evaluation_agent_model,

                    prompt=prompt,

                )

                if isinstance(response, str):

                    evaluation = json.loads(response)

                elif isinstance(response, dict):

                    evaluation = response

                else:

                    raise ValueError(
                        "Unsupported LLM response type."
                    )

            except Exception as ex:

                logger.exception(
                    "LLM evaluation failed: %s",
                    ex,
                )

                evaluation = {
                    "score": 0.5,
                    "strengths": [],
                    "weaknesses": [
                        "LLM evaluation failed."
                    ],
                    "suggestions": [
                        "Retry evaluation."
                    ],
                }

        # =================================================
        # Normalize
        # =================================================

        score = float(
            evaluation.get(
                "score",
                0.5,
            )
        )

        strengths = evaluation.get(
            "strengths",
            [],
        )

        weaknesses = evaluation.get(
            "weaknesses",
            [],
        )

        suggestions = evaluation.get(
            "suggestions",
            [],
        )

        # =================================================
        # Reflection
        # =================================================

        lesson = (
            "\n".join(suggestions)
            if suggestions
            else "No improvement suggestions."
        )

        reflection = {

            "score": score,

            "strengths": strengths,

            "weaknesses": weaknesses,

            "suggestions": suggestions,

            "lesson": lesson,
        }

        reflections = state.setdefault(
            "reflections",
            [],
        )

        reflections.append(reflection)

        # =================================================
        # Save evaluation
        # =================================================

        state["evaluation"] = evaluation

        state["evaluation_score"] = score

        # =================================================
        # Save to Memory
        # =================================================

        memory = state.get("memory")

        if memory is not None:

            memory.save_reflection(

                lesson=lesson,

                source="evaluation",

                score=score,

            )

        logger.info(

            "Evaluation complete | score=%.2f",

            score,

        )

        logger.info("%s finished", self.name)

        return state