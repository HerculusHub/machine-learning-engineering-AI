"""
Tests for customer-market exposure generation.
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


def build_data():

    config = SyntheticDataConfig(
        random_seed=42,
        customer_count=2_000,
        operator_event_count=500,
        exposure_customers_per_event=20,
        exposure_event_chunk_size=100,
        snapshot_date=date(
            2026,
            7,
            31,
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

    return (
        config,
        customers,
        events,
        exposure,
    )


def test_generate_returns_dataframe():

    _, _, _, exposure = build_data()

    assert isinstance(
        exposure,
        pd.DataFrame,
    )


def test_exposure_is_not_empty():

    _, _, _, exposure = build_data()

    assert len(
        exposure
    ) > 0


def test_exposure_ids_are_unique():

    _, _, _, exposure = build_data()

    assert exposure[
        "exposure_id"
    ].is_unique


def test_required_columns_exist():

    _, _, _, exposure = build_data()

    required = {
        "exposure_id",
        "customer_id",
        "event_id",
        "market_id",
        "focal_operator_name",
        "competitor_operator_name",
        "event_category",
        "eligible_flag",
        "exposure_flag",
        "exposure_probability_true",
        "treatment_intensity",
        "signed_treatment_intensity",
        "customer_susceptibility",
        "baseline_churn_propensity",
        "true_treatment_effect_log_odds",
        "observed_event_effect_log_odds",
    }

    assert required.issubset(
        exposure.columns
    )


def test_only_competitor_events_are_used():

    config, _, _, exposure = build_data()

    assert (
        exposure[
            "competitor_operator_name"
        ]
        != config.focal_operator_name
    ).all()


def test_customer_and_event_market_match():

    _, customers, events, exposure = build_data()

    customer_market = customers.set_index(
        "customer_id"
    )[
        "market_id"
    ]

    event_market = events.set_index(
        "event_id"
    )[
        "market_id"
    ]

    mapped_customer_market = (
        exposure[
            "customer_id"
        ].map(
            customer_market
        )
    )

    mapped_event_market = (
        exposure[
            "event_id"
        ].map(
            event_market
        )
    )

    assert (
        mapped_customer_market
        ==
        mapped_event_market
    ).all()


def test_exposure_probability_is_bounded():

    _, _, _, exposure = build_data()

    probability = exposure[
        "exposure_probability_true"
    ]

    assert (
        probability >= 0.0
    ).all()

    assert (
        probability <= 1.0
    ).all()


def test_treatment_intensity_is_bounded():

    _, _, _, exposure = build_data()

    intensity = exposure[
        "treatment_intensity"
    ]

    assert (
        intensity >= 0.0
    ).all()

    assert (
        intensity <= 1.0
    ).all()


def test_susceptibility_is_bounded():

    _, _, _, exposure = build_data()

    value = exposure[
        "customer_susceptibility"
    ]

    assert (
        value >= 0.0
    ).all()

    assert (
        value <= 1.0
    ).all()


def test_unexposed_has_zero_observed_effect():

    _, _, _, exposure = build_data()

    untreated = exposure[
        ~exposure[
            "exposure_flag"
        ]
    ]

    assert (
        untreated[
            "observed_event_effect_log_odds"
        ]
        == 0.0
    ).all()


def test_exposed_effect_matches_ground_truth():

    _, _, _, exposure = build_data()

    treated = exposure[
        exposure[
            "exposure_flag"
        ]
    ]

    assert (
        treated[
            "observed_event_effect_log_odds"
        ]
        ==
        treated[
            "true_treatment_effect_log_odds"
        ]
    ).all()


def test_contains_treated_and_control_observations():

    _, _, _, exposure = build_data()

    values = set(
        exposure[
            "exposure_flag"
        ].unique()
    )

    assert values == {
        False,
        True,
    }


def test_price_reductions_can_raise_churn_pressure():

    _, _, _, exposure = build_data()

    price_cuts = exposure[
        (
            exposure[
                "event_category"
            ]
            == "price_change"
        )
        &
        (
            exposure[
                "price_change_pct"
            ]
            < 0
        )
    ]

    assert len(
        price_cuts
    ) > 0

    assert (
        price_cuts[
            "signed_treatment_intensity"
        ] > 0
    ).all()


def test_competitor_outage_reduces_churn_pressure():

    _, _, _, exposure = build_data()

    outages = exposure[
        exposure[
            "event_category"
        ]
        == "network_outage"
    ]

    assert len(
        outages
    ) > 0

    assert (
        outages[
            "signed_treatment_intensity"
        ] <= 0
    ).all()


def test_reproducible():

    first = build_data()[
        3
    ]

    second = build_data()[
        3
    ]

    pd.testing.assert_frame_equal(
        first,
        second,
    )