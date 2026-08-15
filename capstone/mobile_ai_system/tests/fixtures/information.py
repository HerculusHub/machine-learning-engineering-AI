"""
Test fixtures for InformationResult.

Architecture v2.3 (Frozen MVP)

Reusable sample InformationResult objects used by
Impact Layer unit tests.
"""

from __future__ import annotations

from mobile_ai_system.application.models.information_result import (
    InformationResult,
)


def build_information_result() -> InformationResult:
    """
    Build a minimal InformationResult for unit tests.
    """

    result = InformationResult()

    #
    # The current MVP InformationResult may evolve.
    #
    # We therefore only populate attributes that
    # actually exist.
    #

    if hasattr(result, "records"):
        result.records = []

    if hasattr(result, "metadata"):
        result.metadata = {
            "source": "unit-test",
        }

    if hasattr(result, "query"):
        result.query = "Analyze Verizon customer churn"

    return result