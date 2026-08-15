"""
Tests for Synthetic Churn Model Training.
"""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from scripts.synthetic_data.config import (
    SyntheticDataConfig,
)
from scripts.synthetic_data.churn_model_training import (
    ChurnModelTrainer,
)


def make_dataset(
    start_date: str,
    months: int,
    rows_per_month: int = 200,
    seed: int = 42,
) -> pd.DataFrame:

    rng = np.random.default_rng(
        seed
    )

    dates = pd.date_range(
        start=start_date,
        periods=months,
        freq="MS",
    )

    rows = []

    counter = 0

    for month in dates:

        for _ in range(
            rows_per_month
        ):

            counter += 1

            risk = rng.random()

            rows.append(
                {
                    "customer_id": (
                        f"C{counter:08d}"
                    ),
                    "month": month,
                    "market_id": (
                        f"M{rng.integers(1, 20):03d}"
                    ),

                    "state": rng.choice(
                        [
                            "CA",
                            "TX",
                            "NY",
                        ]
                    ),

                    "customer_segment": (
                        rng.choice(
                            [
                                "standard",
                                "premium",
                                "value",
                            ]
                        )
                    ),

                    "tenure_months_current": (
                        rng.integers(
                            1,
                            120,
                        )
                    ),

                    "number_of_lines": (
                        rng.integers(
                            1,
                            5,
                        )
                    ),

                    "device_age_months_current": (
                        rng.integers(
                            1,
                            48,
                        )
                    ),

                    "autopay_flag": (
                        rng.random() < 0.7
                    ),

                    "monthly_arpu": (
                        rng.normal(
                            65,
                            15,
                        )
                    ),

                    "monthly_bill": (
                        rng.normal(
                            110,
                            30,
                        )
                    ),

                    "monthly_bill_change_1m": (
                        rng.normal(
                            0,
                            0.1,
                        )
                    ),

                    "late_payment_count_1m": (
                        rng.integers(
                            0,
                            3,
                        )
                    ),

                    "late_payment_count_3m": (
                        rng.integers(
                            0,
                            5,
                        )
                    ),

                    "payment_failure_count_1m": (
                        rng.integers(
                            0,
                            2,
                        )
                    ),

                    "data_usage_gb": (
                        rng.normal(
                            30,
                            10,
                        )
                    ),

                    "data_usage_gb_change_1m": (
                        rng.normal(
                            0,
                            0.2,
                        )
                    ),

                    "voice_usage_minutes": (
                        rng.normal(
                            400,
                            100,
                        )
                    ),

                    "sms_usage": (
                        rng.normal(
                            100,
                            30,
                        )
                    ),

                    "support_calls_1m": (
                        rng.integers(
                            0,
                            4,
                        )
                    ),

                    "support_calls_3m": (
                        rng.integers(
                            0,
                            6,
                        )
                    ),

                    "network_complaints_1m": (
                        rng.integers(
                            0,
                            3,
                        )
                    ),

                    "network_complaints_3m": (
                        rng.integers(
                            0,
                            5,
                        )
                    ),

                    "network_outage_minutes": (
                        rng.random()
                        * 30
                    ),

                    "dropped_call_rate": (
                        rng.random()
                        * 0.1
                    ),

                    "average_download_speed_mbps": (
                        rng.normal(
                            180,
                            30,
                        )
                    ),

                    "coverage_quality_score": (
                        rng.random()
                    ),

                    "customer_satisfaction_score": (
                        1.0 - risk
                    ),

                    "nps_score": (
                        100
                        * (
                            0.5
                            - risk
                        )
                    ),

                    "retention_offer_received": (
                        risk > 0.7
                    ),

                    "retention_offer_value": (
                        25.0
                        if risk > 0.7
                        else 0.0
                    ),

                    "plan_change_1m": (
                        rng.integers(
                            0,
                            2,
                        )
                    ),

                    "device_upgrade_1m": (
                        rng.integers(
                            0,
                            2,
                        )
                    ),

                    "competitor_event_count": (
                        rng.integers(
                            0,
                            5,
                        )
                    ),

                    "competitor_event_count_3m": (
                        rng.integers(
                            0,
                            10,
                        )
                    ),

                    "competitor_price_cut_count": (
                        rng.integers(
                            0,
                            3,
                        )
                    ),

                    "competitor_price_cut_count_3m": (
                        rng.integers(
                            0,
                            5,
                        )
                    ),

                    "competitor_promotion_count": (
                        rng.integers(
                            0,
                            3,
                        )
                    ),

                    "competitor_promotion_count_3m": (
                        rng.integers(
                            0,
                            5,
                        )
                    ),

                    "competitor_device_offer_count": 0,
                    "competitor_bundle_offer_count": 0,
                    "competitor_network_improvement_count": 0,
                    "competitor_outage_count": 0,
                    "competitor_advertising_count": 0,

                    "competitor_price_change_pct_mean": 0.0,
                    "competitor_promotion_depth_mean": 0.0,
                    "competitor_device_subsidy_mean": 0.0,
                    "competitor_bundle_discount_mean": 0.0,
                    "competitor_network_speed_change_mean": 0.0,
                    "competitor_outage_minutes_mean": 0.0,
                    "competitor_advertising_spend_change_mean": 0.0,

                    "competitive_pressure_mean": (
                        rng.random()
                    ),

                    "competitive_pressure_max": (
                        rng.random()
                    ),

                    "price_sensitivity_score": (
                        rng.random()
                    ),

                    "promotion_sensitivity_score": (
                        rng.random()
                    ),

                    "network_quality_sensitivity_score": (
                        rng.random()
                    ),

                    "brand_loyalty_score": (
                        rng.random()
                    ),

                    "price_pressure_interaction": (
                        rng.random()
                    ),

                    "promotion_pressure_interaction": (
                        rng.random()
                    ),

                    "network_pressure_interaction": (
                        rng.random()
                    ),

                    "competitive_loyalty_interaction": (
                        rng.random()
                    ),

                    "churn_next_30d": int(
                        risk > 0.93
                    ),
                }
            )

    return pd.DataFrame(
        rows
    )


def build_sets():

    train = make_dataset(
        "2025-01-01",
        6,
        seed=42,
    )

    validation = make_dataset(
        "2025-07-01",
        2,
        seed=43,
    )

    test = make_dataset(
        "2025-09-01",
        2,
        seed=44,
    )

    return (
        train,
        validation,
        test,
    )


def test_trainer_returns_results():

    train, validation, test = (
        build_sets()
    )

    trainer = ChurnModelTrainer(
        SyntheticDataConfig()
    )

    output = trainer.train(
        train=train,
        validation=validation,
        test=test,
    )

    assert "result" in output


def test_both_models_are_trained():

    train, validation, test = (
        build_sets()
    )

    result = ChurnModelTrainer().train(
        train,
        validation,
        test,
    )[
        "result"
    ]

    assert (
        "logistic_regression"
        in result[
            "models"
        ]
    )

    assert (
        "hist_gradient_boosting"
        in result[
            "models"
        ]
    )


def test_champion_is_valid():

    train, validation, test = (
        build_sets()
    )

    result = ChurnModelTrainer().train(
        train,
        validation,
        test,
    )[
        "result"
    ]

    assert result[
        "champion"
    ][
        "name"
    ] in {
        "logistic_regression",
        "hist_gradient_boosting",
    }


def test_target_not_used_as_feature():

    train, validation, test = (
        build_sets()
    )

    result = ChurnModelTrainer().train(
        train,
        validation,
        test,
    )[
        "result"
    ]

    assert (
        "churn_next_30d"
        not in result[
            "features"
        ]
    )


def test_identifiers_not_used_as_features():

    train, validation, test = (
        build_sets()
    )

    result = ChurnModelTrainer().train(
        train,
        validation,
        test,
    )[
        "result"
    ]

    for identifier in [
        "customer_id",
        "month",
        "market_id",
    ]:

        assert identifier not in (
            result[
                "features"
            ]
        )


def test_validation_metrics_bounded():

    train, validation, test = (
        build_sets()
    )

    result = ChurnModelTrainer().train(
        train,
        validation,
        test,
    )[
        "result"
    ]

    for model in result[
        "models"
    ].values():

        metrics = model[
            "validation"
        ]

        for metric in [
            "roc_auc",
            "pr_auc",
            "precision",
            "recall",
            "f1",
            "top_decile_capture",
        ]:

            assert (
                0.0
                <= metrics[
                    metric
                ]
                <= 1.0
            )


def test_threshold_is_bounded():

    train, validation, test = (
        build_sets()
    )

    result = ChurnModelTrainer().train(
        train,
        validation,
        test,
    )[
        "result"
    ]

    for model in result[
        "models"
    ].values():

        assert (
            0.0
            <
            model[
                "threshold"
            ]
            <
            1.0
        )


def test_test_metrics_exist():

    train, validation, test = (
        build_sets()
    )

    result = ChurnModelTrainer().train(
        train,
        validation,
        test,
    )[
        "result"
    ]

    assert (
        "roc_auc"
        in result[
            "champion"
        ][
            "test"
        ]
    )

    assert (
        "pr_auc"
        in result[
            "champion"
        ][
            "test"
        ]
    )
    