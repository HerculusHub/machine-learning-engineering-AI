"""
Churn Sensitivity Tool

Step 11C
--------

Thin Analysis-Agent-facing wrapper around:

    ChurnSensitivityService

This tool exposes controlled predictive sensitivity analysis.

Important
---------
Results are NOT causal estimates.
"""

from __future__ import annotations

from typing import Any

from mobile_ai_system.services.analytics import (
    ChurnSensitivityRequest,
    ChurnSensitivityService,
)

from mobile_ai_system.tools.analytics._serialization import (
    analytics_result_to_dict,
)


class ChurnSensitivityTool:
    """
    Runtime churn-sensitivity tool.
    """

    name = "churn_sensitivity"

    description = (
        "Analyze how a controlled feature perturbation changes "
        "predicted churn probability. This is predictive model "
        "sensitivity, not causal inference."
    )

    def __init__(
        self,
        service: ChurnSensitivityService,
    ) -> None:

        if service is None:

            raise ValueError(
                "ChurnSensitivityTool requires a service."
            )

        if not hasattr(
            service,
            "analyze",
        ):

            raise TypeError(
                "ChurnSensitivityTool service must expose "
                "analyze()."
            )

        self._service = service

    @property
    def service(
        self,
    ) -> ChurnSensitivityService:

        return self._service

    def run(
        self,
        records: list[
            dict[
                str,
                Any,
            ]
        ],
        feature: str,
        change: float,
        expected_direction: str | None = None,
    ) -> dict[str, Any]:
        """
        Run predictive churn sensitivity analysis.
        """

        request = (
            ChurnSensitivityRequest(
                records=records,
                feature=str(
                    feature
                ),
                change=float(
                    change
                ),
                expected_direction=(
                    expected_direction
                ),
            )
        )

        result = (
            self._service.analyze(
                request
            )
        )

        return analytics_result_to_dict(
            result
        )