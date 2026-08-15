"""
Tests for ChurnSensitivityTool.
"""

from __future__ import annotations

from mobile_ai_system.services.analytics import (
    ChurnSensitivityRecord,
    ChurnSensitivityResult,
)

from mobile_ai_system.tools.analytics import (
    ChurnSensitivityTool,
)


class FakeSensitivityService:

    def __init__(
        self,
    ):
        self.last_request = None

    def analyze(
        self,
        request,
    ):
        self.last_request = request

        return ChurnSensitivityResult(
            model_name="sensitivity_model",
            calibration_method="platt",
            feature=request.feature,
            requested_change=request.change,
            row_count=1,
            baseline_mean_probability=0.02,
            scenario_mean_probability=0.03,
            mean_probability_change=0.01,
            relative_probability_change=0.50,
            expected_incremental_churners=0.01,
            expected_direction=(
                request.expected_direction
            ),
            observed_direction="increase",
            direction_validation_passed=True,
            records=[
                ChurnSensitivityRecord(
                    row_index=0,
                    baseline_probability=0.02,
                    scenario_probability=0.03,
                    probability_change=0.01,
                    relative_probability_change=0.50,
                )
            ],
        )


def test_sensitivity_tool_constructs_request():

    service = FakeSensitivityService()

    tool = ChurnSensitivityTool(
        service=service
    )

    result = tool.run(
        records=[
            {
                "pressure": 0.1,
            }
        ],
        feature="pressure",
        change=0.2,
        expected_direction="increase",
    )

    assert (
        service.last_request.feature
        ==
        "pressure"
    )

    assert (
        service.last_request.change
        ==
        0.2
    )

    assert (
        result[
            "observed_direction"
        ]
        ==
        "increase"
    )


def test_sensitivity_tool_preserves_noncausal_metadata():

    tool = ChurnSensitivityTool(
        service=(
            FakeSensitivityService()
        )
    )

    result = tool.run(
        records=[
            {
                "pressure": 0.1,
            }
        ],
        feature="pressure",
        change=0.1,
    )

    assert (
        result[
            "analysis_type"
        ]
        ==
        "predictive_model_sensitivity"
    )

    assert (
        result[
            "causal_interpretation"
        ]
        is False
    )
    