"""
Tests for dedicated churn sensitivity model.

Step 10F
--------

Validates:

- reduced sensitivity feature contract
- redundant composites are excluded
- model training
- calibrated probability behavior
- expected coefficient signs
- artifact serialization contract
- test metrics
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from scripts.synthetic_data.churn_probability_models import (
    CalibratedProbabilityModel,
    SensitivityModelArtifact,
)

from scripts.synthetic_data.churn_sensitivity_model import (
    ChurnSensitivityModelTrainer,
)


# =============================================================
# Fixtures / helpers
# =============================================================


@pytest.fixture(scope="module")
def trainer():
    """
    Shared trainer.
    """

    return ChurnSensitivityModelTrainer()


@pytest.fixture(scope="module")
def training_output(
    trainer,
):
    """
    Train the sensitivity model once for this test module.

    The real engineered synthetic datasets are used because
    Step 10F is intended to behave as an integration/regression
    test for the post-MVP synthetic analytics environment.
    """

    return trainer.train()


# =============================================================
# Feature-contract tests
# =============================================================


def test_sensitivity_feature_count(
    trainer,
):
    """
    Current reduced sensitivity model should contain
    exactly 18 features.
    """

    assert len(
        trainer.SENSITIVITY_FEATURES
    ) == 18


def test_redundant_composites_excluded(
    trainer,
):
    """
    Composite variables responsible for suppression effects
    must remain excluded.
    """

    assert (
        "billing_stress_score"
        not in trainer.SENSITIVITY_FEATURES
    )

    assert (
        "service_friction_score"
        not in trainer.SENSITIVITY_FEATURES
    )


def test_competitive_features_are_canonical(
    trainer,
):
    """
    Sensitivity model should use canonical competitive
    pressure coordinates.
    """

    assert set(
        trainer.COMPETITIVE_FEATURES
    ) == {
        "competitor_price_pressure_3m",
        "competitor_promotion_pressure_3m",
        "competitor_network_pressure_3m",
    }


def test_competitive_features_in_model_features(
    trainer,
):
    """
    Every competitive intervention coordinate must be part
    of the sensitivity feature contract.
    """

    assert set(
        trainer.COMPETITIVE_FEATURES
    ).issubset(
        set(
            trainer.SENSITIVITY_FEATURES
        )
    )


def test_expected_sign_features_in_contract(
    trainer,
):
    """
    Sign-validation features must exist in model contract.
    """

    assert set(
        trainer.EXPECTED_SIGNS
    ).issubset(
        set(
            trainer.SENSITIVITY_FEATURES
        )
    )


# =============================================================
# Training-result tests
# =============================================================


def test_train_returns_expected_objects(
    training_output,
):
    """
    Training should return structured results and models.
    """

    assert isinstance(
        training_output,
        dict,
    )

    assert {
        "result",
        "artifact",
        "base_model",
        "calibrated_model",
        "coefficients",
    }.issubset(
        training_output
    )


def test_artifact_type(
    training_output,
):
    """
    Sensitivity artifact should use stable serializable type.
    """

    assert isinstance(
        training_output[
            "artifact"
        ],
        SensitivityModelArtifact,
    )


def test_calibrated_model_type(
    training_output,
):
    """
    Artifact should contain the stable calibrated wrapper.
    """

    assert isinstance(
        training_output[
            "calibrated_model"
        ],
        CalibratedProbabilityModel,
    )


def test_result_feature_count(
    training_output,
):
    """
    Published feature count should equal actual contract.
    """

    result = training_output[
        "result"
    ]

    assert (
        result[
            "feature_count"
        ]
        ==
        len(
            result[
                "features"
            ]
        )
    )

    assert (
        result[
            "feature_count"
        ]
        == 18
    )


# =============================================================
# Probability tests
# =============================================================


def test_calibrated_test_metrics_bounded(
    training_output,
):
    """
    Ranking and probability metrics should remain valid.
    """

    metrics = (
        training_output[
            "result"
        ][
            "test"
        ][
            "calibrated_metrics"
        ]
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


def test_calibration_improves_brier_score(
    training_output,
):
    """
    Platt calibration should materially improve probability
    quality relative to balanced raw logistic probabilities.
    """

    result = training_output[
        "result"
    ]

    raw = (
        result[
            "test"
        ][
            "raw_metrics"
        ][
            "brier_score"
        ]
    )

    calibrated = (
        result[
            "test"
        ][
            "calibrated_metrics"
        ][
            "brier_score"
        ]
    )

    assert (
        calibrated
        <
        raw
    )


def test_calibrated_probability_matches_prevalence_reasonably(
    training_output,
):
    """
    Mean calibrated probability should be much closer to
    observed prevalence than raw balanced-logistic output.
    """

    result = training_output[
        "result"
    ]

    observed = (
        result[
            "test"
        ][
            "positive_rate"
        ]
    )

    raw_predicted = (
        result[
            "test"
        ][
            "raw_metrics"
        ][
            "mean_predicted_probability"
        ]
    )

    calibrated_predicted = (
        result[
            "test"
        ][
            "calibrated_metrics"
        ][
            "mean_predicted_probability"
        ]
    )

    raw_error = abs(
        raw_predicted
        -
        observed
    )

    calibrated_error = abs(
        calibrated_predicted
        -
        observed
    )

    assert (
        calibrated_error
        <
        raw_error
    )


# =============================================================
# Sign-validation tests
# =============================================================


def test_sign_validation_passes(
    training_output,
):
    """
    Dedicated sensitivity model must satisfy its declared
    coefficient-direction contract.
    """

    result = training_output[
        "result"
    ]

    assert (
        result[
            "sign_validation_passed"
        ]
        is True
    )

    validation = result[
        "sign_validation"
    ]

    assert validation[
        "failed_count"
    ] == 0

    assert validation[
        "failed_features"
    ] == []


@pytest.mark.parametrize(
    "feature",
    [
        "competitor_price_pressure_3m",
        "competitor_promotion_pressure_3m",
        "network_complaints_3m",
        "support_calls_3m",
        "late_payment_count_3m",
    ],
)
def test_expected_positive_coefficients(
    training_output,
    feature,
):
    """
    Adverse pressure/service variables must have positive
    conditional model signs.
    """

    coefficients = (
        training_output[
            "coefficients"
        ]
    )

    row = coefficients[
        coefficients[
            "feature"
        ]
        == feature
    ]

    assert not row.empty

    assert (
        float(
            row[
                "coefficient"
            ].iloc[
                0
            ]
        )
        >
        0.0
    )


@pytest.mark.parametrize(
    "feature",
    [
        "customer_satisfaction_score",
        "brand_loyalty_score",
        "autopay_flag",
        "retention_offer_received",
    ],
)
def test_expected_negative_coefficients(
    training_output,
    feature,
):
    """
    Protective variables must have negative conditional
    model signs.
    """

    coefficients = (
        training_output[
            "coefficients"
        ]
    )

    row = coefficients[
        coefficients[
            "feature"
        ]
        == feature
    ]

    assert not row.empty

    assert (
        float(
            row[
                "coefficient"
            ].iloc[
                0
            ]
        )
        <
        0.0
    )


def test_artifact_internal_sign_validation(
    training_output,
):
    """
    Serialized artifact should independently reproduce sign
    validation.
    """

    artifact = training_output[
        "artifact"
    ]

    result = (
        artifact.sign_validation()
    )

    assert result[
        "passed"
    ] is True

    assert result[
        "failed_count"
    ] == 0


# =============================================================
# Coefficient-table tests
# =============================================================


def test_coefficient_table_unique_features(
    training_output,
):
    """
    Reduced numerical/boolean model should have exactly one
    coefficient representation per raw sensitivity feature.
    """

    coefficients = (
        training_output[
            "coefficients"
        ]
    )

    assert (
        coefficients[
            "feature"
        ].is_unique
    )


def test_coefficient_values_finite(
    training_output,
):
    """
    Coefficients must contain no NaN or infinite values.
    """

    coefficients = (
        training_output[
            "coefficients"
        ][
            "coefficient"
        ]
        .to_numpy(
            dtype=float
        )
    )

    assert np.isfinite(
        coefficients
    ).all()