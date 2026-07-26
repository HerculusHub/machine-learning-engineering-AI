from __future__ import annotations

from dataclasses import dataclass, field

from mobile_ai_system.application.models.request_model import Request


@dataclass(slots=True)
class ParseResult:
    """
    Result produced by the RequestParser.

    Contains the normalized Request plus parser metadata.
    """

    request: Request

    confidence: float = 1.0

    parser_used: str = "rule"

    warnings: list[str] = field(default_factory=list)

    requires_clarification: bool = False