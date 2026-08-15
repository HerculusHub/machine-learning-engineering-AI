"""
Tests for synthetic customer churn outcomes.
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


def build_outcomes():

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

    exposure = (
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
        exposures=exposure,
    )

    outcomes = CustomerChurnOutcomeGenerator(
        config=config,
    ).generate(
        panel=panel,
    )

    return (
        config,
        panel,
        outcomes,
    )


def test_returns_dataframe():

    _, _, outcomes = build_outcomes()

    assert isinstance(
        outcomes,
        pd.DataFrame,
    )


def test_same_grain_as_panel():

    _, panel, outcomes = build_outcomes()

    assert len(
        outcomes
    ) == len(
        panel
    )


def test_customer_month_unique():

    _, _, outcomes = build_outcomes()

    assert not outcomes.duplicated(
        [
            "customer_id",
            "month",
        ]
    ).any()


def test_required_columns():

    _, _, outcomes = build_outcomes()

    required = {
        "customer_id",
        "month",
        "at_risk_flag",
        "churn_next_30d",
        "churn_next_60d",
        "churn_next_90d",
        "realized_churn_event",
        "churn_date",
        "churn_probability_true",
        "counterfactual_churn_probability",
        "incremental_churn_probability_true",
        "competitor_effect_log_odds_true",
        "primary_churn_driver",
    }

    assert required.issubset(
        outcomes.columns
    )


def test_probabilities_bounded():

    _, _, outcomes = build_outcomes()

    for column in [
        "churn_probability_true",
        "counterfactual_churn_probability",
    ]:

        assert (
            outcomes[column]
            >= 0.0
        ).all()

        assert (
            outcomes[column]
            <= 1.0
        ).all()


def test_only_one_realized_churn_per_customer():

    _, _, outcomes = build_outcomes()

    events = (
        outcomes.groupby(
            "customer_id"
        )[
            "realized_churn_event"
        ]
        .sum()
    )

    assert (
        events <= 1
    ).all()


def test_churn_event_occurs_while_at_risk():

    _, _, outcomes = build_outcomes()

    events = outcomes[
        outcomes[
            "realized_churn_event"
        ]
    ]

    assert events[
        "at_risk_flag"
    ].all()


def test_churn_windows_nested():

    _, _, outcomes = build_outcomes()

    assert (
        ~outcomes[
            "churn_next_30d"
        ]
        |
        outcomes[
            "churn_next_60d"
        ]
    ).all()

    assert (
        ~outcomes[
            "churn_next_60d"
        ]
        |
        outcomes[
            "churn_next_90d"
        ]
    ).all()


def test_no_at_risk_rows_after_churn():

    _, _, outcomes = build_outcomes()

    for _, customer in outcomes.groupby(
        "customer_id"
    ):

        events = customer[
            customer[
                "realized_churn_event"
            ]
        ]

        if events.empty:
            continue

        event_month = events[
            "month"
        ].iloc[
            0
        ]

        future = customer[
            customer[
                "month"
            ]
            > event_month
        ]

        assert not future[
            "at_risk_flag"
        ].any()


def test_competitive_effect_identity():

    _, _, outcomes = build_outcomes()

    difference = (
        outcomes[
            "churn_log_odds_true"
        ]
        -
        outcomes[
            "counterfactual_churn_log_odds"
        ]
    )

    expected = outcomes[
        "competitor_effect_log_odds_true"
    ]

    assert (
        difference.round(
            5
        )
        ==
        expected.round(
            5
        )
    ).all()


def test_positive_competitive_effect_raises_probability():

    _, _, outcomes = build_outcomes()

    positive = outcomes[
        outcomes[
            "competitor_effect_log_odds_true"
        ] > 0
    ]

    if not positive.empty:

        assert (
            positive[
                "churn_probability_true"
            ]
            >=
            positive[
                "counterfactual_churn_probability"
            ]
        ).all()


def test_negative_competitive_effect_reduces_probability():

    _, _, outcomes = build_outcomes()

    negative = outcomes[
        outcomes[
            "competitor_effect_log_odds_true"
        ] < 0
    ]

    if not negative.empty:

        assert (
            negative[
                "churn_probability_true"
            ]
            <=
            negative[
                "counterfactual_churn_probability"
            ]
        ).all()


def test_incremental_probability_identity():

    _, _, outcomes = build_outcomes()

    expected = (
        outcomes[
            "churn_probability_true"
        ]
        -
        outcomes[
            "counterfactual_churn_probability"
        ]
    )

    assert (
        expected.round(
            5
        )
        ==
        outcomes[
            "incremental_churn_probability_true"
        ].round(
            5
        )
    ).all()


def test_churners_have_driver():

    _, _, outcomes = build_outcomes()

    churners = outcomes[
        outcomes[
            "realized_churn_event"
        ]
    ]

    assert not churners.empty

    assert churners[
        "primary_churn_driver"
    ].notna().all()


def test_port_out_has_destination():

    _, _, outcomes = build_outcomes()

    port_out = outcomes[
        outcomes[
            "churn_type"
        ]
        == "port_out"
    ]

    if not port_out.empty:

        assert port_out[
            "destination_operator"
        ].notna().all()


def test_reproducible():

    first = build_outcomes()[
        2
    ]

    second = build_outcomes()[
        2
    ]

    pd.testing.assert_frame_equal(
        first,
        second,
    )

    