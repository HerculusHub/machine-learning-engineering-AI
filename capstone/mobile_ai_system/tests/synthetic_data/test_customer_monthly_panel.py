"""
Tests for synthetic customer monthly panel.
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


def build_panel():

    config = SyntheticDataConfig(
        random_seed=42,
        customer_count=500,
        operator_event_count=300,
        exposure_customers_per_event=20,
        exposure_event_chunk_size=100,
        panel_customer_chunk_size=100,
        panel_start_date=date(
            2026,
            1,
            1,
        ),
        panel_end_date=date(
            2026,
            6,
            1,
        ),
    )

    customers = CustomerMasterGenerator(
        config=config,
    ).generate()

    events = OperatorEventGenerator(
        config=config,
    ).generate()

    exposures = (
        CustomerMarketExposureGenerator(
            config=config,
        ).generate(
            customers=customers,
            events=events,
        )
    )

    panel = CustomerMonthlyPanelGenerator(
        config=config,
    ).generate(
        customers=customers,
        exposures=exposures,
    )

    return (
        config,
        customers,
        exposures,
        panel,
    )


def test_generate_returns_dataframe():

    _, _, _, panel = build_panel()

    assert isinstance(
        panel,
        pd.DataFrame,
    )


def test_correct_grain():

    config, customers, _, panel = (
        build_panel()
    )

    months = pd.date_range(
        config.panel_start_date,
        config.panel_end_date,
        freq="MS",
    )

    assert len(panel) == (
        len(customers)
        * len(months)
    )


def test_customer_month_is_unique():

    _, _, _, panel = build_panel()

    assert not panel.duplicated(
        [
            "customer_id",
            "month",
        ]
    ).any()


def test_required_columns_exist():

    _, _, _, panel = build_panel()

    required = {
        "customer_id",
        "month",
        "monthly_arpu",
        "monthly_bill",
        "data_usage_gb",
        "support_calls_1m",
        "support_calls_3m",
        "network_complaints_1m",
        "network_complaints_3m",
        "customer_satisfaction_score",
        "competitor_event_count",
        "competitor_event_count_3m",
        "competitor_price_cut_count_3m",
        "competitor_promotion_count_3m",
        "exposure_effect_log_odds_3m",
        "price_pressure_interaction",
        "promotion_pressure_interaction",
        "monthly_churn_pressure_log_odds",
    }

    assert required.issubset(
        panel.columns
    )


def test_months_are_in_range():

    config, _, _, panel = build_panel()

    assert panel[
        "month"
    ].min() == pd.Timestamp(
        config.panel_start_date
    )

    assert panel[
        "month"
    ].max() == pd.Timestamp(
        config.panel_end_date
    )


def test_arpu_is_positive():

    _, _, _, panel = build_panel()

    assert (
        panel[
            "monthly_arpu"
        ] > 0
    ).all()


def test_bill_is_positive():

    _, _, _, panel = build_panel()

    assert (
        panel[
            "monthly_bill"
        ] > 0
    ).all()


def test_satisfaction_is_bounded():

    _, _, _, panel = build_panel()

    score = panel[
        "customer_satisfaction_score"
    ]

    assert (
        score >= 0.0
    ).all()

    assert (
        score <= 1.0
    ).all()


def test_coverage_quality_is_bounded():

    _, _, _, panel = build_panel()

    score = panel[
        "coverage_quality_score"
    ]

    assert (
        score >= 0.0
    ).all()

    assert (
        score <= 1.0
    ).all()


def test_exposure_counts_nonnegative():

    _, _, _, panel = build_panel()

    assert (
        panel[
            "competitor_event_count"
        ] >= 0
    ).all()

    assert (
        panel[
            "competitor_event_count_3m"
        ] >= 0
    ).all()


def test_three_month_count_at_least_current_month():

    _, _, _, panel = build_panel()

    assert (
        panel[
            "competitor_event_count_3m"
        ]
        >=
        panel[
            "competitor_event_count"
        ]
    ).all()


def test_support_rolling_sum():

    _, _, _, panel = build_panel()

    assert (
        panel[
            "support_calls_3m"
        ]
        >=
        panel[
            "support_calls_1m"
        ]
    ).all()


def test_tenure_increases_over_time():

    _, _, _, panel = build_panel()

    customer_id = panel[
        "customer_id"
    ].iloc[
        0
    ]

    customer = panel[
        panel[
            "customer_id"
        ]
        == customer_id
    ].sort_values(
        "month"
    )

    difference = customer[
        "tenure_months_current"
    ].diff().dropna()

    assert (
        difference == 1
    ).all()


def test_device_age_increases_over_time():

    _, _, _, panel = build_panel()

    customer_id = panel[
        "customer_id"
    ].iloc[
        0
    ]

    customer = panel[
        panel[
            "customer_id"
        ]
        == customer_id
    ].sort_values(
        "month"
    )

    difference = customer[
        "device_age_months_current"
    ].diff().dropna()

    assert (
        difference == 1
    ).all()


def test_no_churn_label_exists():

    _, _, _, panel = build_panel()

    forbidden = {
        "churn",
        "churn_flag",
        "churn_next_30d",
        "observed_churn",
    }

    assert forbidden.isdisjoint(
        panel.columns
    )


def test_reproducible():

    first = build_panel()[
        3
    ]

    second = build_panel()[
        3
    ]

    pd.testing.assert_frame_equal(
        first,
        second,
    )