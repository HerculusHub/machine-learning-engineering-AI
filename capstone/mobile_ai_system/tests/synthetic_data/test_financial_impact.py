"""
Tests for synthetic financial impact generation.
"""

from __future__ import annotations

from datetime import date

import pandas as pd

from scripts.synthetic_data.config import (
    SyntheticDataConfig,
)
from scripts.synthetic_data.customer_master import (
    CustomerMasterGenerator,
)
from scripts.synthetic_data.operator_events import (
    OperatorEventGenerator,
)
from scripts.synthetic_data.customer_market_exposure import (
    CustomerMarketExposureGenerator,
)
from scripts.synthetic_data.customer_monthly_panel import (
    CustomerMonthlyPanelGenerator,
)
from scripts.synthetic_data.customer_churn_outcomes import (
    CustomerChurnOutcomeGenerator,
)
from scripts.synthetic_data.financial_impact import (
    FinancialImpactGenerator,
)


def build_financials():

    config = SyntheticDataConfig(
        random_seed=42,
        customer_count=500,
        operator_event_count=500,
        exposure_customers_per_event=20,
        exposure_event_chunk_size=100,
        panel_customer_chunk_size=100,
        panel_start_date=date(
            2025,
            1,
            1,
        ),
        panel_end_date=date(
            2026,
            12,
            1,
        ),
    )

    customers = CustomerMasterGenerator(
        config=config,
    ).generate()

    events = OperatorEventGenerator(
        config=config,
    ).generate()

    exposure = CustomerMarketExposureGenerator(
        config=config,
    ).generate(
        customers=customers,
        events=events,
    )

    panel = CustomerMonthlyPanelGenerator(
        config=config,
    ).generate(
        customers=customers,
        exposures=exposure,
    )

    outcomes = CustomerChurnOutcomeGenerator(
        config=config,
    ).generate(
        panel=panel,
    )

    operator, market = FinancialImpactGenerator(
        config=config,
    ).generate(
        panel=panel,
        outcomes=outcomes,
    )

    return (
        config,
        operator,
        market,
    )


def test_returns_dataframes():

    _, operator, market = build_financials()

    assert isinstance(
        operator,
        pd.DataFrame,
    )

    assert isinstance(
        market,
        pd.DataFrame,
    )


def test_operator_month_is_unique():

    _, operator, _ = build_financials()

    assert not operator.duplicated(
        [
            "operator_name",
            "month",
        ]
    ).any()


def test_market_month_is_unique():

    _, _, market = build_financials()

    assert not market.duplicated(
        [
            "market_id",
            "month",
        ]
    ).any()


def test_focal_operator_only():

    config, operator, market = build_financials()

    assert set(
        operator[
            "operator_name"
        ].unique()
    ) == {
        config.focal_operator_name
    }

    assert set(
        market[
            "operator_name"
        ].unique()
    ) == {
        config.focal_operator_name
    }


def test_revenue_positive():

    _, operator, _ = build_financials()

    assert (
        operator[
            "service_revenue"
        ] > 0
    ).all()


def test_churn_rate_bounded():

    _, operator, _ = build_financials()

    assert (
        operator[
            "realized_churn_rate"
        ] >= 0
    ).all()

    assert (
        operator[
            "realized_churn_rate"
        ] <= 1
    ).all()


def test_competitor_loss_identity():

    _, operator, _ = build_financials()

    difference = (
        operator[
            "expected_monthly_revenue_loss"
        ]
        -
        operator[
            "counterfactual_monthly_revenue_loss"
        ]
    )

    assert (
        difference.round(
            2
        )
        ==
        operator[
            "incremental_competitor_revenue_loss"
        ].round(
            2
        )
    ).all()


def test_annualized_loss_identity():

    _, operator, _ = build_financials()

    expected = (
        operator[
            "expected_monthly_revenue_loss"
        ]
        * 12.0
    )

    assert (
        expected.round(
            2
        )
        ==
        operator[
            "annualized_revenue_loss"
        ].round(
            2
        )
    ).all()


def test_operator_equals_sum_of_markets():

    _, operator, market = build_financials()

    market_sum = (
        market.groupby(
            "month"
        )[
            "service_revenue"
        ]
        .sum()
    )

    operator_series = (
        operator.set_index(
            "month"
        )[
            "service_revenue"
        ]
    )

    pd.testing.assert_series_equal(
        operator_series,
        market_sum,
        check_names=False,
    )


def test_competitor_clv_loss_can_be_positive():

    _, operator, _ = build_financials()

    assert (
        operator[
            "incremental_competitor_clv_loss"
        ] > 0
    ).any()