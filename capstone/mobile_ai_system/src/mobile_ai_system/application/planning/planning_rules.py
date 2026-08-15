"""
Planning Rules

Architecture v2.3 (Frozen MVP)

Maps parser intent to execution pipelines.
"""

from __future__ import annotations

PIPELINES: dict[str, tuple[str, ...]] = {

    "analysis": (
        "information",
        "impact",
        "report",
        "evaluation",
    ),

    "comparison": (
        "information",
        "impact",
        "report",
        "evaluation",
    ),

    "summary": (
        "information",
        "report",
    ),

    "report": (
        "information",
        "report",
        "evaluation",
    ),

    "default": (
        "information",
        "report",
    ),
}