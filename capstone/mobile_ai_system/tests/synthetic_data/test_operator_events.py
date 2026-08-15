"""
Tests for synthetic competitive operator events.
"""

from __future__ import annotations

from datetime import date

import pandas as pd

from scripts.synthetic_data.config import (
    SyntheticDataConfig,
)
from scripts.synthetic_data.operator_events import (
    OperatorEventGenerator,
)


def build_generator(
    count: int = 1_000,
    seed: int = 42,
) -> OperatorEventGenerator:

    config = SyntheticDataConfig(
        random_seed=seed,
        operator_event_count=count,
        event_start_date=date(
            2023,
            1,
            1,
        ),
        event_end_date=date(
            2026,
            7,
            31,
        ),
    )

    return OperatorEventGenerator(
        config=config,
    )


def test_generate_returns_dataframe():

    result = build_generator().generate()

    assert isinstance(
        result,
        pd.DataFrame,
    )


def test_correct_row_count():

    result = build_generator(
        count=500
    ).generate()

    assert len(result) == 500


def test_event_ids_are_unique():

    result = build_generator().generate()

    assert result[
        "event_id"
    ].is_unique


def test_required_columns_exist():

    result = build_generator().generate()

    required = {
        "event_id",
        "event_date",
        "event_start_date",
        "event_end_date",
        "operator_name",
        "event_category",
        "event_subcategory",
        "state",
        "market_id",
        "geographic_scope",
        "price_change_pct",
        "promotion_discount_pct",
        "device_subsidy_amount",
        "bundle_discount_pct",
        "network_speed_change_pct",
        "coverage_change_pct",
        "network_outage_minutes",
        "advertising_spend_change_pct",
        "campaign_reach_pct",
        "event_duration_days",
        "sentiment_score",
        "importance_score",
        "confidence_score",
        "competitive_pressure_score",
        "source_type",
        "event_source",
        "generated_summary",
    }

    assert required.issubset(
        result.columns
    )


def test_scores_are_bounded():

    result = build_generator().generate()

    for column in [
        "importance_score",
        "confidence_score",
        "competitive_pressure_score",
    ]:

        assert (
            result[column] >= 0.0
        ).all()

        assert (
            result[column] <= 1.0
        ).all()


def test_sentiment_is_bounded():

    result = build_generator().generate()

    assert (
        result[
            "sentiment_score"
        ] >= -1.0
    ).all()

    assert (
        result[
            "sentiment_score"
        ] <= 1.0
    ).all()


def test_price_events_have_price_values():

    result = build_generator(
        count=5_000
    ).generate()

    price_events = result[
        result[
            "event_category"
        ] == "price_change"
    ]

    assert len(
        price_events
    ) > 0

    assert (
        price_events[
            "price_change_pct"
        ].abs()
        > 0
    ).all()


def test_promotions_have_discount():

    result = build_generator(
        count=5_000
    ).generate()

    promotions = result[
        result[
            "event_category"
        ] == "promotion"
    ]

    assert len(
        promotions
    ) > 0

    assert (
        promotions[
            "promotion_discount_pct"
        ] > 0
    ).all()


def test_network_improvements_have_positive_change():

    result = build_generator(
        count=5_000
    ).generate()

    events = result[
        result[
            "event_category"
        ] == "network_improvement"
    ]

    assert len(events) > 0

    assert (
        events[
            "network_speed_change_pct"
        ] > 0
    ).all()


def test_network_outages_have_minutes():

    result = build_generator(
        count=5_000
    ).generate()

    events = result[
        result[
            "event_category"
        ] == "network_outage"
    ]

    assert len(events) > 0

    assert (
        events[
            "network_outage_minutes"
        ] > 0
    ).all()


def test_event_end_not_before_start():

    result = build_generator().generate()

    assert (
        pd.to_datetime(
            result[
                "event_end_date"
            ]
        )
        >=
        pd.to_datetime(
            result[
                "event_start_date"
            ]
        )
    ).all()


def test_market_matches_state():

    result = build_generator().generate()

    matches = result.apply(
        lambda row: (
            row[
                "market_id"
            ].startswith(
                row[
                    "state"
                ]
            )
        ),
        axis=1,
    )

    assert matches.all()


def test_reproducible():

    first = build_generator(
        seed=123
    ).generate()

    second = build_generator(
        seed=123
    ).generate()

    pd.testing.assert_frame_equal(
        first,
        second,
    )


def test_different_seed_changes_events():

    first = build_generator(
        seed=100
    ).generate()

    second = build_generator(
        seed=200
    ).generate()

    assert not first.equals(
        second
    )