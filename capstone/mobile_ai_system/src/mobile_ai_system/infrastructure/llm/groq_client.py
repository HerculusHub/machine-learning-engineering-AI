"""
Groq Client.

Architecture v2.3 (Frozen)

Responsibilities
----------------
- Connect to Groq
- Execute inference
- Hide Groq SDK details

Does NOT
---------
- Select models
- Build prompts
- Perform agent logic
"""

from __future__ import annotations

from groq import Groq

from mobile_ai_system.core.config import get_settings
from mobile_ai_system.infrastructure.llm.base_client import BaseClient


settings = get_settings()


class GroqClient(BaseClient):

    def __init__(self):
        self.client = None

    # ---------------------------------------------------------
    # Lazy initialization
    # ---------------------------------------------------------

    def _ensure_client(self):

        if self.client is None:

            if not settings.groq_api_key:
                raise RuntimeError(
                    "Groq API key is not configured."
                )

            self.client = Groq(
                api_key=settings.groq_api_key,
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

        response = self.client.chat.completions.create(

            model=model,

            temperature=temperature,

            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response.choices[0].message.content