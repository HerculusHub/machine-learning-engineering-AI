"""
Parser Confidence

Architecture v2.3 (Frozen)

Determines parser confidence based on
how much structured information was
successfully extracted.
"""

from __future__ import annotations

from mobile_ai_system.application.models.request_model import Request


class ParserConfidence:
    """
    Computes deterministic parser confidence.

    Release 0.1
    """

    # --------------------------------------------------
    # Confidence Weights
    # --------------------------------------------------

    INTENT_WEIGHT = 0.30

    OPERATOR_WEIGHT = 0.30

    TOPIC_WEIGHT = 0.20

    EVENT_WEIGHT = 0.10

    TEXT_WEIGHT = 0.10

    MAX_SCORE = 1.0

    def score(self, request: Request) -> float:
        """
        Calculate parser confidence.

        Returns
        -------
        float
            Value between 0.0 and 1.0
        """

        score = 0.0

        if request.intent:
            score += self.INTENT_WEIGHT

        if request.operators:
            score += self.OPERATOR_WEIGHT

        if request.topics:
            score += self.TOPIC_WEIGHT

        if request.events:
            score += self.EVENT_WEIGHT

        if request.user_request.strip():
            score += self.TEXT_WEIGHT

        return min(score, self.MAX_SCORE)