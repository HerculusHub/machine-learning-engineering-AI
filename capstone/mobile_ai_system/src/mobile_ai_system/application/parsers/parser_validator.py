"""
Parser Validator

Architecture v2.3 (Frozen Release 0.1)
"""

from __future__ import annotations

from mobile_ai_system.application.models.request_model import Request


class ParserValidator:
    """
    Validate parsed requests.

    Release 0.1:
        Basic structural validation.
    """

    def validate(
        self,
        request: Request,
    ) -> tuple[bool, list[str], list[str]]:

        warnings = []
        errors = []

        if not request.user_request.strip():

            errors.append(
                "Empty user request."
            )

        if not request.operators:

            warnings.append(
                "No telecom operator detected."
            )

        if not request.topics:

            warnings.append(
                "No analysis topic detected."
            )

        valid = len(errors) == 0

        return (
            valid,
            warnings,
            errors,
        )