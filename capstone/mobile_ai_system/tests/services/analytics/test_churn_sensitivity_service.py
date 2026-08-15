"""
Tests for runtime ChurnSensitivityService.

Step 11B-1

Validates:

- injected artifact lifecycle
- stable feature contract
- competitive feature contract
- baseline/scenario probability identities
- expected incremental churn identity
- direction validation
- domain clipping
- missing-feature validation
- sign-validation rejection
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from mobile_ai_system.services.analytics import (
    ChurnSensitivityRequest,
    ChurnSensitivityService,
)


class FakeSensitivityArtifact:
    """
    Minimal sensitivity-artifact contract.
    """

    feature_columns = [
        "competitor_price_pressure_3m",
        "competitor_promotion_pressure_3m",
        "customer_satisfaction_score",
        "support_calls_3m",
        "retention_offer_received",
    ]

    competitive_features = [
        "competitor_price_pressure_3m",
        "competitor_promotion_pressure_3m",
    ]

    model_name = (
        "fake_sensitivity_model"
    )

    class FakeCalibratedModel:
        calibration_method = "platt"

    calibrated_model = (
        FakeCalibratedModel()
    )

    def sign_validation(
        self,
    ):
        return {
            "passed": True,
            "failed_features": [],
        }

    def predict_proba(
        self,
        frame: pd.DataFrame,
    ) -> np.ndarray:
        """
        Deterministic monotonic fake sensitivity model.
        """

        price = frame[
            "competitor_price_pressure_3m"
        ].to_numpy(
            dtype=float
        )

        promotion = frame[
            "competitor_promotion_pressure_3m"
        ].to_numpy(
            dtype=float
        )

        satisfaction = frame[
            "customer_satisfaction_score"
        ].to_numpy(
            dtype=float
        )

        support = frame[
            "support_calls_3m"
        ].to_numpy(
            dtype=float
        )

        retention = frame[
            "retention_offer_received"
        ].astype(
            float
        ).to_numpy()

        probability = (
            0.02
            +
            0.05 * price
            +
            0.06 * promotion
            +
            0.01 * support
            -
            0.015 * satisfaction
            -
            0.01 * retention
        )

        probability = np.clip(
            probability,
            0.001,
            0.999,
        )

        return np.column_stack(
            [
                1.0 - probability,
                probability,
            ]
        )


class InvalidSignArtifact(
    FakeSensitivityArtifact
):
    """
    Artifact failing economic sign validation.
    """

    def sign_validation(
        self,
    ):
        return {
            "passed": False,
            "failed_features": [
                "competitor_price_pressure_3m",
            ],
        }


@pytest.fixture()
def model():
    return FakeSensitivityArtifact()


@pytest.fixture()
def service(
    model,
):
    return ChurnSensitivityService(
        model=model
    )


@pytest.fixture()
def records():
    return [
        {
            "competitor_price_pressure_3m": 0.10,
            "competitor_promotion_pressure_3m": 0.20,
            "customer_satisfaction_score": 0.80,
            "support_calls_3m": 1.0,
            "retention_offer_received": False,
        },
        {
            "competitor_price_pressure_3m": 0.30,
            "competitor_promotion_pressure_3m": 0.10,
            "customer_satisfaction_score": 0.60,
            "support_calls_3m": 2.0,
            "retention_offer_received": True,
        },
    ]


def test_requires_model_or_path():
    """
    Artifact source is mandatory.
    """

    with pytest.raises(
        ValueError
    ):
        ChurnSensitivityService()


def test_injected_model_loaded(
    service,
):
    """
    Injected artifact should already be loaded.
    """

    assert service.is_loaded is True


def test_feature_contract(
    service,
):
    """
    Service exposes model feature contract.
    """

    assert service.feature_columns() == [
        "competitor_price_pressure_3m",
        "competitor_promotion_pressure_3m",
        "customer_satisfaction_score",
        "support_calls_3m",
        "retention_offer_received",
    ]


def test_competitive_feature_contract(
    service,
):
    """
    Canonical competitive coordinates are exposed.
    """

    assert service.competitive_features() == [
        "competitor_price_pressure_3m",
        "competitor_promotion_pressure_3m",
    ]


def test_price_pressure_increase_raises_probability(
    service,
    records,
):
    """
    Positive price-pressure perturbation should raise churn.
    """

    request = ChurnSensitivityRequest(
        records=records,
        feature=(
            "competitor_price_pressure_3m"
        ),
        change=0.10,
        expected_direction="increase",
    )

    result = service.analyze(
        request
    )

    assert (
        result.mean_probability_change
        >
        0.0
    )

    assert (
        result.observed_direction
        ==
        "increase"
    )

    assert (
        result.direction_validation_passed
        is True
    )


def test_satisfaction_increase_reduces_probability(
    service,
    records,
):
    """
    Higher satisfaction should lower fake-model churn risk.
    """

    request = ChurnSensitivityRequest(
        records=records,
        feature=(
            "customer_satisfaction_score"
        ),
        change=0.10,
        expected_direction="decrease",
    )

    result = service.analyze(
        request
    )

    assert (
        result.mean_probability_change
        <
        0.0
    )

    assert (
        result.observed_direction
        ==
        "decrease"
    )

    assert (
        result.direction_validation_passed
        is True
    )


def test_direction_mismatch_detected(
    service,
    records,
):
    """
    Guardrail should detect incorrect business expectation.
    """

    request = ChurnSensitivityRequest(
        records=records,
        feature=(
            "competitor_price_pressure_3m"
        ),
        change=0.10,
        expected_direction="decrease",
    )

    result = service.analyze(
        request
    )

    assert (
        result.direction_validation_passed
        is False
    )


def test_no_expected_direction_returns_none(
    service,
    records,
):
    """
    Direction validation is optional.
    """

    request = ChurnSensitivityRequest(
        records=records,
        feature=(
            "competitor_price_pressure_3m"
        ),
        change=0.10,
    )

    result = service.analyze(
        request
    )

    assert (
        result.direction_validation_passed
        is None
    )


def test_probability_change_identity(
    service,
    records,
):
    """
    Row-level ΔP must equal scenario P minus baseline P.
    """

    result = service.analyze(
        ChurnSensitivityRequest(
            records=records,
            feature=(
                "competitor_promotion_pressure_3m"
            ),
            change=0.20,
        )
    )

    for row in result.records:

        assert np.isclose(
            row.probability_change,
            (
                row.scenario_probability
                -
                row.baseline_probability
            ),
        )


def test_expected_incremental_churn_identity(
    service,
    records,
):
    """
    Expected incremental churners equal sum of ΔP.
    """

    result = service.analyze(
        ChurnSensitivityRequest(
            records=records,
            feature=(
                "competitor_price_pressure_3m"
            ),
            change=0.10,
        )
    )

    expected = sum(
        row.probability_change
        for row in result.records
    )

    assert np.isclose(
        result.expected_incremental_churners,
        expected,
    )


def test_summary_mean_change_identity(
    service,
    records,
):
    """
    Mean ΔP must equal mean row-level ΔP.
    """

    result = service.analyze(
        ChurnSensitivityRequest(
            records=records,
            feature=(
                "support_calls_3m"
            ),
            change=1.0,
        )
    )

    expected = np.mean(
        [
            row.probability_change
            for row in result.records
        ]
    )

    assert np.isclose(
        result.mean_probability_change,
        expected,
    )


def test_probabilities_bounded(
    service,
    records,
):
    """
    Baseline and scenario probabilities remain valid.
    """

    result = service.analyze(
        ChurnSensitivityRequest(
            records=records,
            feature=(
                "competitor_price_pressure_3m"
            ),
            change=0.50,
        )
    )

    for row in result.records:

        assert (
            0.0
            <= row.baseline_probability
            <= 1.0
        )

        assert (
            0.0
            <= row.scenario_probability
            <= 1.0
        )


def test_unit_interval_feature_clipped(
    service,
    records,
):
    """
    Satisfaction perturbation should not exceed 1.0.
    """

    result = service.analyze(
        ChurnSensitivityRequest(
            records=records,
            feature=(
                "customer_satisfaction_score"
            ),
            change=10.0,
        )
    )

    assert (
        result.row_count
        ==
        len(
            records
        )
    )


def test_nonnegative_feature_clipped(
    service,
    records,
):
    """
    Negative competitive pressure must be clipped at zero.
    """

    result = service.analyze(
        ChurnSensitivityRequest(
            records=records,
            feature=(
                "competitor_price_pressure_3m"
            ),
            change=-100.0,
        )
    )

    assert (
        result.row_count
        ==
        len(
            records
        )
    )


def test_boolean_feature_additive_change_rejected(
    service,
    records,
):
    """
    Boolean interventions require a later explicit boolean
    scenario contract, not numeric additive sensitivity.
    """

    request = ChurnSensitivityRequest(
        records=records,
        feature="retention_offer_received",
        change=1.0,
    )

    with pytest.raises(
        ValueError,
        match="Boolean",
    ):
        service.analyze(
            request
        )


def test_missing_required_feature_rejected(
    service,
    records,
):
    """
    Input must satisfy full sensitivity-model feature
    contract.
    """

    invalid = [
        {
            key: value
            for key, value in records[
                0
            ].items()
            if key
            !=
            "support_calls_3m"
        }
    ]

    request = ChurnSensitivityRequest(
        records=invalid,
        feature=(
            "competitor_price_pressure_3m"
        ),
        change=0.1,
    )

    with pytest.raises(
        ValueError,
        match="missing required",
    ):
        service.analyze(
            request
        )


def test_unknown_sensitivity_feature_rejected(
    service,
    records,
):
    """
    Only explicit sensitivity coordinates may be changed.
    """

    request = ChurnSensitivityRequest(
        records=records,
        feature="not_a_model_feature",
        change=0.1,
    )

    with pytest.raises(
        ValueError,
        match="not part",
    ):
        service.analyze(
            request
        )


@pytest.mark.parametrize(
    "direction",
    [
        "up",
        "down",
        "positive",
    ],
)
def test_invalid_expected_direction_rejected(
    service,
    records,
    direction,
):
    """
    Expected-direction vocabulary must remain stable.
    """

    request = ChurnSensitivityRequest(
        records=records,
        feature=(
            "competitor_price_pressure_3m"
        ),
        change=0.1,
        expected_direction=direction,
    )

    with pytest.raises(
        ValueError
    ):
        service.analyze(
            request
        )


def test_empty_records_rejected(
    service,
):
    """
    Sensitivity requests require observations.
    """

    request = ChurnSensitivityRequest(
        records=[],
        feature=(
            "competitor_price_pressure_3m"
        ),
        change=0.1,
    )

    with pytest.raises(
        ValueError
    ):
        service.analyze(
            request
        )


def test_failed_sign_validation_rejected(
    records,
):
    """
    Runtime must refuse a sensitivity artifact whose fitted
    coefficient semantics failed validation.
    """

    service = (
        ChurnSensitivityService(
            model=(
                InvalidSignArtifact()
            )
        )
    )

    request = ChurnSensitivityRequest(
        records=records,
        feature=(
            "competitor_price_pressure_3m"
        ),
        change=0.1,
    )

    with pytest.raises(
        ValueError,
        match="failed sign",
    ):
        service.analyze(
            request
        )


def test_result_metadata(
    service,
    records,
):
    """
    Structured result should preserve runtime analytical
    metadata.
    """

    result = service.analyze(
        ChurnSensitivityRequest(
            records=records,
            feature=(
                "competitor_price_pressure_3m"
            ),
            change=0.1,
        )
    )

    assert (
        result.model_name
        ==
        "fake_sensitivity_model"
    )

    assert (
        result.calibration_method
        ==
        "platt"
    )

    assert (
        result.analysis_type
        ==
        "predictive_model_sensitivity"
    )

    assert (
        result.causal_interpretation
        is False
    )