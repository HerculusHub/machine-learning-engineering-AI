"""
Tests for Synthetic ML Dataset Builder.

Post-MVP Synthetic Analytics Environment
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
from scripts.synthetic_data.ml_dataset_builder import (
    MLDatasetBuilder,
)


def build_ml_data():
    """
    Build complete small synthetic pipeline.
    """

    config = SyntheticDataConfig(
        random_seed=42,
        customer_count=1_000,
        operator_event_count=1_000,
        exposure_customers_per_event=30,
        exposure_event_chunk_size=100,
        panel_customer_chunk_size=200,

        panel_start_date=date(
            2025,
            1,
            1,
        ),

        panel_end_date=date(
            2026,
            6,
            1,
        ),

        ml_train_start_date=date(
            2025,
            1,
            1,
        ),

        ml_train_end_date=date(
            2025,
            12,
            1,
        ),

        ml_validation_start_date=date(
            2026,
            1,
            1,
        ),

        ml_validation_end_date=date(
            2026,
            3,
            1,
        ),

        ml_test_start_date=date(
            2026,
            4,
            1,
        ),

        ml_test_end_date=date(
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

    exposures = CustomerMarketExposureGenerator(
        config=config,
    ).generate(
        customers=customers,
        events=events,
    )

    panel = CustomerMonthlyPanelGenerator(
        config=config,
    ).generate(
        customers=customers,
        exposures=exposures,
    )

    outcomes = CustomerChurnOutcomeGenerator(
        config=config,
    ).generate(
        panel=panel,
    )

    (
        train,
        validation,
        test,
        manifest,
    ) = MLDatasetBuilder(
        config=config,
    ).generate(
        panel=panel,
        outcomes=outcomes,
    )

    return (
        config,
        train,
        validation,
        test,
        manifest,
    )


def test_datasets_not_empty():

    _, train, validation, test, _ = (
        build_ml_data()
    )

    assert not train.empty
    assert not validation.empty
    assert not test.empty


def test_target_exists():

    _, train, validation, test, _ = (
        build_ml_data()
    )

    for frame in [
        train,
        validation,
        test,
    ]:

        assert (
            "churn_next_30d"
            in frame.columns
        )


def test_target_is_binary():

    _, train, validation, test, _ = (
        build_ml_data()
    )

    for frame in [
        train,
        validation,
        test,
    ]:

        assert set(
            frame[
                "churn_next_30d"
            ].unique()
        ).issubset(
            {
                0,
                1,
            }
        )


def test_temporal_order():

    _, train, validation, test, _ = (
        build_ml_data()
    )

    assert (
        train[
            "month"
        ].max()
        <
        validation[
            "month"
        ].min()
    )

    assert (
        validation[
            "month"
        ].max()
        <
        test[
            "month"
        ].min()
    )


def test_train_dates():

    config, train, _, _, _ = (
        build_ml_data()
    )

    assert train[
        "month"
    ].min() == pd.Timestamp(
        config.ml_train_start_date
    )

    assert train[
        "month"
    ].max() == pd.Timestamp(
        config.ml_train_end_date
    )


def test_validation_dates():

    config, _, validation, _, _ = (
        build_ml_data()
    )

    assert validation[
        "month"
    ].min() == pd.Timestamp(
        config.ml_validation_start_date
    )

    assert validation[
        "month"
    ].max() == pd.Timestamp(
        config.ml_validation_end_date
    )


def test_test_dates():

    config, _, _, test, _ = (
        build_ml_data()
    )

    assert test[
        "month"
    ].min() == pd.Timestamp(
        config.ml_test_start_date
    )

    assert test[
        "month"
    ].max() == pd.Timestamp(
        config.ml_test_end_date
    )


def test_customer_month_unique():

    _, train, validation, test, _ = (
        build_ml_data()
    )

    for frame in [
        train,
        validation,
        test,
    ]:

        assert not frame.duplicated(
            [
                "customer_id",
                "month",
            ]
        ).any()


def test_no_known_leakage_columns():

    _, train, validation, test, _ = (
        build_ml_data()
    )

    forbidden = {
        "churn_probability_true",
        "counterfactual_churn_probability",
        "incremental_churn_probability_true",
        "monthly_churn_pressure_log_odds",
        "exposure_effect_log_odds_3m",
        "baseline_churn_propensity",
        "realized_churn_event",
        "churn_date",
        "days_to_churn",
        "primary_churn_driver",
    }

    for frame in [
        train,
        validation,
        test,
    ]:

        assert forbidden.isdisjoint(
            frame.columns
        )


def test_target_not_in_features():

    _, _, _, _, manifest = (
        build_ml_data()
    )

    assert (
        manifest[
            "target"
        ]
        not in manifest[
            "features"
        ]
    )


def test_identifiers_not_in_features():

    _, _, _, _, manifest = (
        build_ml_data()
    )

    identifiers = set(
        manifest[
            "identifiers"
        ]
    )

    features = set(
        manifest[
            "features"
        ]
    )

    assert identifiers.isdisjoint(
        features
    )


def test_manifest_uses_temporal_split():

    _, _, _, _, manifest = (
        build_ml_data()
    )

    assert (
        manifest[
            "split_strategy"
        ]
        == "temporal"
    )


def test_manifest_row_counts():

    _, train, validation, test, manifest = (
        build_ml_data()
    )

    assert (
        manifest[
            "train"
        ][
            "rows"
        ]
        ==
        len(
            train
        )
    )

    assert (
        manifest[
            "validation"
        ][
            "rows"
        ]
        ==
        len(
            validation
        )
    )

    assert (
        manifest[
            "test"
        ][
            "rows"
        ]
        ==
        len(
            test
        )
    )


def test_competitive_features_are_present():

    _, train, _, _, _ = (
        build_ml_data()
    )

    expected = {
        "competitor_price_cut_count_3m",
        "competitor_promotion_count_3m",
        "competitive_pressure_mean",
        "price_pressure_interaction",
        "promotion_pressure_interaction",
    }

    assert expected.issubset(
        train.columns
    )


def test_customer_behavior_features_are_present():

    _, train, _, _, _ = (
        build_ml_data()
    )

    expected = {
        "monthly_arpu",
        "monthly_bill",
        "data_usage_gb",
        "support_calls_3m",
        "network_complaints_3m",
        "customer_satisfaction_score",
        "brand_loyalty_score",
    }

    assert expected.issubset(
        train.columns
    )


def test_month_is_datetime():

    _, train, validation, test, _ = (
        build_ml_data()
    )

    for frame in [
        train,
        validation,
        test,
    ]:

        assert (
            pd.api.types
            .is_datetime64_any_dtype(
                frame[
                    "month"
                ]
            )
        )