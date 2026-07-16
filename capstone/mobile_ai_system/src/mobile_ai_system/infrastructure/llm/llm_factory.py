"""
LLM Factory.

Architecture v2.3 (Frozen)

Creates the appropriate LLM client
according to config.py.

This is the ONLY place that knows
which provider implementation is used.
"""

from __future__ import annotations

from mobile_ai_system.core.config import get_settings

from mobile_ai_system.infrastructure.llm.google_client import GeminiClient
from mobile_ai_system.infrastructure.llm.groq_client import GroqClient
from mobile_ai_system.infrastructure.llm.openai_client import OpenAIClient


class LLMFactory:

    def __init__(self):

        self.settings = get_settings()

        self._clients = {}

    # ---------------------------------------------------------
    # Generic provider creation
    # ---------------------------------------------------------

    def client(self, provider: str):

        provider = provider.lower()

        if provider not in self._clients:

            if provider == "google":

                self._clients[provider] = GeminiClient()

            elif provider == "groq":

                self._clients[provider] = GroqClient()

            elif provider == "openai":

                self._clients[provider] = OpenAIClient()

            else:

                raise ValueError(
                    f"Unknown LLM provider: {provider}"
                )

        return self._clients[provider]

    # ---------------------------------------------------------
    # Agent helpers
    # ---------------------------------------------------------

    def information_client(self):

        return self.client(
            self.settings.information_agent_provider
        )

    def impact_client(self):

        return self.client(
            self.settings.impact_agent_provider
        )

    def report_client(self):

        return self.client(
            self.settings.report_agent_provider
        )

    def evaluation_client(self):

        return self.client(
            self.settings.evaluation_agent_provider
        )

    def supervisor_client(self):

        return self.client(
            self.settings.supervisor_agent_provider
        )