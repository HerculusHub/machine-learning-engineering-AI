"""
Tests for Synthetic Churn Feature Engineering.

Post-MVP Machine Learning Environment
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from scripts.synthetic_data.churn_feature_engineering import (
    ChurnFeatureEngineer,
)


def make_frame() -> pd.DataFrame:
    """
    Create a small deterministic customer-month dataset.

    Four months per customer are included so three-month
    lag-based trend features can be tested directly.
    """

    rows = []

    months = pd.date_range(
        "2025-01-01",
        periods=4,
        freq="MS",
    )

    support_a = [
        1,
        2,
        3,
        5,
    ]

    complaints_a = [
        0,
        1,
        1,
        3,
    ]

    satisfaction_a = [
        0.90,
        0.85,
        0.80,
        0.65,
    ]

    nps_a = [
        60,
        50,
        40,
        10,
    ]

    bill_a = [
        80,
        82,
        84,
        95,
    ]

    usage_a = [
        35,
        34,
        32,
        24,
    ]

    late_a = [
        0,
        0,
        1,
        2,
    ]

    for index, month in enumerate(
        months
    ):

        rows.append(
            {
                "customer_id": "C001",
                "month": month,
                "market_id": "M001",
                "state": "CA",
                "customer_segment": "standard",

                "tenure_months_current": (
                    24
                    + index
                ),

                "number_of_lines": 2,

                "device_age_months_current": (
                    20
                    + index * 6
                ),

                "autopay_flag": True,

                "monthly_arpu": 65.0,

                "monthly_bill": (
                    bill_a[
                        index
                    ]
                ),

                "monthly_bill_change_1m": (
                    0.02
                    * index
                ),

                "late_payment_count_1m": (
                    min(
                        late_a[
                            index
                        ],
                        1,
                    )
                ),

                "late_payment_count_3m": (
                    late_a[
                        index
                    ]
                ),

                "payment_failure_count_1m": (
                    1
                    if index == 3
                    else 0
                ),

                "data_usage_gb": (
                    usage_a[
                        index
                    ]
                ),

                "data_usage_gb_change_1m": (
                    -0.05
                    * index
                ),

                "voice_usage_minutes": 400.0,

                "sms_usage": 100.0,

                "support_calls_1m": (
                    min(
                        support_a[
                            index
                        ],
                        2,
                    )
                ),

                "support_calls_3m": (
                    support_a[
                        index
                    ]
                ),

                "network_complaints_1m": (
                    min(
                        complaints_a[
                            index
                        ],
                        1,
                    )
                ),

                "network_complaints_3m": (
                    complaints_a[
                        index
                    ]
                ),

                "network_outage_minutes": (
                    10.0
                    + index * 5
                ),

                "dropped_call_rate": (
                    0.01
                    + index * 0.005
                ),

                "average_download_speed_mbps": (
                    180.0
                    - index * 5
                ),

                "coverage_quality_score": (
                    0.90
                    - index * 0.05
                ),

                "customer_satisfaction_score": (
                    satisfaction_a[
                        index
                    ]
                ),

                "nps_score": (
                    nps_a[
                        index
                    ]
                ),

                "retention_offer_received": (
                    index == 3
                ),

                "retention_offer_value": (
                    25.0
                    if index == 3
                    else 0.0
                ),

                "plan_change_1m": 0,

                "device_upgrade_1m": 0,

                "competitor_event_count": (
                    index
                ),

                "competitor_event_count_3m": (
                    2
                    + index
                ),

                "competitor_price_cut_count": (
                    1
                    if index >= 2
                    else 0
                ),

                "competitor_price_cut_count_3m": (
                    index
                ),

                "competitor_promotion_count": (
                    1
                    if index >= 1
                    else 0
                ),

                "competitor_promotion_count_3m": (
                    1
                    + index
                ),

                "competitor_device_offer_count": 1,
                "competitor_bundle_offer_count": 1,

                "competitor_network_improvement_count": (
                    2
                    + index
                ),

                "competitor_outage_count": (
                    1
                    if index == 0
                    else 0
                ),

                "competitor_advertising_count": 2,

                "competitor_price_change_pct_mean": (
                    -0.05
                ),

                "competitor_promotion_depth_mean": (
                    0.20
                ),

                "competitor_device_subsidy_mean": (
                    0.10
                ),

                "competitor_bundle_discount_mean": (
                    0.15
                ),

                "competitor_network_speed_change_mean": (
                    0.10
                ),

                "competitor_outage_minutes_mean": (
                    5.0
                ),

                "competitor_advertising_spend_change_mean": (
                    0.10
                ),

                "competitive_pressure_mean": (
                    0.20
                    + index * 0.05
                ),

                "competitive_pressure_max": (
                    0.30
                    + index * 0.05
                ),

                "price_sensitivity_score": 0.70,

                "promotion_sensitivity_score": 0.60,

                "network_quality_sensitivity_score": (
                    0.65
                ),

                "brand_loyalty_score": (
                    0.40
                ),

                "price_pressure_interaction": 0.10,
                "promotion_pressure_interaction": 0.10,
                "network_pressure_interaction": 0.10,
                "competitive_loyalty_interaction": 0.10,

                "churn_next_30d": (
                    1
                    if index == 3
                    else 0
                ),
            }
        )

    # ---------------------------------------------------------
    # Second customer gives cross-customer protection tests.
    # ---------------------------------------------------------

    for index, month in enumerate(
        months
    ):

        rows.append(
            {
                "customer_id": "C002",
                "month": month,
                "market_id": "M002",
                "state": "TX",
                "customer_segment": "premium",

                "tenure_months_current": (
                    40
                    + index
                ),

                "number_of_lines": 3,

                "device_age_months_current": (
                    6
                    + index
                ),

                "autopay_flag": False,

                "monthly_arpu": 85.0,
                "monthly_bill": 130.0,

                "monthly_bill_change_1m": 0.0,

                "late_payment_count_1m": 0,
                "late_payment_count_3m": 0,
                "payment_failure_count_1m": 0,

                "data_usage_gb": 45.0,
                "data_usage_gb_change_1m": 0.0,

                "voice_usage_minutes": 500.0,
                "sms_usage": 120.0,

                "support_calls_1m": 0,
                "support_calls_3m": 0,

                "network_complaints_1m": 0,
                "network_complaints_3m": 0,

                "network_outage_minutes": 0.0,
                "dropped_call_rate": 0.005,

                "average_download_speed_mbps": 220.0,

                "coverage_quality_score": 0.95,

                "customer_satisfaction_score": 0.90,

                "nps_score": 70.0,

                "retention_offer_received": False,
                "retention_offer_value": 0.0,

                "plan_change_1m": 0,
                "device_upgrade_1m": 0,

                "competitor_event_count": 0,
                "competitor_event_count_3m": 0,

                "competitor_price_cut_count": 0,
                "competitor_price_cut_count_3m": 0,

                "competitor_promotion_count": 0,
                "competitor_promotion_count_3m": 0,

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

                "competitive_pressure_mean": 0.0,
                "competitive_pressure_max": 0.0,

                "price_sensitivity_score": 0.30,
                "promotion_sensitivity_score": 0.30,
                "network_quality_sensitivity_score": 0.30,
                "brand_loyalty_score": 0.90,

                "price_pressure_interaction": 0.0,
                "promotion_pressure_interaction": 0.0,
                "network_pressure_interaction": 0.0,
                "competitive_loyalty_interaction": 0.0,

                "churn_next_30d": 0,
            }
        )

    return pd.DataFrame(
        rows
    )


def test_transform_returns_dataframe():

    frame = make_frame()

    result = ChurnFeatureEngineer().transform(
        frame
    )

    assert isinstance(
        result,
        pd.DataFrame,
    )


def test_transform_preserves_row_count():

    frame = make_frame()

    result = ChurnFeatureEngineer().transform(
        frame
    )

    assert len(
        result
    ) == len(
        frame
    )


def test_original_frame_is_not_modified():

    frame = make_frame()

    original_columns = list(
        frame.columns
    )

    ChurnFeatureEngineer().transform(
        frame
    )

    assert list(
        frame.columns
    ) == original_columns


def test_expected_engineered_features_exist():

    frame = make_frame()

    result = ChurnFeatureEngineer().transform(
        frame
    )

    expected = {
        "support_calls_change_3m",
        "network_complaints_change_3m",
        "satisfaction_change_3m",
        "nps_change_3m",
        "bill_change_3m",
        "data_usage_change_3m",
        "late_payment_trend_3m",

        "billing_stress_score",
        "billing_stress_acceleration",

        "service_friction_score",
        "service_friction_acceleration",

        "customer_engagement_decline_score",

        "competitor_price_pressure_3m",
        "competitor_promotion_pressure_3m",
        "competitor_network_pressure_3m",
        "recent_competitor_event_intensity",
        "competitor_pressure_acceleration",

        "price_sensitivity_competitor_pressure",
        "promotion_sensitivity_competitor_pressure",
        "network_sensitivity_competitor_pressure",
        "satisfaction_support_interaction",
        "low_loyalty_competitive_pressure",
        "billing_stress_price_sensitivity",
        "service_friction_network_sensitivity",
        "engagement_decline_loyalty_interaction",

        "device_age_ratio",
        "device_age_squared",
        "device_lifecycle_stage",
        "old_device_no_upgrade",

        "retention_risk_score",
        "high_risk_without_retention_offer",
    }

    assert expected.issubset(
        result.columns
    )


def test_three_month_trend_is_customer_specific():

    frame = make_frame()

    result = ChurnFeatureEngineer().transform(
        frame
    )

    customer = result[
        result[
            "customer_id"
        ] == "C001"
    ].sort_values(
        "month"
    )

    # January support_calls_3m = 1
    # April support_calls_3m = 5
    # Three-month change = 4

    assert (
        customer[
            "support_calls_change_3m"
        ].iloc[
            3
        ]
        == pytest.approx(
            4.0
        )
    )

    # First three months do not yet have a three-month lag.

    assert (
        customer[
            "support_calls_change_3m"
        ].iloc[
            0
        ]
        == pytest.approx(
            0.0
        )
    )


def test_satisfaction_decline_is_negative():

    frame = make_frame()

    result = ChurnFeatureEngineer().transform(
        frame
    )

    customer = result[
        result[
            "customer_id"
        ] == "C001"
    ].sort_values(
        "month"
    )

    # January = 0.90
    # April   = 0.65

    assert (
        customer[
            "satisfaction_change_3m"
        ].iloc[
            3
        ]
        == pytest.approx(
            -0.25
        )
    )


def test_risk_scores_are_bounded():

    frame = make_frame()

    result = ChurnFeatureEngineer().transform(
        frame
    )

    for column in [
        "billing_stress_score",
        "service_friction_score",
        "customer_engagement_decline_score",
        "retention_risk_score",
    ]:

        assert (
            result[
                column
            ] >= 0.0
        ).all()

        assert (
            result[
                column
            ] <= 1.0
        ).all()


def test_device_lifecycle_stage_is_valid():

    frame = make_frame()

    result = ChurnFeatureEngineer().transform(
        frame
    )

    assert set(
        result[
            "device_lifecycle_stage"
        ].unique()
    ).issubset(
        {
            "new",
            "mid",
            "aging",
            "old",
        }
    )


def test_device_age_ratio_is_bounded():

    frame = make_frame()

    result = ChurnFeatureEngineer().transform(
        frame
    )

    assert (
        result[
            "device_age_ratio"
        ] >= 0.0
    ).all()

    assert (
        result[
            "device_age_ratio"
        ] <= 2.0
    ).all()


def test_competitive_pressure_is_zero_without_exposure():

    frame = make_frame()

    result = ChurnFeatureEngineer().transform(
        frame
    )

    customer = result[
        result[
            "customer_id"
        ] == "C002"
    ]

    assert (
        customer[
            "competitor_price_pressure_3m"
        ]
        == 0.0
    ).all()

    assert (
        customer[
            "competitor_promotion_pressure_3m"
        ]
        == 0.0
    ).all()

    assert (
        customer[
            "recent_competitor_event_intensity"
        ]
        == 0.0
    ).all()


def test_target_is_preserved():

    frame = make_frame()

    result = ChurnFeatureEngineer().transform(
        frame
    )

    expected = (
        frame.sort_values(
            [
                "customer_id",
                "month",
            ]
        )
        [
            "churn_next_30d"
        ]
        .reset_index(
            drop=True
        )
    )

    pd.testing.assert_series_equal(
        result[
            "churn_next_30d"
        ].reset_index(
            drop=True
        ),
        expected,
        check_names=False,
    )


def test_forbidden_leakage_input_is_rejected():

    frame = make_frame()

    frame[
        "churn_probability_true"
    ] = 0.5

    with pytest.raises(
        ValueError,
        match="forbidden leakage",
    ):

        ChurnFeatureEngineer().transform(
            frame
        )


def test_empty_frame_is_rejected():

    frame = make_frame().iloc[
        0:0
    ]

    with pytest.raises(
        ValueError,
        match="empty",
    ):

        ChurnFeatureEngineer().transform(
            frame
        )


def test_missing_identifier_is_rejected():

    frame = make_frame().drop(
        columns=[
            "customer_id",
        ]
    )

    with pytest.raises(
        ValueError,
        match="identifiers",
    ):

        ChurnFeatureEngineer().transform(
            frame
        )


def test_no_nan_created_in_engineered_scores():

    frame = make_frame()

    result = ChurnFeatureEngineer().transform(
        frame
    )

    engineered_scores = [
        "billing_stress_score",
        "service_friction_score",
        "customer_engagement_decline_score",
        "competitor_price_pressure_3m",
        "competitor_promotion_pressure_3m",
        "competitor_network_pressure_3m",
        "recent_competitor_event_intensity",
        "retention_risk_score",
    ]

    assert not result[
        engineered_scores
    ].isna().any().any()