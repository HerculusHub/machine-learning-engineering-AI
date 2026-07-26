"""
Information Result

Architecture v2.3 (Frozen)

Represents the structured output produced by the Information Agent.

This object becomes the contract between

Information Agent
        ↓
Impact Analysis Agent
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class InformationResult:
    """
    Structured information collected for downstream analysis.
    """

    # Original user request
    query: str

    # Company or organization
    company: str | None = None

    # Structured evidence
    evidence: list[dict[str, Any]] = field(default_factory=list)

    # High-level summary
    summary: str = ""

    # Retrieval sources
    sources: list[str] = field(default_factory=list)

    # Confidence score
    confidence: float = 0.0

    # Additional metadata
    metadata: dict[str, Any] = field(default_factory=dict)