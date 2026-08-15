"""
Rule Parser

Architecture v2.3 (Frozen Release 0.1)

Responsibilities
----------------
- Deterministically extract structured information
- Canonicalize entities
- Remove duplicates

Does NOT
---------
- Call LLMs
- Call external services
- Make workflow decisions
"""

from __future__ import annotations

from mobile_ai_system.application.models.request_model import Request

from .dictionaries import (
    OPERATOR_ALIASES,
    TOPIC_ALIASES,
    EVENT_ALIASES,
)


class RuleParser:
    """
    Deterministic rule-based parser.
    """

    INTENTS = {
        "analyze": "analysis",
        "compare": "comparison",
        "summarize": "summary",
        "report": "report",
    }

    # ======================================================
    # Public API
    # ======================================================

    def parse(self, text: str) -> Request:

        normalized = text.lower()

        request = Request(
            user_request=text,
        )

        request.intent = self._extract_intent(normalized)

        request.operators = self._extract_entities(
            normalized,
            OPERATOR_ALIASES,
        )

        request.topics = self._extract_entities(
            normalized,
            TOPIC_ALIASES,
        )

        request.events = self._extract_entities(
            normalized,
            EVENT_ALIASES,
        )

        return request

    # ======================================================
    # Intent
    # ======================================================

    def _extract_intent(self, text: str) -> str:

        for keyword, intent in self.INTENTS.items():

            if keyword in text:
                return intent

        return "analysis"

    # ======================================================
    # Generic Entity Extraction
    # ======================================================

    def _extract_entities(
        self,
        text: str,
        aliases: dict[str, str],
    ) -> list[str]:
        """
        Generic entity extraction.

        Performs

        1. matching
        2. canonicalization
        3. deduplication
        """

        found = []

        seen = set()

        for alias, canonical in aliases.items():

            if alias in text:

                if canonical not in seen:

                    found.append(canonical)

                    seen.add(canonical)

        return found