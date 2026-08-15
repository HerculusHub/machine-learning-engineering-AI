"""
Tests for synthetic customer master generation.
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


def build_generator(
    customer_count: int = 1_000,
    seed: int = 42,
) -> CustomerMasterGenerator:
    """
    Build a small deterministic generator for testing.
    """

    config = SyntheticDataConfig(
        random_seed=seed,
        customer_count=customer_count,
        snapshot_date=date(
            2026,
            7,
            31,
        ),
    )

    return CustomerMasterGenerator(
        config=config,
    )


def test_generate_returns_dataframe():
    generator = build_generator()

    result = generator.generate()

    assert isinstance(
        result,
        pd.DataFrame,
    )


def test_generate_correct_row_count():
    generator = build_generator(
        customer_count=500
    )

    result = generator.generate()

    assert len(result) == 500


def test_customer_ids_are_unique():
    generator = build_generator()

    result = generator.generate()

    assert result[
        "customer_id"
    ].is_unique


def test_required_columns_exist():
    generator = build_generator()

    result = generator.generate()

    required_columns = {
        "customer_id",
        "snapshot_date",
        "state",
        "market_id",
        "age_band",
        "household_size",
        "household_income_band",
        "tenure_start_date",
        "tenure_months",
        "customer_segment",
        "account_type",
        "number_of_lines",
        "primary_plan_id",
        "device_type",
        "device_age_months",
        "autopay_flag",
        "paperless_billing_flag",
        "historical_arpu",
        "historical_data_usage_gb",
        "historical_support_calls",
        "historical_network_complaints",
        "price_sensitivity_score",
        "promotion_sensitivity_score",
        "network_quality_sensitivity_score",
        "brand_loyalty_score",
        "credit_risk_band",
        "baseline_churn_propensity",
    }

    assert required_columns.issubset(
        result.columns
    )


def test_behavior_scores_are_bounded():
    generator = build_generator()

    result = generator.generate()

    score_columns = [
        "price_sensitivity_score",
        "promotion_sensitivity_score",
        "network_quality_sensitivity_score",
        "brand_loyalty_score",
    ]

    for column in score_columns:

        assert (
            result[column] >= 0.0
        ).all()

        assert (
            result[column] <= 1.0
        ).all()


def test_churn_propensity_is_valid_probability():
    generator = build_generator()

    result = generator.generate()

    probability = result[
        "baseline_churn_propensity"
    ]

    assert (
        probability >= 0.0
    ).all()

    assert (
        probability <= 1.0
    ).all()


def test_customer_segments_are_valid():
    generator = build_generator()

    result = generator.generate()

    expected = {
        "value",
        "standard",
        "premium",
        "family",
        "prepaid",
    }

    assert set(
        result[
            "customer_segment"
        ].unique()
    ).issubset(
        expected
    )


def test_account_types_are_valid():
    generator = build_generator()

    result = generator.generate()

    assert set(
        result[
            "account_type"
        ].unique()
    ).issubset(
        {
            "postpaid",
            "prepaid",
        }
    )


def test_tenure_is_positive():
    generator = build_generator()

    result = generator.generate()

    assert (
        result[
            "tenure_months"
        ] > 0
    ).all()


def test_arpu_is_positive():
    generator = build_generator()

    result = generator.generate()

    assert (
        result[
            "historical_arpu"
        ] > 0
    ).all()


def test_generator_is_reproducible():
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


def test_different_seeds_change_population():
    first = build_generator(
        seed=100
    ).generate()

    second = build_generator(
        seed=200
    ).generate()

    assert not first.equals(
        second
    )


def test_market_id_matches_state():
    generator = build_generator()

    result = generator.generate()

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