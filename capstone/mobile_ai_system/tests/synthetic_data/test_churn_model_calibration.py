"""
Tests for Synthetic Customer Churn Model Calibration.

Post-MVP Machine Learning Environment
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from sklearn.linear_model import LogisticRegression

from scripts.synthetic_data.churn_model_calibration import (
    CalibratedProbabilityModel,
    ChurnModelCalibrator,
    IsotonicProbabilityCalibrator,
    PlattProbabilityCalibrator,
)


# =============================================================
# Test helpers
# =============================================================


def make_dataset(
    start_date: str,
    months: int,
    rows_per_month: int = 400,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Create a small deterministic temporal churn dataset.

    The target is intentionally imbalanced and related to a
    few observable features so calibration tests remain fast
    but meaningful.
    """

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

    for month_index, month in enumerate(
        dates
    ):

        for _ in range(
            rows_per_month
        ):

            counter += 1

            service_friction = (
                rng.beta(
                    2.0,
                    5.0,
                )
            )

            billing_stress = (
                rng.beta(
                    1.5,
                    6.0,
                )
            )

            loyalty = (
                rng.beta(
                    4.0,
                    2.0,
                )
            )

            competitive_pressure = (
                rng.beta(
                    2.0,
                    6.0,
                )
            )

            risk_logit = (
                -4.30
                + 1.60
                * service_friction
                + 1.10
                * billing_stress
                - 0.90
                * loyalty
                + 0.70
                * competitive_pressure
                + 0.05
                * month_index
            )

            probability = (
                1.0
                /
                (
                    1.0
                    +
                    np.exp(
                        -risk_logit
                    )
                )
            )

            target = int(
                rng.random()
                <
                probability
            )

            rows.append(
                {
                    "customer_id": (
                        f"C{counter:08d}"
                    ),

                    "month": month,

                    "market_id": (
                        f"M{rng.integers(1, 10):03d}"
                    ),

                    "service_friction_score": (
                        service_friction
                    ),

                    "billing_stress_score": (
                        billing_stress
                    ),

                    "brand_loyalty_score": (
                        loyalty
                    ),

                    "competitive_pressure_mean": (
                        competitive_pressure
                    ),

                    "support_calls_3m": (
                        rng.poisson(
                            1.0
                            + 3.0
                            * service_friction
                        )
                    ),

                    "network_complaints_3m": (
                        rng.poisson(
                            0.5
                            + 2.5
                            * service_friction
                        )
                    ),

                    "late_payment_count_3m": (
                        rng.poisson(
                            0.3
                            + 2.0
                            * billing_stress
                        )
                    ),

                    "customer_satisfaction_score": (
                        np.clip(
                            0.95
                            - 0.55
                            * service_friction
                            + rng.normal(
                                0.0,
                                0.05,
                            ),
                            0.0,
                            1.0,
                        )
                    ),

                    "retention_risk_score": (
                        np.clip(
                            0.45
                            * service_friction
                            + 0.30
                            * billing_stress
                            + 0.15
                            * (
                                1.0
                                - loyalty
                            )
                            + 0.10
                            * competitive_pressure,
                            0.0,
                            1.0,
                        )
                    ),

                    "churn_next_30d": (
                        target
                    ),
                }
            )

    return pd.DataFrame(
        rows
    )


def build_validation_and_test():
    """
    Build chronologically ordered validation/test datasets.
    """

    validation = make_dataset(
        start_date="2025-07-01",
        months=3,
        rows_per_month=500,
        seed=42,
    )

    test = make_dataset(
        start_date="2025-10-01",
        months=2,
        rows_per_month=500,
        seed=43,
    )

    return (
        validation,
        test,
    )


def feature_columns(
    frame: pd.DataFrame,
) -> list[str]:
    """
    Return model predictor columns used by test models.
    """

    excluded = {
        "customer_id",
        "month",
        "market_id",
        "churn_next_30d",
    }

    return [
        column
        for column in frame.columns
        if column not in excluded
    ]


def build_base_models():
    """
    Train small base models that expose predict_proba().

    Two logistic models are sufficient for calibration unit
    tests. The production workflow still loads the actual
    Step-9C logistic and histogram-boosting artifacts.
    """

    validation, test = (
        build_validation_and_test()
    )

    combined = pd.concat(
        [
            validation,
            test,
        ],
        ignore_index=True,
    )

    features = (
        feature_columns(
            combined
        )
    )

    x = combined[
        features
    ]

    y = combined[
        "churn_next_30d"
    ].astype(
        int
    )

    logistic = LogisticRegression(
        max_iter=500,
        class_weight="balanced",
    )

    logistic.fit(
        x,
        y,
    )

    # ---------------------------------------------------------
    # A second probability model stands in for the production
    # HistogramGradientBoosting model in unit tests.
    # ---------------------------------------------------------

    second_model = LogisticRegression(
        max_iter=500,
    )

    second_model.fit(
        x,
        y,
    )

    return (
        validation,
        test,
        logistic,
        second_model,
    )


# =============================================================
# Platt calibration
# =============================================================


def test_platt_calibrator_returns_probabilities():

    probabilities = np.array(
        [
            0.10,
            0.20,
            0.30,
            0.70,
            0.80,
            0.90,
        ]
    )

    y_true = np.array(
        [
            0,
            0,
            0,
            1,
            1,
            1,
        ]
    )

    calibrator = (
        PlattProbabilityCalibrator()
        .fit(
            probabilities,
            y_true,
        )
    )

    calibrated = calibrator.predict(
        probabilities
    )

    assert calibrated.shape == (
        len(
            probabilities
        ),
    )

    assert (
        calibrated > 0.0
    ).all()

    assert (
        calibrated < 1.0
    ).all()


def test_platt_calibrator_requires_fit():

    calibrator = (
        PlattProbabilityCalibrator()
    )

    with pytest.raises(
        RuntimeError,
        match="not been fitted",
    ):

        calibrator.predict(
            np.array(
                [
                    0.1,
                    0.2,
                ]
            )
        )


# =============================================================
# Isotonic calibration
# =============================================================


def test_isotonic_calibrator_returns_probabilities():

    probabilities = np.array(
        [
            0.05,
            0.10,
            0.15,
            0.40,
            0.60,
            0.80,
            0.90,
        ]
    )

    y_true = np.array(
        [
            0,
            0,
            0,
            0,
            1,
            1,
            1,
        ]
    )

    calibrator = (
        IsotonicProbabilityCalibrator()
        .fit(
            probabilities,
            y_true,
        )
    )

    calibrated = calibrator.predict(
        probabilities
    )

    assert calibrated.shape == (
        len(
            probabilities
        ),
    )

    assert (
        calibrated > 0.0
    ).all()

    assert (
        calibrated < 1.0
    ).all()


def test_isotonic_is_monotonic():

    probabilities = np.array(
        [
            0.05,
            0.10,
            0.20,
            0.30,
            0.50,
            0.70,
            0.90,
        ]
    )

    y_true = np.array(
        [
            0,
            0,
            0,
            1,
            0,
            1,
            1,
        ]
    )

    calibrator = (
        IsotonicProbabilityCalibrator()
        .fit(
            probabilities,
            y_true,
        )
    )

    calibrated = (
        calibrator.predict(
            probabilities
        )
    )

    assert (
        np.diff(
            calibrated
        ) >= -1e-12
    ).all()


def test_isotonic_calibrator_requires_fit():

    calibrator = (
        IsotonicProbabilityCalibrator()
    )

    with pytest.raises(
        RuntimeError,
        match="not been fitted",
    ):

        calibrator.predict(
            np.array(
                [
                    0.1,
                    0.2,
                ]
            )
        )


# =============================================================
# Temporal validation split
# =============================================================


def test_validation_period_is_split_temporally():

    validation, _ = (
        build_validation_and_test()
    )

    calibrator = (
        ChurnModelCalibrator()
    )

    fit, selection = (
        calibrator
        ._split_validation_period(
            validation
        )
    )

    assert (
        fit[
            "month"
        ].max()
        <
        selection[
            "month"
        ].min()
    )


def test_final_validation_month_is_selection_period():

    validation, _ = (
        build_validation_and_test()
    )

    calibrator = (
        ChurnModelCalibrator()
    )

    _, selection = (
        calibrator
        ._split_validation_period(
            validation
        )
    )

    assert (
        selection[
            "month"
        ].nunique()
        == 1
    )

    assert (
        selection[
            "month"
        ].iloc[
            0
        ]
        ==
        validation[
            "month"
        ].max()
    )


# =============================================================
# Probability metrics
# =============================================================


def test_probability_metrics_are_valid():

    y_true = np.array(
        [
            0,
            0,
            0,
            1,
            0,
            1,
            0,
            1,
        ]
    )

    probabilities = np.array(
        [
            0.05,
            0.10,
            0.20,
            0.60,
            0.15,
            0.70,
            0.30,
            0.80,
        ]
    )

    metrics = (
        ChurnModelCalibrator
        ._evaluate_probability_model(
            y_true=y_true,
            probabilities=(
                probabilities
            ),
        )
    )

    assert (
        0.0
        <= metrics[
            "roc_auc"
        ]
        <= 1.0
    )

    assert (
        0.0
        <= metrics[
            "pr_auc"
        ]
        <= 1.0
    )

    assert (
        0.0
        <= metrics[
            "brier_score"
        ]
        <= 1.0
    )

    assert (
        metrics[
            "log_loss"
        ]
        >= 0.0
    )

    assert (
        0.0
        <= metrics[
            "expected_calibration_error"
        ]
        <= 1.0
    )


def test_ece_is_zero_for_perfect_binary_predictions():

    y_true = np.array(
        [
            0,
            0,
            1,
            1,
        ]
    )

    probabilities = np.array(
        [
            0.0,
            0.0,
            1.0,
            1.0,
        ]
    )

    ece = (
        ChurnModelCalibrator
        ._expected_calibration_error(
            y_true=y_true,
            probabilities=(
                probabilities
            ),
            bins=10,
        )
    )

    assert ece < 1e-5


# =============================================================
# Calibration table
# =============================================================


def test_calibration_table_preserves_row_count():

    y_true = np.array(
        [
            0,
            0,
            0,
            0,
            1,
            0,
            1,
            1,
            0,
            1,
        ]
    )

    probabilities = np.linspace(
        0.05,
        0.50,
        len(
            y_true
        ),
    )

    table = (
        ChurnModelCalibrator
        ._calibration_table(
            y_true=y_true,
            probabilities=(
                probabilities
            ),
            bins=5,
        )
    )

    total_rows = sum(
        row[
            "rows"
        ]
        for row in table
    )

    assert total_rows == len(
        y_true
    )


# =============================================================
# Calibrated model wrapper
# =============================================================


def test_calibrated_model_predict_proba():

    validation, test, logistic, _ = (
        build_base_models()
    )

    features = (
        feature_columns(
            validation
        )
    )

    raw_probability = (
        logistic.predict_proba(
            validation[
                features
            ]
        )[
            :,
            1,
        ]
    )

    calibrator = (
        PlattProbabilityCalibrator()
        .fit(
            probabilities=(
                raw_probability
            ),
            y_true=(
                validation[
                    "churn_next_30d"
                ]
                .astype(
                    int
                )
                .to_numpy()
            ),
        )
    )

    model = (
        CalibratedProbabilityModel(
            base_model=(
                logistic
            ),
            calibrator=(
                calibrator
            ),
            calibration_method=(
                "platt"
            ),
            feature_columns=(
                features
            ),
        )
    )

    probabilities = (
        model.predict_proba(
            test
        )
    )

    assert probabilities.shape == (
        len(
            test
        ),
        2,
    )

    assert np.allclose(
        probabilities.sum(
            axis=1
        ),
        1.0,
    )

    assert (
        probabilities >= 0.0
    ).all()

    assert (
        probabilities <= 1.0
    ).all()


# =============================================================
# Full calibration workflow
# =============================================================


def test_calibrate_returns_result():

    (
        validation,
        test,
        logistic,
        second_model,
    ) = build_base_models()

    calibrator = (
        ChurnModelCalibrator(
            use_engineered=False
        )
    )

    output = calibrator.calibrate(
        validation=validation,
        test=test,
        logistic_model=logistic,
        gradient_boosting_model=(
            second_model
        ),
    )

    assert "result" in output

    assert (
        "calibrated_model"
        in output
    )


def test_selected_method_is_valid():

    (
        validation,
        test,
        logistic,
        second_model,
    ) = build_base_models()

    result = (
        ChurnModelCalibrator(
            use_engineered=False
        )
        .calibrate(
            validation=validation,
            test=test,
            logistic_model=logistic,
            gradient_boosting_model=(
                second_model
            ),
        )[
            "result"
        ]
    )

    assert (
        result[
            "selected_calibration_method"
        ]
        in {
            "platt",
            "isotonic",
        }
    )


def test_selection_results_include_all_candidates():

    (
        validation,
        test,
        logistic,
        second_model,
    ) = build_base_models()

    result = (
        ChurnModelCalibrator(
            use_engineered=False
        )
        .calibrate(
            validation=validation,
            test=test,
            logistic_model=logistic,
            gradient_boosting_model=(
                second_model
            ),
        )[
            "result"
        ]
    )

    assert set(
        result[
            "selection_results"
        ].keys()
    ) == {
        "raw_logistic",
        "raw_hist_gradient_boosting",
        "platt",
        "isotonic",
    }


def test_test_results_include_calibrated_model():

    (
        validation,
        test,
        logistic,
        second_model,
    ) = build_base_models()

    result = (
        ChurnModelCalibrator(
            use_engineered=False
        )
        .calibrate(
            validation=validation,
            test=test,
            logistic_model=logistic,
            gradient_boosting_model=(
                second_model
            ),
        )[
            "result"
        ]
    )

    assert (
        "calibrated_logistic"
        in result[
            "test_results"
        ]
    )


def test_calibrated_test_probabilities_match_output_rate_reasonably():

    (
        validation,
        test,
        logistic,
        second_model,
    ) = build_base_models()

    result = (
        ChurnModelCalibrator(
            use_engineered=False
        )
        .calibrate(
            validation=validation,
            test=test,
            logistic_model=logistic,
            gradient_boosting_model=(
                second_model
            ),
        )[
            "result"
        ]
    )

    metrics = (
        result[
            "test_results"
        ][
            "calibrated_logistic"
        ]
    )

    difference = abs(
        metrics[
            "mean_predicted_probability"
        ]
        -
        metrics[
            "observed_positive_rate"
        ]
    )

    # Calibration should bring average predicted prevalence
    # into the same broad range as observed prevalence.
    #
    # The synthetic unit-test sample is intentionally small,
    # so this tolerance should not be overly strict.

    assert difference < 0.05


def test_calibrated_brier_is_better_than_raw_balanced_logistic():

    (
        validation,
        test,
        logistic,
        second_model,
    ) = build_base_models()

    result = (
        ChurnModelCalibrator(
            use_engineered=False
        )
        .calibrate(
            validation=validation,
            test=test,
            logistic_model=logistic,
            gradient_boosting_model=(
                second_model
            ),
        )[
            "result"
        ]
    )

    raw_brier = (
        result[
            "test_results"
        ][
            "raw_logistic"
        ][
            "brier_score"
        ]
    )

    calibrated_brier = (
        result[
            "test_results"
        ][
            "calibrated_logistic"
        ][
            "brier_score"
        ]
    )

    assert calibrated_brier < raw_brier


# =============================================================
# Input validation
# =============================================================


def test_rejects_temporal_overlap():

    validation, test = (
        build_validation_and_test()
    )

    # Move test into validation period.

    test = test.copy()

    test[
        "month"
    ] = pd.Timestamp(
        "2025-08-01"
    )

    calibrator = (
        ChurnModelCalibrator()
    )

    with pytest.raises(
        ValueError,
        match="before the test period",
    ):

        calibrator._validate_inputs(
            validation=validation,
            test=test,
        )


def test_rejects_feature_schema_mismatch():

    validation, test = (
        build_validation_and_test()
    )

    test = test.drop(
        columns=[
            "service_friction_score",
        ]
    )

    calibrator = (
        ChurnModelCalibrator()
    )

    with pytest.raises(
        ValueError,
        match="schemas",
    ):

        calibrator._validate_inputs(
            validation=validation,
            test=test,
        )