"""
Google Gemini Client

Architecture v2.3 (Frozen)

Responsibilities
----------------
- Connect to Google Gemini
- Generate text
- Lazy initialization

Does NOT
---------
- Choose models
- Build prompts
- Perform agent logic
"""

from __future__ import annotations

from google import genai

from mobile_ai_system.infrastructure.llm.base_client import BaseClient
from mobile_ai_system.core.config import get_settings

settings = get_settings()


class GoogleClient(BaseClient):

    def __init__(self):
        # Lazy initialization
        self.client = None

    # ---------------------------------------------------------
    # Internal
    # ---------------------------------------------------------

    def _ensure_client(self):

        if self.client is None:

            self.client = genai.Client(
                api_key=settings.google_api_key,
            )

    # ---------------------------------------------------------
    # Health Check
    # ---------------------------------------------------------

    def health_check(self) -> bool:
        return True

    # ---------------------------------------------------------
    # Generate
    # ---------------------------------------------------------

    def generate(
        self,
        *,
        model: str,
        prompt: str,
        temperature: float = 0.2,
    ) -> str:

        self._ensure_client()

        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                "temperature": temperature,
            },
        )

        return response.text