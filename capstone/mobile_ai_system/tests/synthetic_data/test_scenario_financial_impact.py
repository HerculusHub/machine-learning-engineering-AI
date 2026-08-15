"""
Tests for Step-10E telecom scenario financial impact.

Validates:

- financial scenario output structure
- probability-to-churn-count identities
- revenue identities
- annualization identities
- gross-margin identities
- CLV identities
- competitive loss semantics
- defensive benefit semantics
- segment aggregation
- market aggregation
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from scripts.synthetic_data.scenario_financial_impact import (
    TelecomScenarioFinancialImpact,
)


# =============================================================
# Fixtures
# =============================================================


@pytest.fixture(scope="module")
def analyzer():
    """
    Shared financial-impact analyzer.
    """

    return TelecomScenarioFinancialImpact()


@pytest.fixture(scope="module")
def financial_output(
    analyzer,
):
    """
    Run Step-10E once for regression tests.
    """

    return analyzer.calculate()


# =============================================================
# Output structure
# =============================================================


def test_calculate_returns_expected_outputs(
    financial_output,
):
    """
    Step-10E should return result and three analytical frames.
    """

    assert {
        "result",
        "details",
        "segments",
        "markets",
    }.issubset(
        financial_output
    )

    assert isinstance(
        financial_output[
            "details"
        ],
        pd.DataFrame,
    )

    assert isinstance(
        financial_output[
            "segments"
        ],
        pd.DataFrame,
    )

    assert isinstance(
        financial_output[
            "markets"
        ],
        pd.DataFrame,
    )


def test_scenario_count(
    financial_output,
):
    """
    Financial layer should preserve all nine Step-10D
    scenarios.
    """

    assert (
        financial_output[
            "result"
        ][
            "scenario_count"
        ]
        == 9
    )


def test_financial_assumptions_valid(
    financial_output,
):
    """
    Margin and CLV horizon must be valid.
    """

    result = financial_output[
        "result"
    ]

    assert (
        0.0
        <= result[
            "gross_margin_rate"
        ]
        <= 1.0
    )

    assert (
        result[
            "clv_horizon_months"
        ]
        >
        0
    )

    assert (
        result[
            "annualization_months"
        ]
        == 12
    )


# =============================================================
# Customer-level identities
# =============================================================


def test_expected_incremental_churners_identity(
    financial_output,
):
    """
    Customer-level expected churn impact equals Δ probability.
    """

    details = financial_output[
        "details"
    ]

    assert np.allclose(
        details[
            "expected_incremental_churners"
        ].to_numpy(
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


def test_additional_and_prevented_churn_nonnegative(
    financial_output,
):
    """
    Split adverse/beneficial expected churn quantities cannot
    be negative.
    """

    details = financial_output[
        "details"
    ]

    assert (
        details[
            "expected_additional_churners"
        ]
        >= 0.0
    ).all()

    assert (
        details[
            "expected_churn_prevented"
        ]
        >= 0.0
    ).all()


def test_incremental_churn_decomposition(
    financial_output,
):
    """
    Signed incremental churn should equal:

        additional churn - prevented churn
    """

    details = financial_output[
        "details"
    ]

    expected = (
        details[
            "expected_additional_churners"
        ]
        -
        details[
            "expected_churn_prevented"
        ]
    )

    assert np.allclose(
        expected.to_numpy(
            dtype=float
        ),
        details[
            "expected_incremental_churners"
        ].to_numpy(
            dtype=float
        ),
        rtol=0.0,
        atol=1e-12,
    )


# =============================================================
# Revenue identities
# =============================================================


def test_monthly_revenue_at_risk_identity(
    financial_output,
):
    """
    Revenue at risk equals additional expected churners times
    monthly service revenue.
    """

    details = financial_output[
        "details"
    ]

    expected = (
        details[
            "expected_additional_churners"
        ]
        *
        details[
            "monthly_service_revenue"
        ]
    )

    assert np.allclose(
        expected.to_numpy(
            dtype=float
        ),
        details[
            "monthly_revenue_at_risk"
        ].to_numpy(
            dtype=float
        ),
        rtol=1e-12,
        atol=1e-10,
    )


def test_monthly_revenue_protected_identity(
    financial_output,
):
    """
    Protected revenue equals expected prevented churn times
    monthly service revenue.
    """

    details = financial_output[
        "details"
    ]

    expected = (
        details[
            "expected_churn_prevented"
        ]
        *
        details[
            "monthly_service_revenue"
        ]
    )

    assert np.allclose(
        expected.to_numpy(
            dtype=float
        ),
        details[
            "monthly_revenue_protected"
        ].to_numpy(
            dtype=float
        ),
        rtol=1e-12,
        atol=1e-10,
    )


def test_net_monthly_revenue_identity(
    financial_output,
):
    """
    Net impact is protected revenue minus revenue at risk.
    """

    details = financial_output[
        "details"
    ]

    expected = (
        details[
            "monthly_revenue_protected"
        ]
        -
        details[
            "monthly_revenue_at_risk"
        ]
    )

    assert np.allclose(
        expected.to_numpy(),
        details[
            "net_monthly_revenue_impact"
        ].to_numpy(),
        rtol=1e-12,
        atol=1e-10,
    )


def test_annualized_revenue_identity(
    financial_output,
):
    """
    Annualized revenue equals monthly net revenue × 12.
    """

    details = financial_output[
        "details"
    ]

    expected = (
        details[
            "net_monthly_revenue_impact"
        ]
        *
        12.0
    )

    assert np.allclose(
        expected.to_numpy(),
        details[
            "net_annualized_revenue_impact"
        ].to_numpy(),
        rtol=1e-12,
        atol=1e-8,
    )


# =============================================================
# Margin and CLV identities
# =============================================================


def test_gross_margin_identity(
    financial_output,
):
    """
    Annualized gross-margin impact must equal annualized
    revenue impact × configured gross margin.
    """

    result = financial_output[
        "result"
    ]

    details = financial_output[
        "details"
    ]

    margin = result[
        "gross_margin_rate"
    ]

    expected = (
        details[
            "net_annualized_revenue_impact"
        ]
        *
        margin
    )

    assert np.allclose(
        expected.to_numpy(),
        details[
            "net_annualized_gross_margin_impact"
        ].to_numpy(),
        rtol=1e-12,
        atol=1e-8,
    )


def test_clv_identity(
    financial_output,
):
    """
    Net CLV equals monthly revenue impact × gross margin ×
    CLV horizon.
    """

    result = financial_output[
        "result"
    ]

    details = financial_output[
        "details"
    ]

    multiplier = (
        result[
            "gross_margin_rate"
        ]
        *
        result[
            "clv_horizon_months"
        ]
    )

    expected = (
        details[
            "net_monthly_revenue_impact"
        ]
        *
        multiplier
    )

    assert np.allclose(
        expected.to_numpy(),
        details[
            "net_clv_impact"
        ].to_numpy(),
        rtol=1e-12,
        atol=1e-8,
    )


def test_published_clv_multiplier_identity(
    financial_output,
):
    """
    Published CLV multiplier must match margin × horizon.
    """

    result = financial_output[
        "result"
    ]

    expected = (
        result[
            "gross_margin_rate"
        ]
        *
        result[
            "clv_horizon_months"
        ]
    )

    assert np.isclose(
        expected,
        result[
            "clv_monthly_revenue_multiplier"
        ],
    )


# =============================================================
# Financial direction tests
# =============================================================


def test_competitive_scenarios_are_financial_losses(
    financial_output,
):
    """
    Accepted competitive scenarios must create negative net
    financial impact.
    """

    scenarios = financial_output[
        "result"
    ][
        "scenarios"
    ]

    competitive = [
        scenario
        for scenario in scenarios
        if scenario[
            "category"
        ]
        ==
        "competitive"
    ]

    assert competitive

    for scenario in competitive:

        assert (
            scenario[
                "financial_direction"
            ]
            ==
            "loss"
        )

        assert (
            scenario[
                "net_annualized_revenue_impact"
            ]
            <
            0.0
        )

        assert (
            scenario[
                "net_clv_impact"
            ]
            <
            0.0
        )

        assert (
            scenario[
                "monthly_revenue_at_risk"
            ]
            >
            0.0
        )


def test_defensive_scenarios_are_financial_benefits(
    financial_output,
):
    """
    Defensive scenarios must protect financial value.
    """

    scenarios = financial_output[
        "result"
    ][
        "scenarios"
    ]

    defensive = [
        scenario
        for scenario in scenarios
        if scenario[
            "category"
        ]
        ==
        "defensive"
    ]

    assert defensive

    for scenario in defensive:

        assert (
            scenario[
                "financial_direction"
            ]
            ==
            "benefit"
        )

        assert (
            scenario[
                "net_annualized_revenue_impact"
            ]
            >
            0.0
        )

        assert (
            scenario[
                "net_clv_impact"
            ]
            >
            0.0
        )

        assert (
            scenario[
                "monthly_revenue_protected"
            ]
            >
            0.0
        )


# =============================================================
# Cross-step regression identities
# =============================================================


def test_scenario_churn_totals_match_detail_rows(
    financial_output,
):
    """
    Scenario-level expected incremental churners must equal
    customer-level probability-change totals.
    """

    details = financial_output[
        "details"
    ]

    published = {
        row[
            "scenario"
        ]: row[
            "expected_incremental_churners"
        ]
        for row in (
            financial_output[
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


def test_severe_attack_is_largest_competitive_loss(
    financial_output,
):
    """
    Severe competitive attack should remain the largest
    competitive revenue-loss scenario.
    """

    competitive = [
        row
        for row in (
            financial_output[
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

    largest_loss = min(
        competitive,
        key=lambda row: row[
            "net_annualized_revenue_impact"
        ],
    )

    assert (
        largest_loss[
            "scenario"
        ]
        ==
        "severe_competitive_attack"
    )


def test_combined_defensive_response_is_largest_benefit(
    financial_output,
):
    """
    Combined defensive response should remain strongest
    financial-protection scenario.
    """

    defensive = [
        row
        for row in (
            financial_output[
                "result"
            ][
                "scenarios"
            ]
        )
        if row[
            "category"
        ]
        ==
        "defensive"
    ]

    largest = max(
        defensive,
        key=lambda row: row[
            "net_annualized_revenue_impact"
        ],
    )

    assert (
        largest[
            "scenario"
        ]
        ==
        "combined_defensive_response"
    )


# =============================================================
# Aggregation identities
# =============================================================


def test_segment_revenue_sums_to_scenario(
    financial_output,
):
    """
    Segment financial aggregation must preserve scenario
    totals.
    """

    details = financial_output[
        "details"
    ]

    segments = financial_output[
        "segments"
    ]

    detail_total = (
        details.groupby(
            "scenario",
            observed=True,
        )[
            "net_annualized_revenue_impact"
        ]
        .sum()
        .sort_index()
    )

    segment_total = (
        segments.groupby(
            "scenario",
            observed=True,
        )[
            "net_annualized_revenue_impact"
        ]
        .sum()
        .sort_index()
    )

    assert np.allclose(
        detail_total.to_numpy(),
        segment_total.to_numpy(),
        rtol=1e-10,
        atol=1e-8,
    )


def test_market_revenue_sums_to_scenario(
    financial_output,
):
    """
    Market aggregation must preserve scenario financial
    totals.
    """

    details = financial_output[
        "details"
    ]

    markets = financial_output[
        "markets"
    ]

    detail_total = (
        details.groupby(
            "scenario",
            observed=True,
        )[
            "net_annualized_revenue_impact"
        ]
        .sum()
        .sort_index()
    )

    market_total = (
        markets.groupby(
            "scenario",
            observed=True,
        )[
            "net_annualized_revenue_impact"
        ]
        .sum()
        .sort_index()
    )

    assert np.allclose(
        detail_total.to_numpy(),
        market_total.to_numpy(),
        rtol=1e-10,
        atol=1e-8,
    )


def test_segment_clv_sums_to_scenario(
    financial_output,
):
    """
    Segment CLV aggregation must preserve detailed totals.
    """

    details = financial_output[
        "details"
    ]

    segments = financial_output[
        "segments"
    ]

    detail_total = (
        details.groupby(
            "scenario",
            observed=True,
        )[
            "net_clv_impact"
        ]
        .sum()
        .sort_index()
    )

    segment_total = (
        segments.groupby(
            "scenario",
            observed=True,
        )[
            "net_clv_impact"
        ]
        .sum()
        .sort_index()
    )

    assert np.allclose(
        detail_total.to_numpy(),
        segment_total.to_numpy(),
        rtol=1e-10,
        atol=1e-8,
    )