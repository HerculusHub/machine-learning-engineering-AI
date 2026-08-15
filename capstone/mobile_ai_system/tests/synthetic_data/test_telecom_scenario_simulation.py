"""
Tests for Step-10D telecom scenario simulation.

Validates:

- sensitivity-model artifact compatibility
- baseline probability bounds
- scenario library
- direction guardrails
- competitive scenarios increase churn
- defensive scenarios decrease churn
- expected churner identity
- customer-level detail grain
- segment aggregation
- feature-change audit trail
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from scripts.synthetic_data.telecom_scenario_simulation import (
    TelecomScenarioSimulator,
)


# =============================================================
# Fixtures
# =============================================================


@pytest.fixture(scope="module")
def simulator():
    """
    Shared simulator.
    """

    return TelecomScenarioSimulator()


@pytest.fixture(scope="module")
def simulation_output(
    simulator,
):
    """
    Run complete Step-10D simulation once.
    """

    return simulator.simulate()


# =============================================================
# Structural tests
# =============================================================


def test_simulate_returns_expected_frames(
    simulation_output,
):
    """
    Simulator should return all Step-10D outputs.
    """

    assert {
        "result",
        "details",
        "segments",
        "feature_changes",
    }.issubset(
        simulation_output
    )

    assert isinstance(
        simulation_output[
            "details"
        ],
        pd.DataFrame,
    )

    assert isinstance(
        simulation_output[
            "segments"
        ],
        pd.DataFrame,
    )

    assert isinstance(
        simulation_output[
            "feature_changes"
        ],
        pd.DataFrame,
    )


def test_default_scenario_count(
    simulation_output,
):
    """
    Current Step-10D library contains nine scenarios.
    """

    result = simulation_output[
        "result"
    ]

    assert (
        result[
            "scenario_count"
        ]
        == 9
    )


def test_all_scenarios_direction_validated(
    simulation_output,
):
    """
    Regression guardrail: all approved scenarios should have
    correct direction.
    """

    result = simulation_output[
        "result"
    ]

    assert (
        result[
            "direction_validated_scenarios"
        ]
        ==
        result[
            "scenario_count"
        ]
    )

    assert (
        result[
            "direction_rejected_scenarios"
        ]
        == 0
    )

    assert all(
        scenario[
            "direction_validation_passed"
        ]
        for scenario in result[
            "scenarios"
        ]
    )


# =============================================================
# Probability tests
# =============================================================


def test_baseline_probability_bounded(
    simulation_output,
):
    """
    Baseline calibrated probability must be valid.
    """

    baseline = (
        simulation_output[
            "result"
        ][
            "baseline_mean_probability"
        ]
    )

    assert (
        0.0
        <= baseline
        <= 1.0
    )


def test_detail_probabilities_bounded(
    simulation_output,
):
    """
    All customer-level probabilities must remain valid.
    """

    details = simulation_output[
        "details"
    ]

    assert details[
        "baseline_probability"
    ].between(
        0.0,
        1.0,
    ).all()

    assert details[
        "scenario_probability"
    ].between(
        0.0,
        1.0,
    ).all()


def test_probability_change_identity(
    simulation_output,
):
    """
    ΔP must exactly equal scenario P - baseline P.
    """

    details = simulation_output[
        "details"
    ]

    expected = (
        details[
            "scenario_probability"
        ]
        -
        details[
            "baseline_probability"
        ]
    )

    assert np.allclose(
        expected.to_numpy(
            dtype=float
        ),
        details[
            "probability_change"
        ].to_numpy(
            dtype=float
        ),
        rtol=0.0,
        atol=1e-12,
    )


# =============================================================
# Competitive scenario direction
# =============================================================


def test_competitive_scenarios_increase_churn(
    simulation_output,
):
    """
    Every accepted competitive scenario should increase
    population-level churn probability.
    """

    scenarios = (
        simulation_output[
            "result"
        ][
            "scenarios"
        ]
    )

    competitive = [
        row
        for row in scenarios
        if row[
            "category"
        ]
        ==
        "competitive"
    ]

    assert competitive

    for row in competitive:

        assert (
            row[
                "mean_probability_change"
            ]
            >
            0.0
        )

        assert (
            row[
                "expected_incremental_churners"
            ]
            >
            0.0
        )

        assert (
            row[
                "observed_direction"
            ]
            ==
            "increase"
        )


def test_defensive_scenarios_reduce_churn(
    simulation_output,
):
    """
    Every accepted defensive scenario should reduce churn.
    """

    scenarios = (
        simulation_output[
            "result"
        ][
            "scenarios"
        ]
    )

    defensive = [
        row
        for row in scenarios
        if row[
            "category"
        ]
        ==
        "defensive"
    ]

    assert defensive

    for row in defensive:

        assert (
            row[
                "mean_probability_change"
            ]
            <
            0.0
        )

        assert (
            row[
                "expected_incremental_churners"
            ]
            <
            0.0
        )

        assert (
            row[
                "observed_direction"
            ]
            ==
            "decrease"
        )


# =============================================================
# Magnitude ordering
# =============================================================


def test_aggressive_price_attack_exceeds_moderate(
    simulation_output,
):
    """
    1-SD price shock should have larger population impact
    than 0.5-SD price shock.
    """

    lookup = {
        row[
            "scenario"
        ]: row
        for row in (
            simulation_output[
                "result"
            ][
                "scenarios"
            ]
        )
    }

    moderate = lookup[
        "moderate_price_attack"
    ]

    aggressive = lookup[
        "aggressive_price_attack"
    ]

    assert (
        aggressive[
            "mean_probability_change"
        ]
        >
        moderate[
            "mean_probability_change"
        ]
    )


def test_combined_attack_exceeds_single_price_attack(
    simulation_output,
):
    """
    Combined price + promotion should exceed isolated
    aggressive price shock.
    """

    lookup = {
        row[
            "scenario"
        ]: row
        for row in (
            simulation_output[
                "result"
            ][
                "scenarios"
            ]
        )
    }

    assert (
        lookup[
            "combined_competitive_attack"
        ][
            "mean_probability_change"
        ]
        >
        lookup[
            "aggressive_price_attack"
        ][
            "mean_probability_change"
        ]
    )


def test_severe_attack_has_largest_competitive_impact(
    simulation_output,
):
    """
    Severe multi-dimensional shock should be strongest
    competitive scenario.
    """

    competitive = [
        row
        for row in (
            simulation_output[
                "result"
            ][
                "scenarios"
            ]
        )
        if row[
            "category"
        ]
        ==
        "competitive"
    ]

    largest = max(
        competitive,
        key=lambda row: row[
            "mean_probability_change"
        ],
    )

    assert (
        largest[
            "scenario"
        ]
        ==
        "severe_competitive_attack"
    )


def test_combined_defense_stronger_than_retention_alone(
    simulation_output,
):
    """
    Combined service + retention response should protect
    more churn than retention alone.
    """

    lookup = {
        row[
            "scenario"
        ]: row
        for row in (
            simulation_output[
                "result"
            ][
                "scenarios"
            ]
        )
    }

    combined = lookup[
        "combined_defensive_response"
    ]

    retention = lookup[
        "retention_campaign"
    ]

    assert abs(
        combined[
            "mean_probability_change"
        ]
    ) > abs(
        retention[
            "mean_probability_change"
        ]
    )


# =============================================================
# Expected churner identities
# =============================================================


def test_expected_incremental_churner_identity(
    simulation_output,
):
    """
    Scenario expected churners must equal the sum of
    customer-level probability changes.
    """

    details = simulation_output[
        "details"
    ]

    published = {
        row[
            "scenario"
        ]: row[
            "expected_incremental_churners"
        ]
        for row in (
            simulation_output[
                "result"
            ][
                "scenarios"
            ]
        )
    }

    expected = (
        details.groupby(
            "scenario",
            observed=True,
        )[
            "probability_change"
        ]
        .sum()
    )

    for scenario, value in (
        expected.items()
    ):

        assert np.isclose(
            float(
                value
            ),
            float(
                published[
                    scenario
                ]
            ),
            rtol=1e-10,
            atol=1e-10,
        )


# =============================================================
# Grain / aggregation tests
# =============================================================


def test_detail_row_count(
    simulation_output,
):
    """
    Details should contain one row per population observation
    per scenario.
    """

    result = simulation_output[
        "result"
    ]

    details = simulation_output[
        "details"
    ]

    assert len(
        details
    ) == (
        result[
            "population_rows"
        ]
        *
        result[
            "scenario_count"
        ]
    )


def test_customer_month_scenario_unique(
    simulation_output,
):
    """
    Scenario detail grain should be unique.
    """

    details = simulation_output[
        "details"
    ]

    duplicate = details.duplicated(
        subset=[
            "scenario",
            "customer_id",
            "month",
            "market_id",
        ]
    )

    assert not duplicate.any()


def test_segment_expected_churners_sum_to_scenario(
    simulation_output,
):
    """
    Customer-segment aggregation must preserve scenario-level
    expected churn counts.
    """

    details = simulation_output[
        "details"
    ]

    segments = simulation_output[
        "segments"
    ]

    detail_total = (
        details.groupby(
            "scenario",
            observed=True,
        )[
            "probability_change"
        ]
        .sum()
        .sort_index()
    )

    segment_total = (
        segments.groupby(
            "scenario",
            observed=True,
        )[
            "expected_incremental_churners"
        ]
        .sum()
        .sort_index()
    )

    assert np.allclose(
        detail_total.to_numpy(),
        segment_total.to_numpy(),
        rtol=1e-10,
        atol=1e-10,
    )


# =============================================================
# Feature-change audit tests
# =============================================================


def test_feature_change_audit_not_empty(
    simulation_output,
):
    """
    Every Step-10D run should record scenario interventions.
    """

    changes = simulation_output[
        "feature_changes"
    ]

    assert not changes.empty


def test_price_attack_changes_price_pressure(
    simulation_output,
):
    """
    Price-attack scenarios must modify canonical price
    pressure coordinate.
    """

    changes = simulation_output[
        "feature_changes"
    ]

    rows = changes[
        (
            changes[
                "scenario"
            ]
            ==
            "aggressive_price_attack"
        )
        &
        (
            changes[
                "feature"
            ]
            ==
            "competitor_price_pressure_3m"
        )
    ]

    assert not rows.empty

    assert (
        float(
            rows[
                "mean_actual_change"
            ].iloc[
                0
            ]
        )
        >
        0.0
    )


def test_promotion_blitz_changes_promotion_pressure(
    simulation_output,
):
    """
    Promotion blitz must change canonical promotion pressure.
    """

    changes = simulation_output[
        "feature_changes"
    ]

    rows = changes[
        (
            changes[
                "scenario"
            ]
            ==
            "promotion_blitz"
        )
        &
        (
            changes[
                "feature"
            ]
            ==
            "competitor_promotion_pressure_3m"
        )
    ]

    assert not rows.empty

    assert (
        float(
            rows[
                "mean_actual_change"
            ].iloc[
                0
            ]
        )
        >
        0.0
    )