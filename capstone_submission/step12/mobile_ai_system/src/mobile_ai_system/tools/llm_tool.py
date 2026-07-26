"""
LLM Tool

Architecture v2.3 (Frozen)

Responsibilities
----------------
- Provide a unified interface for all LLM providers.
- Lazily create provider clients.
- Dispatch generation requests.

Does NOT
---------
- Build prompts
- Decide which provider/model to use
"""

from __future__ import annotations

from mobile_ai_system.tools.base import BaseTool


class LLMTool(BaseTool):

    NAME = "LLMTool"

    def __init__(self):

        # Lazy initialization.
        # Clients are created only when first used.
        self.clients: dict[str, object] = {}

    # ==========================================================
    # BaseTool API
    # ==========================================================

    def connect(self) -> None:
        """
        Nothing to connect at startup.

        LLM clients are initialized lazily.
        """
        return None

    def health_check(self) -> bool:
        return True

    # ==========================================================
    # Internal
    # ==========================================================

    def _get_client(self, provider: str):

        provider = provider.lower()

        # Already created
        if provider in self.clients:
            return self.clients[provider]

        # Import ONLY when needed.
        # This avoids requiring every SDK/API key
        # during startup or testing.

        if provider == "google":

            from mobile_ai_system.infrastructure.llm.google_client import (
                GoogleClient,
            )

            self.clients[provider] = GoogleClient()

        elif provider == "groq":

            from mobile_ai_system.infrastructure.llm.groq_client import (
                GroqClient,
            )

            self.clients[provider] = GroqClient()

        elif provider == "openai":

            from mobile_ai_system.infrastructure.llm.openai_client import (
                OpenAIClient,
            )

            self.clients[provider] = OpenAIClient()

        else:

            raise ValueError(
                f"Unsupported LLM provider: {provider}"
            )

        return self.clients[provider]

    # ==========================================================
    # Public API
    # ==========================================================

    def generate(
        self,
        *,
        provider: str,
        model: str,
        prompt: str,
        temperature: float = 0.2,
    ) -> str:

        client = self._get_client(provider)

        return client.generate(
            model=model,
            prompt=prompt,
            temperature=temperature,
        )

    # ==========================================================
    # Execute
    # ==========================================================

    def execute(self, *args, **kwargs):

        return self.generate(*args, **kwargs)