"""
Churn Prediction Tool

Step 11C
--------

Thin Analysis-Agent-facing wrapper around:

    ChurnPredictionService

The tool performs only:

- lightweight input validation
- request-contract construction
- service invocation
- result serialization

It performs NO model or analytical logic.
"""

from __future__ import annotations

from typing import Any

from mobile_ai_system.services.analytics import (
    ChurnPredictionRequest,
    ChurnPredictionService,
)

from mobile_ai_system.tools.analytics._serialization import (
    analytics_result_to_dict,
)


class ChurnPredictionTool:
    """
    Runtime churn-prediction tool.
    """

    name = "churn_prediction"

    description = (
        "Calculate calibrated customer churn probabilities "
        "using the runtime churn prediction service."
    )

    def __init__(
        self,
        service: ChurnPredictionService,
    ) -> None:
        """
        Initialize tool with runtime service.
        """

        if service is None:

            raise ValueError(
                "ChurnPredictionTool requires a service."
            )

        if not hasattr(
            service,
            "predict",
        ):

            raise TypeError(
                "ChurnPredictionTool service must expose "
                "predict()."
            )

        self._service = service

    @property
    def service(
        self,
    ) -> ChurnPredictionService:
        """
        Underlying runtime service.
        """

        return self._service

    def run(
        self,
        records: list[
            dict[
                str,
                Any,
            ]
        ],
        threshold: float = 0.50,
    ) -> dict[str, Any]:
        """
        Calculate calibrated churn probabilities.
        """

        request = (
            ChurnPredictionRequest(
                records=records,
                threshold=float(
                    threshold
                ),
            )
        )

        result = (
            self._service.predict(
                request
            )
        )

        return analytics_result_to_dict(
            result
        )