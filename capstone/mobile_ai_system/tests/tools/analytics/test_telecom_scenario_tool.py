"""
Tests for TelecomScenarioTool.
"""

from __future__ import annotations

from mobile_ai_system.services.analytics import (
    TelecomScenarioFeatureChange,
    TelecomScenarioRecord,
    TelecomScenarioResult,
)

from mobile_ai_system.tools.analytics import (
    TelecomScenarioTool,
)


class FakeScenarioService:

    def __init__(
        self,
    ):
        self.last_request = None

    def available_scenarios(
        self,
    ):
        return [
            "price_attack",
        ]

    def simulate(
        self,
        request,
    ):
        self.last_request = request

        return TelecomScenarioResult(
            scenario_id=request.scenario_id,
            scenario_title="Price Attack",
            category="competitive",
            description="Test scenario.",
            intensity=request.intensity,
            row_count=1,

            baseline_mean_probability=0.02,
            scenario_mean_probability=0.03,
            mean_probability_change=0.01,
            relative_probability_change=0.50,

            expected_incremental_churners=0.01,

            expected_direction="increase",
            observed_direction="increase",
            direction_validation_passed=True,

            feature_changes=[
                TelecomScenarioFeatureChange(
                    feature="price_pressure",
                    requested_change=0.1,
                    expected_direction="increase",
                )
            ],

            records=[
                TelecomScenarioRecord(
                    row_index=0,
                    baseline_probability=0.02,
                    scenario_probability=0.03,
                    probability_change=0.01,
                    relative_probability_change=0.50,
                )
            ],
        )


def test_scenario_tool_delegates():

    service = FakeScenarioService()

    tool = TelecomScenarioTool(
        service=service
    )

    result = tool.run(
        records=[
            {
                "price_pressure": 0.1,
            }
        ],
        scenario_id="price_attack",
        intensity=1.5,
    )

    assert (
        service.last_request.scenario_id
        ==
        "price_attack"
    )

    assert (
        service.last_request.intensity
        ==
        1.5
    )

    assert (
        result[
            "direction_validation_passed"
        ]
        is True
    )


def test_scenario_tool_serializes_row_records():

    tool = TelecomScenarioTool(
        service=(
            FakeScenarioService()
        )
    )

    result = tool.run(
        records=[
            {
                "price_pressure": 0.1,
            }
        ],
        scenario_id="price_attack",
    )

    assert (
        result[
            "records"
        ][
            0
        ][
            "probability_change"
        ]
        ==
        0.01
    )


def test_available_scenarios():

    tool = TelecomScenarioTool(
        service=(
            FakeScenarioService()
        )
    )

    assert (
        tool.available_scenarios()
        ==
        [
            "price_attack",
        ]
    )