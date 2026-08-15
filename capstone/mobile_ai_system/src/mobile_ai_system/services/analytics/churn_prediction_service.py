"""
Runtime Churn Prediction Service

Step 11A
--------

Purpose
-------
Expose the calibrated churn prediction model to the
application layer without coupling agents or tools directly
to offline synthetic-data scripts.

Dependency direction
--------------------

Analysis Agent
      ↓
Analytics Tool
      ↓
ChurnPredictionService
      ↓
Persisted calibrated model

The service:

- loads an existing persisted model artifact
- validates feature contracts
- returns calibrated churn probabilities
- optionally derives binary predictions
- never trains or recalibrates models

The service intentionally does NOT import:

    scripts.synthetic_data.*

That package remains the offline training/research layer.
"""

from __future__ import annotations

from pathlib import Path
from threading import Lock
from typing import Any

import joblib
import numpy as np
import pandas as pd

from mobile_ai_system.services.analytics.contracts import (
    ChurnPredictionRecord,
    ChurnPredictionRequest,
    ChurnPredictionResult,
)


class ChurnPredictionService:
    """
    Runtime calibrated churn prediction service.
    """

    DEFAULT_MODEL_NAME = (
        "calibrated_churn_prediction_model"
    )

    def __init__(
        self,
        model_path: str | Path | None = None,
        model: Any | None = None,
    ) -> None:
        """
        Initialize service.

        Parameters
        ----------
        model_path
            Path to persisted joblib churn model.

        model
            Optional already-loaded model.

            Primarily useful for:

            - dependency injection
            - tests
            - alternative artifact stores

        Notes
        -----
        At least one of model_path or model must be supplied.

        If model is supplied, lazy disk loading is skipped.
        """

        if (
            model_path is None
            and model is None
        ):

            raise ValueError(
                "ChurnPredictionService requires either "
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

        # -----------------------------------------------------
        # Service instances may eventually be reused across
        # agent calls. Lazy model loading must therefore be
        # thread-safe.
        # -----------------------------------------------------

        self._load_lock = Lock()

    # =========================================================
    # Public properties
    # =========================================================

    @property
    def model_path(
        self,
    ) -> Path | None:
        """
        Persisted model path, when path-based loading is used.
        """

        return self._model_path

    @property
    def is_loaded(
        self,
    ) -> bool:
        """
        Whether model artifact is already loaded.
        """

        return (
            self._model
            is not None
        )

    # =========================================================
    # Public prediction API
    # =========================================================

    def predict(
        self,
        request: ChurnPredictionRequest,
    ) -> ChurnPredictionResult:
        """
        Predict calibrated churn probability.

        Parameters
        ----------
        request
            Structured prediction request.

        Returns
        -------
        ChurnPredictionResult
            Structured prediction result.
        """

        self._validate_request(
            request
        )

        frame = pd.DataFrame(
            request.records
        )

        probabilities = (
            self.predict_frame(
                frame
            )
        )

        predictions = [
            ChurnPredictionRecord(
                row_index=index,
                churn_probability=float(
                    probability
                ),
                predicted_churn=bool(
                    probability
                    >= request.threshold
                ),
            )
            for index, probability
            in enumerate(
                probabilities
            )
        ]

        return ChurnPredictionResult(
            model_name=(
                self._model_name()
            ),

            calibration_method=(
                self._calibration_method()
            ),

            feature_count=len(
                self.feature_columns()
            ),

            row_count=len(
                predictions
            ),

            threshold=float(
                request.threshold
            ),

            predictions=(
                predictions
            ),

            mean_churn_probability=float(
                np.mean(
                    probabilities
                )
            ),

            minimum_churn_probability=float(
                np.min(
                    probabilities
                )
            ),

            maximum_churn_probability=float(
                np.max(
                    probabilities
                )
            ),
        )

    def predict_frame(
        self,
        frame: pd.DataFrame,
    ) -> np.ndarray:
        """
        Predict calibrated positive-class churn probability
        for a DataFrame.

        This method is useful internally for other analytics
        services that already operate on DataFrames.

        Returns
        -------
        np.ndarray
            One calibrated churn probability per row.
        """

        if not isinstance(
            frame,
            pd.DataFrame,
        ):

            raise TypeError(
                "predict_frame expects a pandas DataFrame."
            )

        if frame.empty:

            raise ValueError(
                "Prediction dataset cannot be empty."
            )

        model = (
            self._get_model()
        )

        self._validate_model(
            model
        )

        feature_columns = (
            self.feature_columns()
        )

        missing = [
            feature
            for feature in feature_columns
            if feature
            not in frame.columns
        ]

        if missing:

            raise ValueError(
                "Prediction dataset missing required "
                "model features: "
                f"{missing}"
            )

        # -----------------------------------------------------
        # Preserve the persisted model's feature order.
        #
        # Extra columns are intentionally allowed because
        # application state may contain identifiers, metadata,
        # or other features unused by this model.
        # -----------------------------------------------------

        x = frame[
            feature_columns
        ]

        probabilities = (
            model.predict_proba(
                x
            )
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
                "Churn model predict_proba() must return "
                "a two-dimensional class-probability array."
            )

        positive_probability = (
            probabilities[
                :,
                1,
            ]
        )

        if len(
            positive_probability
        ) != len(
            frame
        ):

            raise ValueError(
                "Churn model returned an unexpected "
                "number of predictions."
            )

        if not np.isfinite(
            positive_probability
        ).all():

            raise ValueError(
                "Churn model returned NaN or infinite "
                "probabilities."
            )

        if (
            (
                positive_probability
                <
                0.0
            ).any()
            or
            (
                positive_probability
                >
                1.0
            ).any()
        ):

            raise ValueError(
                "Churn probabilities must be between "
                "0 and 1."
            )

        return positive_probability

    # =========================================================
    # Feature contract
    # =========================================================

    def feature_columns(
        self,
    ) -> list[str]:
        """
        Return persisted model feature contract.
        """

        model = (
            self._get_model()
        )

        self._validate_model(
            model
        )

        feature_columns = getattr(
            model,
            "feature_columns",
            None,
        )

        if feature_columns is None:

            raise ValueError(
                "Persisted churn model does not expose "
                "feature_columns."
            )

        return [
            str(
                feature
            )
            for feature in feature_columns
        ]

    # =========================================================
    # Model lifecycle
    # =========================================================

    def _get_model(
        self,
    ) -> Any:
        """
        Lazily load model artifact.
        """

        if self._model is not None:

            return self._model

        with self._load_lock:

            if self._model is not None:

                return self._model

            if self._model_path is None:

                raise RuntimeError(
                    "No churn model path configured."
                )

            if not (
                self._model_path.exists()
            ):

                raise FileNotFoundError(
                    "Churn model artifact not found: "
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
        Validate minimum runtime model interface.
        """

        if not hasattr(
            model,
            "predict_proba",
        ):

            raise TypeError(
                "Persisted churn model must expose "
                "predict_proba()."
            )

        if not hasattr(
            model,
            "feature_columns",
        ):

            raise TypeError(
                "Persisted churn model must expose "
                "feature_columns."
            )

        feature_columns = getattr(
            model,
            "feature_columns",
        )

        if not feature_columns:

            raise ValueError(
                "Persisted churn model has an empty "
                "feature contract."
            )

    # =========================================================
    # Request validation
    # =========================================================

    @staticmethod
    def _validate_request(
        request: ChurnPredictionRequest,
    ) -> None:
        """
        Validate structured request.
        """

        if not isinstance(
            request,
            ChurnPredictionRequest,
        ):

            raise TypeError(
                "predict expects ChurnPredictionRequest."
            )

        if not request.records:

            raise ValueError(
                "Prediction request must contain at least "
                "one record."
            )

        if not (
            0.0
            <= request.threshold
            <= 1.0
        ):

            raise ValueError(
                "Prediction threshold must be between "
                "0 and 1."
            )

        for index, record in enumerate(
            request.records
        ):

            if not isinstance(
                record,
                dict,
            ):

                raise TypeError(
                    "Prediction record at index "
                    f"{index} must be a dictionary."
                )

    # =========================================================
    # Metadata
    # =========================================================

    def _model_name(
        self,
    ) -> str:
        """
        Resolve runtime model name.
        """

        model = (
            self._get_model()
        )

        explicit_name = getattr(
            model,
            "model_name",
            None,
        )

        if explicit_name:

            return str(
                explicit_name
            )

        return (
            self.DEFAULT_MODEL_NAME
        )

    def _calibration_method(
        self,
    ) -> str | None:
        """
        Resolve persisted calibration metadata.
        """

        model = (
            self._get_model()
        )

        calibration_method = getattr(
            model,
            "calibration_method",
            None,
        )

        if calibration_method is None:

            return None

        return str(
            calibration_method
        )