"""
Runtime Churn Sensitivity Service

Step 11B-1
-----------

Purpose
-------
Expose the dedicated low-collinearity churn sensitivity model
to the runtime application layer.

Dependency direction
--------------------

Analysis Agent
      ↓
Analytics Tool
      ↓
ChurnSensitivityService
      ↓
Persisted SensitivityModelArtifact

The service:

- loads an existing sensitivity artifact
- validates the runtime feature contract
- performs controlled additive feature perturbation
- compares baseline and scenario churn probabilities
- returns expected incremental churners
- validates optional expected scenario direction
- never trains or recalibrates models

Important
---------
Results are predictive model sensitivity estimates.

They are NOT causal treatment effects.

The runtime service intentionally does NOT import:

    scripts.synthetic_data.*
"""

from __future__ import annotations

from pathlib import Path
from threading import Lock
from typing import Any

import joblib
import numpy as np
import pandas as pd

from mobile_ai_system.services.analytics.contracts import (
    ChurnSensitivityRecord,
    ChurnSensitivityRequest,
    ChurnSensitivityResult,
)


class ChurnSensitivityService:
    """
    Runtime model-based churn sensitivity service.
    """

    DEFAULT_MODEL_NAME = (
        "churn_sensitivity_model"
    )

    ALLOWED_DIRECTIONS = {
        "increase",
        "decrease",
    }

    UNIT_INTERVAL_FEATURES = {
        "price_sensitivity_score",
        "promotion_sensitivity_score",
        "network_quality_sensitivity_score",
        "brand_loyalty_score",
        "customer_satisfaction_score",
        "retention_risk_score",
    }

    NONNEGATIVE_FEATURES = {
        "competitor_price_pressure_3m",
        "competitor_promotion_pressure_3m",
        "competitor_network_pressure_3m",
        "support_calls_3m",
        "network_complaints_3m",
        "late_payment_count_3m",
        "tenure_months_current",
        "device_age_months_current",
        "number_of_lines",
        "monthly_arpu",
    }

    BOOLEAN_FEATURES = {
        "autopay_flag",
        "retention_offer_received",
    }

    def __init__(
        self,
        model_path: str | Path | None = None,
        model: Any | None = None,
    ) -> None:
        """
        Initialize sensitivity service.

        Parameters
        ----------
        model_path
            Path to persisted sensitivity artifact.

        model
            Optional already-loaded model artifact.

            Useful for:
            - tests
            - dependency injection
            - alternative artifact stores
        """

        if (
            model_path is None
            and model is None
        ):

            raise ValueError(
                "ChurnSensitivityService requires either "
                "model_path or model."
            )

        self._model_path = (
            Path(
                model_path
            )
            if model_path is not None
            else None
        )

        self._model = model

        self._load_lock = Lock()

    # =========================================================
    # Public properties
    # =========================================================

    @property
    def model_path(
        self,
    ) -> Path | None:
        """
        Persisted artifact path when path-based loading is used.
        """

        return self._model_path

    @property
    def is_loaded(
        self,
    ) -> bool:
        """
        Whether artifact is already loaded.
        """

        return (
            self._model
            is not None
        )

    # =========================================================
    # Public API
    # =========================================================

    def analyze(
        self,
        request: ChurnSensitivityRequest,
    ) -> ChurnSensitivityResult:
        """
        Run predictive sensitivity analysis.
        """

        self._validate_request(
            request
        )

        frame = pd.DataFrame(
            request.records
        )

        if frame.empty:

            raise ValueError(
                "Sensitivity request dataset cannot be empty."
            )

        model = self._get_model()

        self._validate_model(
            model
        )

        feature_columns = (
            self.feature_columns()
        )

        self._validate_frame_contract(
            frame=frame,
            feature_columns=feature_columns,
        )

        if request.feature not in (
            feature_columns
        ):

            raise ValueError(
                "Requested sensitivity feature is not part "
                "of the model contract: "
                f"{request.feature}"
            )

        if request.feature in (
            self.BOOLEAN_FEATURES
        ):

            raise ValueError(
                "Boolean sensitivity features must not be "
                "perturbed using additive numeric change: "
                f"{request.feature}"
            )

        # =====================================================
        # Baseline scoring
        # =====================================================

        baseline_probability = (
            self._predict_probability(
                model=model,
                frame=frame,
            )
        )

        # =====================================================
        # Scenario construction
        # =====================================================

        scenario_frame = (
            frame.copy()
        )

        original_values = pd.to_numeric(
            scenario_frame[
                request.feature
            ],
            errors="coerce",
        )

        if original_values.isna().any():

            raise ValueError(
                "Sensitivity feature contains values that "
                "cannot be converted to numeric: "
                f"{request.feature}"
            )

        scenario_values = (
            original_values.astype(
                float
            )
            +
            float(
                request.change
            )
        )

        scenario_values = (
            self._clip_feature(
                feature=(
                    request.feature
                ),
                values=(
                    scenario_values
                ),
            )
        )

        scenario_frame[
            request.feature
        ] = (
            scenario_values
        )

        # =====================================================
        # Scenario scoring
        # =====================================================

        scenario_probability = (
            self._predict_probability(
                model=model,
                frame=scenario_frame,
            )
        )

        probability_change = (
            scenario_probability
            -
            baseline_probability
        )

        baseline_mean = float(
            np.mean(
                baseline_probability
            )
        )

        scenario_mean = float(
            np.mean(
                scenario_probability
            )
        )

        mean_change = float(
            np.mean(
                probability_change
            )
        )

        if baseline_mean > 0.0:

            relative_change = float(
                mean_change
                /
                baseline_mean
            )

        else:

            relative_change = 0.0

        observed_direction = (
            self._direction_from_change(
                mean_change
            )
        )

        direction_validation_passed = (
            self._validate_direction(
                expected=(
                    request.expected_direction
                ),
                observed=(
                    observed_direction
                ),
            )
        )

        # =====================================================
        # Observation-level structured records
        # =====================================================

        records = []

        for index in range(
            len(
                frame
            )
        ):

            base = float(
                baseline_probability[
                    index
                ]
            )

            scenario = float(
                scenario_probability[
                    index
                ]
            )

            delta = float(
                probability_change[
                    index
                ]
            )

            if base > 0.0:

                relative = float(
                    delta
                    /
                    base
                )

            else:

                relative = 0.0

            records.append(
                ChurnSensitivityRecord(
                    row_index=index,
                    baseline_probability=(
                        base
                    ),
                    scenario_probability=(
                        scenario
                    ),
                    probability_change=(
                        delta
                    ),
                    relative_probability_change=(
                        relative
                    ),
                )
            )

        return ChurnSensitivityResult(
            model_name=(
                self._model_name()
            ),

            calibration_method=(
                self._calibration_method()
            ),

            feature=(
                request.feature
            ),

            requested_change=float(
                request.change
            ),

            row_count=len(
                records
            ),

            baseline_mean_probability=(
                baseline_mean
            ),

            scenario_mean_probability=(
                scenario_mean
            ),

            mean_probability_change=(
                mean_change
            ),

            relative_probability_change=(
                relative_change
            ),

            expected_incremental_churners=float(
                np.sum(
                    probability_change
                )
            ),

            expected_direction=(
                request.expected_direction
            ),

            observed_direction=(
                observed_direction
            ),

            direction_validation_passed=(
                direction_validation_passed
            ),

            records=(
                records
            ),
        )

    # =========================================================
    # Feature contract
    # =========================================================

    def feature_columns(
        self,
    ) -> list[str]:
        """
        Return sensitivity-model feature contract.
        """

        model = self._get_model()

        self._validate_model(
            model
        )

        feature_columns = getattr(
            model,
            "feature_columns",
            None,
        )

        if not feature_columns:

            raise ValueError(
                "Sensitivity model exposes an empty "
                "feature contract."
            )

        return [
            str(
                feature
            )
            for feature in feature_columns
        ]

    def competitive_features(
        self,
    ) -> list[str]:
        """
        Return canonical competitive sensitivity coordinates.
        """

        model = self._get_model()

        self._validate_model(
            model
        )

        features = getattr(
            model,
            "competitive_features",
            [],
        )

        return [
            str(
                feature
            )
            for feature in features
        ]

    # =========================================================
    # Prediction
    # =========================================================

    @staticmethod
    def _predict_probability(
        model: Any,
        frame: pd.DataFrame,
    ) -> np.ndarray:
        """
        Return calibrated positive-class probabilities.
        """

        probabilities = model.predict_proba(
            frame
        )

        probabilities = np.asarray(
            probabilities,
            dtype=float,
        )

        if (
            probabilities.ndim != 2
            or probabilities.shape[
                1
            ] < 2
        ):

            raise ValueError(
                "Sensitivity model predict_proba() must "
                "return a two-column probability array."
            )

        positive = probabilities[
            :,
            1,
        ]

        if len(
            positive
        ) != len(
            frame
        ):

            raise ValueError(
                "Sensitivity model returned unexpected "
                "prediction count."
            )

        if not np.isfinite(
            positive
        ).all():

            raise ValueError(
                "Sensitivity model returned NaN or infinite "
                "probabilities."
            )

        if (
            (
                positive
                <
                0.0
            ).any()
            or
            (
                positive
                >
                1.0
            ).any()
        ):

            raise ValueError(
                "Sensitivity probabilities must remain "
                "inside [0, 1]."
            )

        return positive

    # =========================================================
    # Scenario feature clipping
    # =========================================================

    def _clip_feature(
        self,
        feature: str,
        values: pd.Series,
    ) -> pd.Series:
        """
        Preserve obvious feature-domain constraints.
        """

        result = values.astype(
            float
        )

        if feature in (
            self.UNIT_INTERVAL_FEATURES
        ):

            result = result.clip(
                lower=0.0,
                upper=1.0,
            )

        if feature in (
            self.NONNEGATIVE_FEATURES
        ):

            result = result.clip(
                lower=0.0
            )

        return result

    # =========================================================
    # Direction semantics
    # =========================================================

    @staticmethod
    def _direction_from_change(
        change: float,
    ) -> str:
        """
        Convert mean probability change to direction.
        """

        tolerance = 1e-12

        if change > tolerance:

            return "increase"

        if change < -tolerance:

            return "decrease"

        return "unchanged"

    @classmethod
    def _validate_direction(
        cls,
        expected: str | None,
        observed: str,
    ) -> bool | None:
        """
        Validate optional business-direction expectation.
        """

        if expected is None:

            return None

        return (
            expected
            ==
            observed
        )

    # =========================================================
    # Model lifecycle
    # =========================================================

    def _get_model(
        self,
    ) -> Any:
        """
        Lazily load persisted sensitivity artifact.
        """

        if self._model is not None:

            return self._model

        with self._load_lock:

            if self._model is not None:

                return self._model

            if self._model_path is None:

                raise RuntimeError(
                    "No sensitivity model path configured."
                )

            if not self._model_path.exists():

                raise FileNotFoundError(
                    "Sensitivity model artifact not found: "
                    f"{self._model_path}"
                )

            self._model = joblib.load(
                self._model_path
            )

        return self._model

    @staticmethod
    def _validate_model(
        model: Any,
    ) -> None:
        """
        Validate minimum sensitivity-artifact interface.
        """

        if not hasattr(
            model,
            "predict_proba",
        ):

            raise TypeError(
                "Sensitivity artifact must expose "
                "predict_proba()."
            )

        if not hasattr(
            model,
            "feature_columns",
        ):

            raise TypeError(
                "Sensitivity artifact must expose "
                "feature_columns."
            )

        if not hasattr(
            model,
            "competitive_features",
        ):

            raise TypeError(
                "Sensitivity artifact must expose "
                "competitive_features."
            )

        if not hasattr(
            model,
            "sign_validation",
        ):

            raise TypeError(
                "Sensitivity artifact must expose "
                "sign_validation()."
            )

        feature_columns = getattr(
            model,
            "feature_columns",
        )

        if not feature_columns:

            raise ValueError(
                "Sensitivity artifact has an empty "
                "feature contract."
            )

        validation = (
            model.sign_validation()
        )

        if not isinstance(
            validation,
            dict,
        ):

            raise TypeError(
                "Sensitivity sign_validation() must return "
                "a dictionary."
            )

        if not validation.get(
            "passed",
            False,
        ):

            raise ValueError(
                "Sensitivity artifact failed sign "
                "validation. Failed features: "
                f"{validation.get('failed_features', [])}"
            )

    # =========================================================
    # Request validation
    # =========================================================

    @classmethod
    def _validate_request(
        cls,
        request: ChurnSensitivityRequest,
    ) -> None:
        """
        Validate structured sensitivity request.
        """

        if not isinstance(
            request,
            ChurnSensitivityRequest,
        ):

            raise TypeError(
                "analyze expects ChurnSensitivityRequest."
            )

        if not request.records:

            raise ValueError(
                "Sensitivity request must contain at least "
                "one record."
            )

        for index, record in enumerate(
            request.records
        ):

            if not isinstance(
                record,
                dict,
            ):

                raise TypeError(
                    "Sensitivity record at index "
                    f"{index} must be a dictionary."
                )

        if not request.feature:

            raise ValueError(
                "Sensitivity feature cannot be empty."
            )

        if not np.isfinite(
            float(
                request.change
            )
        ):

            raise ValueError(
                "Sensitivity change must be finite."
            )

        if (
            request.expected_direction
            is not None
            and
            request.expected_direction
            not in cls.ALLOWED_DIRECTIONS
        ):

            raise ValueError(
                "expected_direction must be one of: "
                "'increase', 'decrease', or None."
            )

    # =========================================================
    # Frame validation
    # =========================================================

    @staticmethod
    def _validate_frame_contract(
        frame: pd.DataFrame,
        feature_columns: list[str],
    ) -> None:
        """
        Validate model feature contract.
        """

        missing = [
            feature
            for feature in feature_columns
            if feature
            not in frame.columns
        ]

        if missing:

            raise ValueError(
                "Sensitivity dataset missing required "
                "features: "
                f"{missing}"
            )

    # =========================================================
    # Metadata
    # =========================================================

    def _model_name(
        self,
    ) -> str:
        """
        Resolve runtime sensitivity-model name.
        """

        model = self._get_model()

        explicit = getattr(
            model,
            "model_name",
            None,
        )

        if explicit:

            return str(
                explicit
            )

        calibrated_model = getattr(
            model,
            "calibrated_model",
            None,
        )

        if calibrated_model is not None:

            nested_name = getattr(
                calibrated_model,
                "model_name",
                None,
            )

            if nested_name:

                return str(
                    nested_name
                )

        return (
            self.DEFAULT_MODEL_NAME
        )

    def _calibration_method(
        self,
    ) -> str | None:
        """
        Resolve probability calibration method.
        """

        model = self._get_model()

        calibrated_model = getattr(
            model,
            "calibrated_model",
            None,
        )

        if calibrated_model is None:

            method = getattr(
                model,
                "calibration_method",
                None,
            )

        else:

            method = getattr(
                calibrated_model,
                "calibration_method",
                None,
            )

        if method is None:

            return None

        return str(
            method
        )