"""
Request Parser

Architecture v2.3 (Frozen)

Responsibilities
----------------
Convert raw user text into a structured Request.

Does NOT
---------
- Use an LLM
- Call external services
- Modify workflow state
"""

from __future__ import annotations

from mobile_ai_system.application.models.request_model import Request


class RequestParser:
    """
    Deterministic parser.

    Release 0.1:
    Rule-based extraction only.
    """

    OPERATORS = {
        "verizon",
        "att",
        "at&t",
        "tmobile",
        "t-mobile",
    }

    TOPICS = {
        "customer churn",
        "network quality",
        "pricing",
        "financial performance",
        "subscriber growth",
    }

    EVENTS = {
        "price increase",
        "merger",
        "outage",
        "promotion",
    }

    INTENTS = {
        "analyze": "analysis",
        "compare": "comparison",
        "summarize": "summary",
        "report": "report",
    }

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def parse(self, text: str) -> Request:
        """
        Convert raw user text into a structured Request.
        """

        normalized = text.lower()

        request = Request(
            user_request=text,
        )

        # Task type
        request.task_type = self._extract_intent(normalized)

        # Target company/operator
        operator = self._extract_operator(normalized)
        if operator:
            request.target = operator

        # Structured parameters
        topic = self._extract_topic(normalized)
        if topic:
            request.parameters["topic"] = topic

        event = self._extract_event(normalized)
        if event:
            request.parameters["event"] = event

        return request

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    def _extract_intent(self, text: str) -> str:

        for keyword, intent in self.INTENTS.items():
            if keyword in text:
                return intent

        return "analysis"

    def _extract_operator(self, text: str) -> str:

        for operator in self.OPERATORS:
            if operator in text:
                return operator

        return ""

    def _extract_topic(self, text: str):

        for topic in self.TOPICS:
            if topic in text:
                return topic

        return None

    def _extract_event(self, text: str):

        for event in self.EVENTS:
            if event in text:
                return event

        return None