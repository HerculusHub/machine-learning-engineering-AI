"""
OpenAI Client

Architecture v2.3 (Frozen)

Responsibilities
----------------
- Encapsulate all OpenAI SDK usage
- Lazily create the SDK client
- Generate text from OpenAI models

Does NOT
---------
- Select provider
- Build prompts
- Perform agent logic
"""

from __future__ import annotations

from openai import OpenAI

from mobile_ai_system.core.config import get_settings
from mobile_ai_system.infrastructure.llm.base_client import BaseClient

settings = get_settings()


class OpenAIClient(BaseClient):

    def __init__(self):

        # Lazy initialization
        self.client = None

    # ---------------------------------------------------------
    # Internal
    # ---------------------------------------------------------

    def _ensure_client(self):

        if self.client is None:

            if not settings.openai_api_key:
                raise RuntimeError(
                    "OPENAI_API_KEY is not configured."
                )

            self.client = OpenAI(
                api_key=settings.openai_api_key,
            )

    # ---------------------------------------------------------
    # Health
    # ---------------------------------------------------------

    def health_check(self) -> bool:
        return True

    # ---------------------------------------------------------
    # Generate
    # ---------------------------------------------------------

    def generate(
        self,
        *,
        prompt: str,
        model: str,
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
