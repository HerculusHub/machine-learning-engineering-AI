"""
Structured user request.

Architecture v2.3 (Frozen)

This object is the canonical representation of a user request.
Every downstream service consumes this object instead of parsing
raw user text repeatedly.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Request:

    # Original user input
    raw_text: str

    # Primary intent
    intent: str = "analysis"

    # Business entities
    operator: str | None = None
    competitor: list[str] = field(default_factory=list)

    # Business topic
    topic: str | None = None

    # Triggering event
    event: str | None = None

    # Optional timeframe
    timeframe: str | None = None

    # Extra filters
    filters: dict = field(default_factory=dict)