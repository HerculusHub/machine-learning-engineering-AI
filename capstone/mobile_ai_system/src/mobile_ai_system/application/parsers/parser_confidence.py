"""
Parser Confidence

Architecture v2.3 (Frozen Release 0.1)

Responsibilities
----------------
Estimate confidence of deterministic parsing.

Does NOT
---------
Use LLMs.
Modify requests.
Validate business logic.
"""

from __future__ import annotations

from mobile_ai_system.application.models.request_model import Request


class ParserConfidence:
    """
    Computes confidence for a parsed request.

    Release 0.1:
        Rule-based heuristic.

    Future:
        Statistical model
        ML classifier
        LLM confidence fusion
    """

    def score(self, request: Request) -> float:

        score = 0.0

        # Intent

        if request.intent:
            score += 0.30

        # Operator

        if request.operators:
            score += 0.30

        # Topic

        if request.topics:
            score += 0.20

        # Event

        if request.events:
            score += 0.10

        # User supplied some text

        if request.user_request.strip():
            score += 0.10

        return min(score, 1.0)