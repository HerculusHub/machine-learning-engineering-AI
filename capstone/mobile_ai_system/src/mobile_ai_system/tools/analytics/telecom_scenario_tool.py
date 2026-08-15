"""
Telecom Scenario Tool

Step 11C
--------

Thin Analysis-Agent-facing wrapper around:

    TelecomScenarioService

The tool maps agent requests to the named runtime scenario
service.

Business scenario definitions remain inside the service.
"""

from __future__ import annotations

from typing import Any

from mobile_ai_system.services.analytics import (
    TelecomScenarioRequest,
    TelecomScenarioService,
)

from mobile_ai_system.tools.analytics._serialization import (
    analytics_result_to_dict,
)


class TelecomScenarioTool:
    """
    Runtime telecom-scenario simulation tool.
    """

    name = "telecom_scenario"

    description = (
        "Simulate a named telecom competitive or defensive "
        "scenario and return churn-probability impact. "
        "Results are predictive sensitivity, not causal "
        "inference."
    )

    def __init__(
        self,
        service: TelecomScenarioService,
    ) -> None:

        if service is None:

            raise ValueError(
                "TelecomScenarioTool requires a service."
            )

        if not hasattr(
            service,
            "simulate",
        ):

            raise TypeError(
                "TelecomScenarioTool service must expose "
                "simulate()."
            )

        self._service = service

    @property
    def service(
        self,
    ) -> TelecomScenarioService:

        return self._service

    def available_scenarios(
        self,
    ) -> list[str]:
        """
        Return registered scenario IDs.
        """

        if not hasattr(
            self._service,
            "available_scenarios",
        ):

            return []

        return list(
            self._service
            .available_scenarios()
        )

    def run(
        self,
        records: list[
            dict[
                str,
                Any,
            ]
        ],
        scenario_id: str,
        intensity: float = 1.0,
        segment: str | None = None,
        market_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Execute named telecom scenario.
        """

        request = (
            TelecomScenarioRequest(
                records=records,
                scenario_id=str(
                    scenario_id
                ),
                intensity=float(
                    intensity
                ),
                segment=segment,
                market_id=market_id,
            )
        )

        result = (
            self._service.simulate(
                request
            )
        )

        return analytics_result_to_dict(
            result
        )