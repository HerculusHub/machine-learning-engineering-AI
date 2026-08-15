"""
Tests for runtime TelecomScenarioService.

Step 11B-2
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from mobile_ai_system.services.analytics import (
    ChurnSensitivityService,
    TelecomScenarioRequest,
    TelecomScenarioService,
)


class FakeSensitivityArtifact:
    """
    Runtime-compatible fake sensitivity artifact.
    """

    feature_columns = [
        "competitor_price_pressure_3m",
        "competitor_promotion_pressure_3m",
        "competitor_network_pressure_3m",
        "customer_satisfaction_score",
        "support_calls_3m",
        "network_complaints_3m",
    ]

    competitive_features = [
        "competitor_price_pressure_3m",
        "competitor_promotion_pressure_3m",
        "competitor_network_pressure_3m",
    ]

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

        network = frame[
            "competitor_network_pressure_3m"
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

        complaints = frame[
            "network_complaints_3m"
        ].to_numpy(
            dtype=float
        )

        probability = (
            0.02
            +
            0.08 * price
            +
            0.09 * promotion
            +
            0.04 * network
            -
            0.02 * satisfaction
            +
            0.01 * support
            +
            0.012 * complaints
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


@pytest.fixture()
def sensitivity_service():
    """
    Runtime sensitivity service.
    """

    return ChurnSensitivityService(
        model=(
            FakeSensitivityArtifact()
        )
    )


@pytest.fixture()
def scenario_service(
    sensitivity_service,
):
    """
    Runtime telecom scenario service.
    """

    return TelecomScenarioService(
        sensitivity_service=(
            sensitivity_service
        )
    )


@pytest.fixture()
def records():
    """
    Complete fake sensitivity records.
    """

    return [
        {
            "competitor_price_pressure_3m": 0.10,
            "competitor_promotion_pressure_3m": 0.10,
            "competitor_network_pressure_3m": 0.10,
            "customer_satisfaction_score": 0.80,
            "support_calls_3m": 2.0,
            "network_complaints_3m": 1.0,
        },
        {
            "competitor_price_pressure_3m": 0.20,
            "competitor_promotion_pressure_3m": 0.20,
            "competitor_network_pressure_3m": 0.15,
            "customer_satisfaction_score": 0.65,
            "support_calls_3m": 3.0,
            "network_complaints_3m": 2.0,
        },
    ]


def test_available_scenarios(
    scenario_service,
):
    """
    Named scenario library should be exposed.
    """

    scenarios = (
        scenario_service
        .available_scenarios()
    )

    assert (
        "moderate_price_attack"
        in scenarios
    )

    assert (
        "severe_competitive_attack"
        in scenarios
    )

    assert (
        "service_recovery"
        in scenarios
    )


def test_moderate_price_attack_increases_churn(
    scenario_service,
    records,
):
    """
    Moderate price attack should increase churn probability.
    """

    result = (
        scenario_service.simulate(
            TelecomScenarioRequest(
                records=records,
                scenario_id=(
                    "moderate_price_attack"
                ),
            )
        )
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


def test_aggressive_price_attack_exceeds_moderate(
    scenario_service,
    records,
):
    """
    Stronger price shock should create larger response.
    """

    moderate = (
        scenario_service.simulate(
            TelecomScenarioRequest(
                records=records,
                scenario_id=(
                    "moderate_price_attack"
                ),
            )
        )
    )

    aggressive = (
        scenario_service.simulate(
            TelecomScenarioRequest(
                records=records,
                scenario_id=(
                    "aggressive_price_attack"
                ),
            )
        )
    )

    assert (
        aggressive.mean_probability_change
        >
        moderate.mean_probability_change
    )


def test_intensity_scaling(
    scenario_service,
    records,
):
    """
    Higher scenario intensity should increase impact.
    """

    standard = (
        scenario_service.simulate(
            TelecomScenarioRequest(
                records=records,
                scenario_id=(
                    "aggressive_price_attack"
                ),
                intensity=1.0,
            )
        )
    )

    stronger = (
        scenario_service.simulate(
            TelecomScenarioRequest(
                records=records,
                scenario_id=(
                    "aggressive_price_attack"
                ),
                intensity=1.5,
            )
        )
    )

    assert (
        stronger.mean_probability_change
        >
        standard.mean_probability_change
    )


def test_combined_attack_exceeds_single_attack(
    scenario_service,
    records,
):
    """
    Combined price + promotion attack should exceed
    aggressive price alone.
    """

    price = (
        scenario_service.simulate(
            TelecomScenarioRequest(
                records=records,
                scenario_id=(
                    "aggressive_price_attack"
                ),
            )
        )
    )

    combined = (
        scenario_service.simulate(
            TelecomScenarioRequest(
                records=records,
                scenario_id=(
                    "combined_competitive_attack"
                ),
            )
        )
    )

    assert (
        combined.mean_probability_change
        >
        price.mean_probability_change
    )


def test_severe_attack_positive(
    scenario_service,
    records,
):
    """
    Severe competitive scenario should increase risk.
    """

    result = (
        scenario_service.simulate(
            TelecomScenarioRequest(
                records=records,
                scenario_id=(
                    "severe_competitive_attack"
                ),
            )
        )
    )

    assert (
        result.expected_incremental_churners
        >
        0.0
    )

    assert (
        result.direction_validation_passed
        is True
    )


def test_service_recovery_reduces_churn(
    scenario_service,
    records,
):
    """
    Defensive service recovery should reduce churn.
    """

    result = (
        scenario_service.simulate(
            TelecomScenarioRequest(
                records=records,
                scenario_id=(
                    "service_recovery"
                ),
            )
        )
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


def test_expected_churn_identity(
    scenario_service,
    records,
):
    """
    Expected incremental churners = mean ΔP × row count.
    """

    result = (
        scenario_service.simulate(
            TelecomScenarioRequest(
                records=records,
                scenario_id=(
                    "promotion_blitz"
                ),
            )
        )
    )

    expected = (
        result.mean_probability_change
        *
        result.row_count
    )

    assert np.isclose(
        result.expected_incremental_churners,
        expected,
    )


def test_probabilities_bounded(
    scenario_service,
    records,
):
    """
    Mean probabilities must remain valid.
    """

    result = (
        scenario_service.simulate(
            TelecomScenarioRequest(
                records=records,
                scenario_id=(
                    "combined_competitive_attack"
                ),
            )
        )
    )

    assert (
        0.0
        <= result.baseline_mean_probability
        <= 1.0
    )

    assert (
        0.0
        <= result.scenario_mean_probability
        <= 1.0
    )


def test_feature_changes_recorded(
    scenario_service,
    records,
):
    """
    Scenario intervention audit trail should be populated.
    """

    result = (
        scenario_service.simulate(
            TelecomScenarioRequest(
                records=records,
                scenario_id=(
                    "combined_competitive_attack"
                ),
            )
        )
    )

    features = {
        row.feature
        for row in (
            result.feature_changes
        )
    }

    assert (
        "competitor_price_pressure_3m"
        in features
    )

    assert (
        "competitor_promotion_pressure_3m"
        in features
    )


def test_unknown_scenario_rejected(
    scenario_service,
    records,
):
    """
    Unknown scenario IDs must fail explicitly.
    """

    with pytest.raises(
        ValueError,
        match="Unknown telecom scenario",
    ):

        scenario_service.simulate(
            TelecomScenarioRequest(
                records=records,
                scenario_id="unknown",
            )
        )


@pytest.mark.parametrize(
    "intensity",
    [
        0.0,
        -1.0,
    ],
)
def test_nonpositive_intensity_rejected(
    scenario_service,
    records,
    intensity,
):
    """
    Scenario intensity must be positive.
    """

    with pytest.raises(
        ValueError
    ):

        scenario_service.simulate(
            TelecomScenarioRequest(
                records=records,
                scenario_id=(
                    "moderate_price_attack"
                ),
                intensity=intensity,
            )
        )


def test_empty_records_rejected(
    scenario_service,
):
    """
    Scenario request needs observations.
    """

    with pytest.raises(
        ValueError
    ):

        scenario_service.simulate(
            TelecomScenarioRequest(
                records=[],
                scenario_id=(
                    "moderate_price_attack"
                ),
            )
        )


def test_result_metadata(
    scenario_service,
    records,
):
    """
    Result explicitly preserves non-causal interpretation.
    """

    result = (
        scenario_service.simulate(
            TelecomScenarioRequest(
                records=records,
                scenario_id=(
                    "promotion_blitz"
                ),
            )
        )
    )

    assert (
        result.analysis_type
        ==
        "predictive_telecom_scenario_simulation"
    )

    assert (
        result.causal_interpretation
        is False
    )

    assert (
        result.category
        ==
        "competitive"
    )

def test_row_level_records_created(
    scenario_service,
    records,
):
    """
    TelecomScenarioService must return exactly one
    TelecomScenarioRecord per input observation.
    """

    result = scenario_service.simulate(
        TelecomScenarioRequest(
            records=records,
            scenario_id="promotion_blitz",
        )
    )

    assert (
        len(
            result.records
        )
        ==
        len(
            records
        )
    )

    assert (
        result.row_count
        ==
        len(
            result.records
        )
    )

    assert [
        row.row_index
        for row in result.records
    ] == list(
        range(
            len(
                records
            )
        )
    )


def test_row_probability_change_identity(
    scenario_service,
    records,
):
    """
    Every row must satisfy:

        probability_change
            =
        scenario_probability
            -
        baseline_probability
    """

    result = scenario_service.simulate(
        TelecomScenarioRequest(
            records=records,
            scenario_id="aggressive_price_attack",
        )
    )

    for row in result.records:

        expected = (
            row.scenario_probability
            -
            row.baseline_probability
        )

        assert np.isclose(
            row.probability_change,
            expected,
            rtol=1e-10,
            atol=1e-12,
        )


def test_row_changes_sum_to_expected_churners(
    scenario_service,
    records,
):
    """
    Population expected incremental churners must equal the
    sum of exact row-level probability changes.
    """

    result = scenario_service.simulate(
        TelecomScenarioRequest(
            records=records,
            scenario_id=(
                "combined_competitive_attack"
            ),
        )
    )

    expected = sum(
        row.probability_change
        for row in result.records
    )

    assert np.isclose(
        result.expected_incremental_churners,
        expected,
        rtol=1e-10,
        atol=1e-12,
    )


def test_row_mean_matches_published_change(
    scenario_service,
    records,
):
    """
    Published mean scenario ΔP must equal the mean of the
    exact row-level probability changes.
    """

    result = scenario_service.simulate(
        TelecomScenarioRequest(
            records=records,
            scenario_id="service_recovery",
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
        rtol=1e-10,
        atol=1e-12,
    )