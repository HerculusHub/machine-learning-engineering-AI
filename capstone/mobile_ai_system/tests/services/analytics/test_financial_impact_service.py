"""
Tests for runtime FinancialImpactService.

Step 11B-3
"""

from __future__ import annotations

import numpy as np
import pytest

from mobile_ai_system.services.analytics import (
    FinancialImpactCustomer,
    FinancialImpactRequest,
    FinancialImpactService,
    TelecomScenarioRecord,
    TelecomScenarioResult,
)


@pytest.fixture()
def service():
    """
    Financial-impact service.
    """

    return FinancialImpactService()


def make_scenario(
    *,
    incremental_churners: float,
    row_count: int = 2,
    category: str = "competitive",
) -> TelecomScenarioResult:
    """
    Build minimal valid telecom scenario result.
    """

    direction = (
        "increase"
        if incremental_churners > 0.0
        else "decrease"
    )

    return TelecomScenarioResult(
        scenario_id="test_scenario",
        scenario_title="Test Scenario",
        category=category,
        description="Test scenario.",
        intensity=1.0,
        row_count=row_count,
        baseline_mean_probability=0.02,
        scenario_mean_probability=(
            0.02
            +
            incremental_churners
            /
            row_count
        ),
        mean_probability_change=(
            incremental_churners
            /
            row_count
        ),
        relative_probability_change=0.10,
        expected_incremental_churners=(
            incremental_churners
        ),
        expected_direction=direction,
        observed_direction=direction,
        direction_validation_passed=True,
        feature_changes=[],
    )


@pytest.fixture()
def financials():
    """
    Two-customer financial population.
    """

    return [
        FinancialImpactCustomer(
            row_index=0,
            monthly_service_revenue=100.0,
            customer_segment="premium",
            market_id="M1",
        ),
        FinancialImpactCustomer(
            row_index=1,
            monthly_service_revenue=200.0,
            customer_segment="standard",
            market_id="M2",
        ),
    ]


def test_competitive_scenario_is_loss(
    service,
    financials,
):
    """
    Positive incremental churn should create financial loss.
    """

    result = service.calculate(
        FinancialImpactRequest(
            scenario_result=(
                make_scenario(
                    incremental_churners=0.30,
                )
            ),
            customer_financials=financials,
        )
    )

    assert (
        result.financial_direction
        ==
        "loss"
    )

    assert (
        result.net_monthly_revenue_impact
        <
        0.0
    )

    assert (
        result.net_annualized_revenue_impact
        <
        0.0
    )

    assert (
        result.net_clv_impact
        <
        0.0
    )


def test_defensive_scenario_is_benefit(
    service,
    financials,
):
    """
    Negative incremental churn should protect value.
    """

    scenario = (
        make_scenario(
            incremental_churners=-0.30,
            category="defensive",
        )
    )

    result = service.calculate(
        FinancialImpactRequest(
            scenario_result=scenario,
            customer_financials=financials,
        )
    )

    assert (
        result.financial_direction
        ==
        "benefit"
    )

    assert (
        result.net_monthly_revenue_impact
        >
        0.0
    )

    assert (
        result.net_clv_impact
        >
        0.0
    )


def test_incremental_churn_identity(
    service,
    financials,
):
    """
    Row-level allocated churn totals must preserve scenario
    aggregate.
    """

    scenario = make_scenario(
        incremental_churners=0.30,
    )

    result = service.calculate(
        FinancialImpactRequest(
            scenario_result=scenario,
            customer_financials=financials,
        )
    )

    expected = sum(
        row.expected_incremental_churners
        for row in result.records
    )

    assert np.isclose(
        expected,
        scenario.expected_incremental_churners,
    )

    assert np.isclose(
        result.expected_incremental_churners,
        scenario.expected_incremental_churners,
    )


def test_additional_churn_nonnegative(
    service,
    financials,
):
    """
    Adverse scenario should produce only additional churn.
    """

    result = service.calculate(
        FinancialImpactRequest(
            scenario_result=(
                make_scenario(
                    incremental_churners=0.30,
                )
            ),
            customer_financials=financials,
        )
    )

    assert (
        result.expected_additional_churners
        >= 0.0
    )

    assert np.isclose(
        result.expected_churn_prevented,
        0.0,
    )


def test_prevented_churn_nonnegative(
    service,
    financials,
):
    """
    Defensive scenario should produce churn prevented.
    """

    result = service.calculate(
        FinancialImpactRequest(
            scenario_result=(
                make_scenario(
                    incremental_churners=-0.30,
                    category="defensive",
                )
            ),
            customer_financials=financials,
        )
    )

    assert (
        result.expected_churn_prevented
        >= 0.0
    )

    assert np.isclose(
        result.expected_additional_churners,
        0.0,
    )


def test_monthly_revenue_identity(
    service,
    financials,
):
    """
    Net monthly impact equals protected minus at-risk
    revenue.
    """

    result = service.calculate(
        FinancialImpactRequest(
            scenario_result=(
                make_scenario(
                    incremental_churners=0.30,
                )
            ),
            customer_financials=financials,
        )
    )

    expected = (
        result.monthly_revenue_protected
        -
        result.monthly_revenue_at_risk
    )

    assert np.isclose(
        result.net_monthly_revenue_impact,
        expected,
    )


def test_annualization_identity(
    service,
    financials,
):
    """
    Annualized impact equals monthly impact × months.
    """

    result = service.calculate(
        FinancialImpactRequest(
            scenario_result=(
                make_scenario(
                    incremental_churners=0.30,
                )
            ),
            customer_financials=financials,
            annualization_months=12,
        )
    )

    assert np.isclose(
        result.net_annualized_revenue_impact,
        (
            result.net_monthly_revenue_impact
            *
            12.0
        ),
    )


def test_gross_margin_identity(
    service,
    financials,
):
    """
    Margin impact equals annualized revenue × margin rate.
    """

    result = service.calculate(
        FinancialImpactRequest(
            scenario_result=(
                make_scenario(
                    incremental_churners=0.30,
                )
            ),
            customer_financials=financials,
            gross_margin_rate=0.35,
        )
    )

    assert np.isclose(
        result.net_annualized_gross_margin_impact,
        (
            result.net_annualized_revenue_impact
            *
            0.35
        ),
    )


def test_clv_identity(
    service,
    financials,
):
    """
    CLV impact equals monthly impact × margin × horizon.
    """

    result = service.calculate(
        FinancialImpactRequest(
            scenario_result=(
                make_scenario(
                    incremental_churners=0.30,
                )
            ),
            customer_financials=financials,
            gross_margin_rate=0.35,
            clv_horizon_months=24,
        )
    )

    assert np.isclose(
        result.net_clv_impact,
        (
            result.net_monthly_revenue_impact
            *
            0.35
            *
            24.0
        ),
    )


def test_segment_aggregation(
    service,
    financials,
):
    """
    Segment results should preserve both segment labels.
    """

    result = service.calculate(
        FinancialImpactRequest(
            scenario_result=(
                make_scenario(
                    incremental_churners=0.30,
                )
            ),
            customer_financials=financials,
        )
    )

    groups = {
        row.group_value
        for row in (
            result.segment_results
        )
    }

    assert groups == {
        "premium",
        "standard",
    }


def test_market_aggregation(
    service,
    financials,
):
    """
    Market results should preserve market labels.
    """

    result = service.calculate(
        FinancialImpactRequest(
            scenario_result=(
                make_scenario(
                    incremental_churners=0.30,
                )
            ),
            customer_financials=financials,
        )
    )

    groups = {
        row.group_value
        for row in (
            result.market_results
        )
    }

    assert groups == {
        "M1",
        "M2",
    }


def test_segment_totals_match_result(
    service,
    financials,
):
    """
    Segment financial totals must sum to population total.
    """

    result = service.calculate(
        FinancialImpactRequest(
            scenario_result=(
                make_scenario(
                    incremental_churners=0.30,
                )
            ),
            customer_financials=financials,
        )
    )

    total = sum(
        row.net_annualized_revenue_impact
        for row in (
            result.segment_results
        )
    )

    assert np.isclose(
        total,
        result.net_annualized_revenue_impact,
    )


def test_market_totals_match_result(
    service,
    financials,
):
    """
    Market financial totals must sum to population total.
    """

    result = service.calculate(
        FinancialImpactRequest(
            scenario_result=(
                make_scenario(
                    incremental_churners=0.30,
                )
            ),
            customer_financials=financials,
        )
    )

    total = sum(
        row.net_clv_impact
        for row in (
            result.market_results
        )
    )

    assert np.isclose(
        total,
        result.net_clv_impact,
    )


def test_financial_row_count_must_match_scenario(
    service,
):
    """
    Scenario population and financial population must align.
    """

    scenario = make_scenario(
        incremental_churners=0.30,
        row_count=2,
    )

    financials = [
        FinancialImpactCustomer(
            row_index=0,
            monthly_service_revenue=100.0,
        )
    ]

    with pytest.raises(
        ValueError,
        match="count must match",
    ):

        service.calculate(
            FinancialImpactRequest(
                scenario_result=scenario,
                customer_financials=financials,
            )
        )


def test_negative_revenue_rejected(
    service,
):
    """
    Monthly service revenue cannot be negative.
    """

    scenario = make_scenario(
        incremental_churners=0.10,
        row_count=1,
    )

    financials = [
        FinancialImpactCustomer(
            row_index=0,
            monthly_service_revenue=-1.0,
        )
    ]

    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):

        service.calculate(
            FinancialImpactRequest(
                scenario_result=scenario,
                customer_financials=financials,
            )
        )


@pytest.mark.parametrize(
    "margin",
    [
        -0.01,
        1.01,
    ],
)
def test_invalid_margin_rejected(
    service,
    financials,
    margin,
):
    """
    Gross margin must remain inside [0, 1].
    """

    with pytest.raises(
        ValueError
    ):

        service.calculate(
            FinancialImpactRequest(
                scenario_result=(
                    make_scenario(
                        incremental_churners=0.30,
                    )
                ),
                customer_financials=financials,
                gross_margin_rate=margin,
            )
        )


@pytest.mark.parametrize(
    "months",
    [
        0,
        -1,
    ],
)
def test_invalid_clv_horizon_rejected(
    service,
    financials,
    months,
):
    """
    CLV horizon must be positive.
    """

    with pytest.raises(
        ValueError
    ):

        service.calculate(
            FinancialImpactRequest(
                scenario_result=(
                    make_scenario(
                        incremental_churners=0.30,
                    )
                ),
                customer_financials=financials,
                clv_horizon_months=months,
            )
        )


def test_result_metadata(
    service,
    financials,
):
    """
    Financial result must remain explicitly non-causal.
    """

    result = service.calculate(
        FinancialImpactRequest(
            scenario_result=(
                make_scenario(
                    incremental_churners=0.30,
                )
            ),
            customer_financials=financials,
        )
    )

    assert (
        result.analysis_type
        ==
        "predictive_scenario_financial_translation"
    )

    assert (
        result.causal_interpretation
        is False
    )

# =============================================================
# Step 11B-4
# Exact row-level scenario financial translation
# =============================================================


def test_exact_row_path_uses_each_scenario_probability_change(
    service,
):
    """
    When TelecomScenarioResult.records is populated, the
    service must use each row's actual probability_change.

    It must NOT fall back to aggregate revenue-weighted
    allocation.
    """

    scenario = TelecomScenarioResult(
        scenario_id="exact_row_test",
        scenario_title="Exact Row Test",
        category="competitive",
        description="Exact row-level financial test.",
        intensity=1.0,
        row_count=2,

        baseline_mean_probability=0.02,
        scenario_mean_probability=0.04,
        mean_probability_change=0.02,
        relative_probability_change=1.0,

        expected_incremental_churners=0.04,

        expected_direction="increase",
        observed_direction="increase",
        direction_validation_passed=True,

        feature_changes=[],

        records=[
            TelecomScenarioRecord(
                row_index=0,
                baseline_probability=0.02,
                scenario_probability=0.03,
                probability_change=0.01,
                relative_probability_change=0.50,
            ),

            TelecomScenarioRecord(
                row_index=1,
                baseline_probability=0.02,
                scenario_probability=0.05,
                probability_change=0.03,
                relative_probability_change=1.50,
            ),
        ],
    )

    financials = [
        FinancialImpactCustomer(
            row_index=0,
            monthly_service_revenue=100.0,
        ),

        FinancialImpactCustomer(
            row_index=1,
            monthly_service_revenue=200.0,
        ),
    ]

    result = service.calculate(
        FinancialImpactRequest(
            scenario_result=scenario,
            customer_financials=financials,
        )
    )

    assert len(
        result.records
    ) == 2

    # Exact scenario ΔP values must survive unchanged.

    assert np.isclose(
        result.records[
            0
        ].expected_incremental_churners,
        0.01,
    )

    assert np.isclose(
        result.records[
            1
        ].expected_incremental_churners,
        0.03,
    )


def test_exact_row_monthly_revenue_at_risk_identity(
    service,
):
    """
    Exact row financial identity:

        row revenue at risk
            =
        row positive ΔP
            ×
        row monthly service revenue
    """

    scenario = TelecomScenarioResult(
        scenario_id="exact_revenue_test",
        scenario_title="Exact Revenue Test",
        category="competitive",
        description="Exact financial identity test.",
        intensity=1.0,
        row_count=2,

        baseline_mean_probability=0.10,
        scenario_mean_probability=0.125,
        mean_probability_change=0.025,
        relative_probability_change=0.25,

        expected_incremental_churners=0.05,

        expected_direction="increase",
        observed_direction="increase",
        direction_validation_passed=True,

        feature_changes=[],

        records=[
            TelecomScenarioRecord(
                row_index=0,
                baseline_probability=0.10,
                scenario_probability=0.11,
                probability_change=0.01,
                relative_probability_change=0.10,
            ),

            TelecomScenarioRecord(
                row_index=1,
                baseline_probability=0.10,
                scenario_probability=0.14,
                probability_change=0.04,
                relative_probability_change=0.40,
            ),
        ],
    )

    financials = [
        FinancialImpactCustomer(
            row_index=0,
            monthly_service_revenue=100.0,
        ),

        FinancialImpactCustomer(
            row_index=1,
            monthly_service_revenue=200.0,
        ),
    ]

    result = service.calculate(
        FinancialImpactRequest(
            scenario_result=scenario,
            customer_financials=financials,
        )
    )

    # Row 0:
    #
    # 0.01 × $100 = $1

    assert np.isclose(
        result.records[
            0
        ].monthly_revenue_at_risk,
        1.0,
    )

    # Row 1:
    #
    # 0.04 × $200 = $8

    assert np.isclose(
        result.records[
            1
        ].monthly_revenue_at_risk,
        8.0,
    )

    # Population:
    #
    # $1 + $8 = $9

    assert np.isclose(
        result.monthly_revenue_at_risk,
        9.0,
    )

    assert np.isclose(
        result.net_monthly_revenue_impact,
        -9.0,
    )


def test_exact_row_path_differs_from_legacy_revenue_weighting(
    service,
):
    """
    Regression guard:

    Construct a case where exact ΔP allocation is materially
    different from revenue-weighted aggregate allocation.

    The returned values must follow exact TelecomScenarioRecord
    changes.
    """

    scenario = TelecomScenarioResult(
        scenario_id="path_selection_test",
        scenario_title="Path Selection Test",
        category="competitive",
        description="Verify exact path selection.",
        intensity=1.0,
        row_count=2,

        baseline_mean_probability=0.10,
        scenario_mean_probability=0.15,
        mean_probability_change=0.05,
        relative_probability_change=0.50,

        expected_incremental_churners=0.10,

        expected_direction="increase",
        observed_direction="increase",
        direction_validation_passed=True,

        feature_changes=[],

        records=[
            # Almost the entire churn effect belongs to the
            # low-revenue customer.
            TelecomScenarioRecord(
                row_index=0,
                baseline_probability=0.10,
                scenario_probability=0.19,
                probability_change=0.09,
                relative_probability_change=0.90,
            ),

            TelecomScenarioRecord(
                row_index=1,
                baseline_probability=0.10,
                scenario_probability=0.11,
                probability_change=0.01,
                relative_probability_change=0.10,
            ),
        ],
    )

    financials = [
        FinancialImpactCustomer(
            row_index=0,
            monthly_service_revenue=100.0,
        ),

        FinancialImpactCustomer(
            row_index=1,
            monthly_service_revenue=900.0,
        ),
    ]

    result = service.calculate(
        FinancialImpactRequest(
            scenario_result=scenario,
            customer_financials=financials,
        )
    )

    # Exact path:
    #
    # row 0:
    #   0.09 × $100 = $9
    #
    # row 1:
    #   0.01 × $900 = $9
    #
    # total = $18

    assert np.isclose(
        result.monthly_revenue_at_risk,
        18.0,
    )

    # A revenue-weighted aggregate allocation would produce a
    # different answer, so this assertion explicitly protects
    # path selection.

    aggregate = 0.10

    revenue_weights = np.array(
        [
            100.0,
            900.0,
        ]
    ) / 1000.0

    legacy_allocation = (
        aggregate
        *
        revenue_weights
    )

    legacy_revenue_at_risk = (
        legacy_allocation[
            0
        ]
        *
        100.0
        +
        legacy_allocation[
            1
        ]
        *
        900.0
    )

    assert not np.isclose(
        result.monthly_revenue_at_risk,
        legacy_revenue_at_risk,
    )


def test_exact_defensive_row_path_protects_revenue(
    service,
):
    """
    Negative row-level ΔP values must translate into exact
    row-level churn prevention and revenue protection.
    """

    scenario = TelecomScenarioResult(
        scenario_id="exact_defensive_test",
        scenario_title="Exact Defensive Test",
        category="defensive",
        description="Exact defensive scenario test.",
        intensity=1.0,
        row_count=2,

        baseline_mean_probability=0.10,
        scenario_mean_probability=0.075,
        mean_probability_change=-0.025,
        relative_probability_change=-0.25,

        expected_incremental_churners=-0.05,

        expected_direction="decrease",
        observed_direction="decrease",
        direction_validation_passed=True,

        feature_changes=[],

        records=[
            TelecomScenarioRecord(
                row_index=0,
                baseline_probability=0.10,
                scenario_probability=0.09,
                probability_change=-0.01,
                relative_probability_change=-0.10,
            ),

            TelecomScenarioRecord(
                row_index=1,
                baseline_probability=0.10,
                scenario_probability=0.06,
                probability_change=-0.04,
                relative_probability_change=-0.40,
            ),
        ],
    )

    financials = [
        FinancialImpactCustomer(
            row_index=0,
            monthly_service_revenue=100.0,
        ),

        FinancialImpactCustomer(
            row_index=1,
            monthly_service_revenue=200.0,
        ),
    ]

    result = service.calculate(
        FinancialImpactRequest(
            scenario_result=scenario,
            customer_financials=financials,
        )
    )

    # Protected monthly revenue:
    #
    # 0.01 × 100 = 1
    # 0.04 × 200 = 8
    #
    # total = 9

    assert np.isclose(
        result.monthly_revenue_protected,
        9.0,
    )

    assert np.isclose(
        result.net_monthly_revenue_impact,
        9.0,
    )

    assert (
        result.financial_direction
        ==
        "benefit"
    )


def test_exact_row_incremental_churn_sum_identity(
    service,
):
    """
    Sum of financial row-level incremental churn must equal
    the scenario's published expected incremental churners.
    """

    scenario = TelecomScenarioResult(
        scenario_id="sum_identity_test",
        scenario_title="Sum Identity Test",
        category="competitive",
        description="Row total identity test.",
        intensity=1.0,
        row_count=3,

        baseline_mean_probability=0.10,
        scenario_mean_probability=0.12,
        mean_probability_change=0.02,
        relative_probability_change=0.20,

        expected_incremental_churners=0.06,

        expected_direction="increase",
        observed_direction="increase",
        direction_validation_passed=True,

        feature_changes=[],

        records=[
            TelecomScenarioRecord(
                row_index=0,
                baseline_probability=0.10,
                scenario_probability=0.11,
                probability_change=0.01,
                relative_probability_change=0.10,
            ),

            TelecomScenarioRecord(
                row_index=1,
                baseline_probability=0.10,
                scenario_probability=0.12,
                probability_change=0.02,
                relative_probability_change=0.20,
            ),

            TelecomScenarioRecord(
                row_index=2,
                baseline_probability=0.10,
                scenario_probability=0.13,
                probability_change=0.03,
                relative_probability_change=0.30,
            ),
        ],
    )

    financials = [
        FinancialImpactCustomer(
            row_index=0,
            monthly_service_revenue=100.0,
        ),

        FinancialImpactCustomer(
            row_index=1,
            monthly_service_revenue=150.0,
        ),

        FinancialImpactCustomer(
            row_index=2,
            monthly_service_revenue=200.0,
        ),
    ]

    result = service.calculate(
        FinancialImpactRequest(
            scenario_result=scenario,
            customer_financials=financials,
        )
    )

    expected = sum(
        row.expected_incremental_churners
        for row in result.records
    )

    assert np.isclose(
        expected,
        0.06,
    )

    assert np.isclose(
        result.expected_incremental_churners,
        scenario.expected_incremental_churners,
    )


def test_exact_row_order_does_not_control_matching(
    service,
):
    """
    Financial/scenario rows must match by row_index rather than
    by their list position.
    """

    scenario = TelecomScenarioResult(
        scenario_id="row_index_test",
        scenario_title="Row Index Test",
        category="competitive",
        description="Explicit row-index matching.",
        intensity=1.0,
        row_count=2,

        baseline_mean_probability=0.10,
        scenario_mean_probability=0.12,
        mean_probability_change=0.02,
        relative_probability_change=0.20,

        expected_incremental_churners=0.04,

        expected_direction="increase",
        observed_direction="increase",
        direction_validation_passed=True,

        feature_changes=[],

        # Intentionally reversed order.
        records=[
            TelecomScenarioRecord(
                row_index=1,
                baseline_probability=0.10,
                scenario_probability=0.13,
                probability_change=0.03,
                relative_probability_change=0.30,
            ),

            TelecomScenarioRecord(
                row_index=0,
                baseline_probability=0.10,
                scenario_probability=0.11,
                probability_change=0.01,
                relative_probability_change=0.10,
            ),
        ],
    )

    financials = [
        FinancialImpactCustomer(
            row_index=0,
            monthly_service_revenue=100.0,
        ),

        FinancialImpactCustomer(
            row_index=1,
            monthly_service_revenue=200.0,
        ),
    ]

    result = service.calculate(
        FinancialImpactRequest(
            scenario_result=scenario,
            customer_financials=financials,
        )
    )

    assert np.isclose(
        result.records[
            0
        ].expected_incremental_churners,
        0.01,
    )

    assert np.isclose(
        result.records[
            1
        ].expected_incremental_churners,
        0.03,
    )

    assert np.isclose(
        result.monthly_revenue_at_risk,
        7.0,
    )


def test_exact_row_probability_identity_rejected(
    service,
):
    """
    Invalid TelecomScenarioRecord probability identity must
    fail before financial translation.

    probability_change must equal:

        scenario_probability - baseline_probability
    """

    scenario = TelecomScenarioResult(
        scenario_id="bad_probability_test",
        scenario_title="Bad Probability Test",
        category="competitive",
        description="Invalid row identity.",
        intensity=1.0,
        row_count=1,

        baseline_mean_probability=0.10,
        scenario_mean_probability=0.12,
        mean_probability_change=0.02,
        relative_probability_change=0.20,

        expected_incremental_churners=0.05,

        expected_direction="increase",
        observed_direction="increase",
        direction_validation_passed=True,

        feature_changes=[],

        records=[
            TelecomScenarioRecord(
                row_index=0,
                baseline_probability=0.10,
                scenario_probability=0.12,

                # Wrong intentionally:
                # expected change is 0.02.
                probability_change=0.05,

                relative_probability_change=0.50,
            )
        ],
    )

    financials = [
        FinancialImpactCustomer(
            row_index=0,
            monthly_service_revenue=100.0,
        )
    ]

    with pytest.raises(
        ValueError,
        match="probability_change must equal",
    ):

        service.calculate(
            FinancialImpactRequest(
                scenario_result=scenario,
                customer_financials=financials,
            )
        )


def test_exact_row_aggregate_identity_rejected(
    service,
):
    """
    Valid individual ΔP rows whose total disagrees with the
    scenario aggregate must be rejected.
    """

    scenario = TelecomScenarioResult(
        scenario_id="bad_aggregate_test",
        scenario_title="Bad Aggregate Test",
        category="competitive",
        description="Invalid aggregate identity.",
        intensity=1.0,
        row_count=2,

        baseline_mean_probability=0.10,
        scenario_mean_probability=0.11,
        mean_probability_change=0.01,
        relative_probability_change=0.10,

        # Wrong intentionally.
        expected_incremental_churners=0.50,

        expected_direction="increase",
        observed_direction="increase",
        direction_validation_passed=True,

        feature_changes=[],

        records=[
            TelecomScenarioRecord(
                row_index=0,
                baseline_probability=0.10,
                scenario_probability=0.11,
                probability_change=0.01,
                relative_probability_change=0.10,
            ),

            TelecomScenarioRecord(
                row_index=1,
                baseline_probability=0.10,
                scenario_probability=0.11,
                probability_change=0.01,
                relative_probability_change=0.10,
            ),
        ],
    )

    financials = [
        FinancialImpactCustomer(
            row_index=0,
            monthly_service_revenue=100.0,
        ),

        FinancialImpactCustomer(
            row_index=1,
            monthly_service_revenue=100.0,
        ),
    ]

    with pytest.raises(
        ValueError,
        match="do not sum",
    ):

        service.calculate(
            FinancialImpactRequest(
                scenario_result=scenario,
                customer_financials=financials,
            )
        )