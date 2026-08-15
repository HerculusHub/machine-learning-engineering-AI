"""
Tests for ChurnPredictionService.

Step 11A
--------

These tests validate the runtime service boundary without
requiring the offline synthetic-data pipeline.

The fake model implements the same minimum persisted artifact
contract expected by the runtime service:

    feature_columns
    calibration_method
    predict_proba()
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from mobile_ai_system.services.analytics import (
    ChurnPredictionRequest,
    ChurnPredictionService,
)


class FakeCalibratedChurnModel:
    """
    Minimal runtime-compatible fake model.
    """

    feature_columns = [
        "risk_score",
        "service_calls",
    ]

    calibration_method = (
        "platt"
    )

    model_name = (
        "fake_calibrated_churn_model"
    )

    def predict_proba(
        self,
        frame: pd.DataFrame,
    ) -> np.ndarray:
        """
        Deterministic synthetic probabilities.
        """

        risk = frame[
            "risk_score"
        ].to_numpy(
            dtype=float
        )

        calls = frame[
            "service_calls"
        ].to_numpy(
            dtype=float
        )

        probability = np.clip(
            0.05
            +
            0.50
            * risk
            +
            0.02
            * calls,
            0.0,
            1.0,
        )

        return np.column_stack(
            [
                1.0
                -
                probability,
                probability,
            ]
        )


@pytest.fixture()
def model():
    """
    Fake persisted calibrated model.
    """

    return FakeCalibratedChurnModel()


@pytest.fixture()
def service(
    model,
):
    """
    Service using injected model.
    """

    return ChurnPredictionService(
        model=model
    )


def test_service_accepts_injected_model(
    service,
):
    """
    Injected models should be immediately available.
    """

    assert (
        service.is_loaded
        is True
    )


def test_requires_model_or_path():
    """
    Service cannot operate without an artifact source.
    """

    with pytest.raises(
        ValueError
    ):

        ChurnPredictionService()


def test_feature_columns(
    service,
):
    """
    Service exposes persisted feature contract.
    """

    assert (
        service.feature_columns()
        ==
        [
            "risk_score",
            "service_calls",
        ]
    )


def test_predict_frame_returns_probability_array(
    service,
):
    """
    DataFrame inference should return one probability per row.
    """

    frame = pd.DataFrame(
        {
            "risk_score": [
                0.10,
                0.50,
            ],

            "service_calls": [
                0,
                2,
            ],
        }
    )

    probabilities = (
        service.predict_frame(
            frame
        )
    )

    assert isinstance(
        probabilities,
        np.ndarray,
    )

    assert probabilities.shape == (
        2,
    )


def test_predict_frame_probabilities_bounded(
    service,
):
    """
    Returned probabilities must remain inside [0, 1].
    """

    frame = pd.DataFrame(
        {
            "risk_score": [
                0.0,
                0.4,
                1.0,
            ],

            "service_calls": [
                0,
                1,
                10,
            ],
        }
    )

    probabilities = (
        service.predict_frame(
            frame
        )
    )

    assert (
        probabilities
        >= 0.0
    ).all()

    assert (
        probabilities
        <= 1.0
    ).all()


def test_predict_frame_ignores_extra_columns(
    service,
):
    """
    Runtime application state may include additional fields.
    """

    frame = pd.DataFrame(
        {
            "customer_id": [
                "C001",
            ],

            "risk_score": [
                0.30,
            ],

            "service_calls": [
                1,
            ],

            "unused_metadata": [
                "example",
            ],
        }
    )

    probabilities = (
        service.predict_frame(
            frame
        )
    )

    assert len(
        probabilities
    ) == 1


def test_predict_frame_rejects_missing_features(
    service,
):
    """
    Persisted feature contract must be satisfied.
    """

    frame = pd.DataFrame(
        {
            "risk_score": [
                0.30,
            ],
        }
    )

    with pytest.raises(
        ValueError,
        match="missing required",
    ):

        service.predict_frame(
            frame
        )


def test_predict_frame_rejects_empty_frame(
    service,
):
    """
    Empty inference batches should be rejected.
    """

    with pytest.raises(
        ValueError
    ):

        service.predict_frame(
            pd.DataFrame()
        )


def test_structured_prediction_result(
    service,
):
    """
    Structured request should produce structured response.
    """

    request = (
        ChurnPredictionRequest(
            records=[
                {
                    "risk_score": 0.10,
                    "service_calls": 0,
                },
                {
                    "risk_score": 0.90,
                    "service_calls": 4,
                },
            ],
            threshold=0.50,
        )
    )

    result = service.predict(
        request
    )

    assert result.row_count == 2

    assert result.feature_count == 2

    assert (
        result.calibration_method
        ==
        "platt"
    )

    assert (
        result.model_name
        ==
        "fake_calibrated_churn_model"
    )


def test_structured_probability_identity(
    service,
):
    """
    Published record probabilities should equal fake-model
    calculation.
    """

    request = (
        ChurnPredictionRequest(
            records=[
                {
                    "risk_score": 0.20,
                    "service_calls": 1,
                },
            ]
        )
    )

    result = service.predict(
        request
    )

    expected = (
        0.05
        +
        0.50
        * 0.20
        +
        0.02
        * 1
    )

    assert np.isclose(
        result.predictions[
            0
        ].churn_probability,
        expected,
    )


def test_binary_prediction_uses_threshold(
    service,
):
    """
    Binary churn flag should obey requested threshold.
    """

    request = (
        ChurnPredictionRequest(
            records=[
                {
                    "risk_score": 0.90,
                    "service_calls": 4,
                },
            ],
            threshold=0.50,
        )
    )

    result = service.predict(
        request
    )

    assert (
        result.predictions[
            0
        ].predicted_churn
        is True
    )


def test_summary_probability_identities(
    service,
):
    """
    Summary min/mean/max must match record predictions.
    """

    request = (
        ChurnPredictionRequest(
            records=[
                {
                    "risk_score": 0.10,
                    "service_calls": 0,
                },
                {
                    "risk_score": 0.50,
                    "service_calls": 2,
                },
                {
                    "risk_score": 0.80,
                    "service_calls": 3,
                },
            ]
        )
    )

    result = service.predict(
        request
    )

    probabilities = np.array(
        [
            row.churn_probability
            for row in (
                result.predictions
            )
        ]
    )

    assert np.isclose(
        result.mean_churn_probability,
        probabilities.mean(),
    )

    assert np.isclose(
        result.minimum_churn_probability,
        probabilities.min(),
    )

    assert np.isclose(
        result.maximum_churn_probability,
        probabilities.max(),
    )


@pytest.mark.parametrize(
    "threshold",
    [
        -0.01,
        1.01,
    ],
)
def test_invalid_threshold_rejected(
    service,
    threshold,
):
    """
    Threshold must remain inside [0, 1].
    """

    request = (
        ChurnPredictionRequest(
            records=[
                {
                    "risk_score": 0.10,
                    "service_calls": 0,
                },
            ],
            threshold=threshold,
        )
    )

    with pytest.raises(
        ValueError
    ):

        service.predict(
            request
        )


def test_empty_request_rejected(
    service,
):
    """
    At least one record is required.
    """

    request = (
        ChurnPredictionRequest(
            records=[]
        )
    )

    with pytest.raises(
        ValueError
    ):

        service.predict(
            request
        )


def test_prediction_order_preserved(
    service,
):
    """
    Service must preserve input row order.
    """

    request = (
        ChurnPredictionRequest(
            records=[
                {
                    "risk_score": 0.8,
                    "service_calls": 0,
                },
                {
                    "risk_score": 0.1,
                    "service_calls": 0,
                },
            ]
        )
    )

    result = service.predict(
        request
    )

    assert (
        result.predictions[
            0
        ].row_index
        == 0
    )

    assert (
        result.predictions[
            1
        ].row_index
        == 1
    )

    assert (
        result.predictions[
            0
        ].churn_probability
        >
        result.predictions[
            1
        ].churn_probability
    )