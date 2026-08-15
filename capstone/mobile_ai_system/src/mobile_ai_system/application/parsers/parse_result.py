"""
Parse Result

Architecture v2.3 (Frozen Release 0.1)

Represents the complete output of the parsing subsystem.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from mobile_ai_system.application.models.request_model import Request


@dataclass(slots=True)
class ParseResult:
    """
    Output produced by any parser implementation.
    """

    request: Request

    parser_name: str

    confidence: float = 1.0

    valid: bool = True

    warnings: list[str] = field(default_factory=list)

    errors: list[str] = field(default_factory=list)

    metadata: dict = field(default_factory=dict)