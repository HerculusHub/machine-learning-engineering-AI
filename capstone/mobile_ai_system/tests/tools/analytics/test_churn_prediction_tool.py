"""
Tests for ChurnPredictionTool.
"""

from __future__ import annotations

from mobile_ai_system.services.analytics import (
    ChurnPredictionRecord,
    ChurnPredictionResult,
)

from mobile_ai_system.tools.analytics import (
    ChurnPredictionTool,
)


class FakePredictionService:

    def __init__(
        self,
    ):
        self.last_request = None

    def predict(
        self,
        request,
    ):
        self.last_request = request

        return ChurnPredictionResult(
            model_name="test_model",
            calibration_method="platt",
            feature_count=2,
            row_count=1,
            threshold=request.threshold,
            predictions=[
                ChurnPredictionRecord(
                    row_index=0,
                    churn_probability=0.25,
                    predicted_churn=False,
                )
            ],
            mean_churn_probability=0.25,
            minimum_churn_probability=0.25,
            maximum_churn_probability=0.25,
        )


def test_prediction_tool_delegates_to_service():

    service = FakePredictionService()

    tool = ChurnPredictionTool(
        service=service
    )

    result = tool.run(
        records=[
            {
                "x": 1.0,
            }
        ],
        threshold=0.40,
    )

    assert (
        service.last_request
        is not None
    )

    assert (
        service.last_request.threshold
        ==
        0.40
    )

    assert (
        result[
            "mean_churn_probability"
        ]
        ==
        0.25
    )


def test_prediction_tool_serializes_records():

    tool = ChurnPredictionTool(
        service=(
            FakePredictionService()
        )
    )

    result = tool.run(
        records=[
            {
                "x": 1.0,
            }
        ]
    )

    assert isinstance(
        result,
        dict,
    )

    assert isinstance(
        result[
            "predictions"
        ],
        list,
    )

    assert (
        result[
            "predictions"
        ][
            0
        ][
            "row_index"
        ]
        ==
        0
    )