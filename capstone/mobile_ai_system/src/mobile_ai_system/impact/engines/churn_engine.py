"""
Customer Churn Engine

Architecture v2.3 (Frozen MVP)

Responsibilities
----------------
- Delegate feature construction to FeatureBuilder.
- Execute event-level churn inference when a compatible
  legacy model artifact is available.
- Delegate calibrated customer-level prediction to
  ChurnPredictionService when explicitly configured.
- Gracefully fall back when the optional event-level
  model artifact is unavailable.
- Produce ChurnResult.

Important Release 0.1 boundary
------------------------------
The existing Impact Layer operates on event-level features
built from InformationResult.

The calibrated ChurnPredictionService operates on a
customer-level engineered feature schema.

Those two feature spaces are not interchangeable.

Therefore the normal frozen Impact pipeline should use the
legacy/event-level backend.

If no compatible event-level model artifact exists, the
engine returns an explicit deterministic fallback result
rather than fabricating customer-level features.

The fallback is marked clearly in ChurnResult.metadata.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from mobile_ai_system.application.models.information_result import (
    InformationResult,
)
from mobile_ai_system.impact.builders import (
    FeatureBuilder,
)
from mobile_ai_system.impact.interfaces.i_churn_engine import (
    IChurnEngine,
)
from mobile_ai_system.impact.models.churn_result import (
    ChurnResult,
)
from mobile_ai_system.impact.models.feature_vector import (
    FeatureVector,
)
from mobile_ai_system.services.analytics import (
    ChurnPredictionRequest,
    ChurnPredictionService,
)


class ChurnEngine(IChurnEngine):
    """
    Default implementation of IChurnEngine.

    Runtime modes
    -------------

    Event-level Impact path:

        InformationResult
            ↓
        FeatureBuilder
            ↓
        FeatureVector
            ↓
        optional legacy event-level model
            ↓
        ChurnResult

    Explicit customer-analytics path:

        FeatureVector
            ↓
        ChurnPredictionService
            ↓
        ChurnResult

    Release 0.1 normally uses the first path.

    If its event-level model is unavailable, the engine
    produces a deterministic fallback ChurnResult so the
    remainder of the MVP pipeline can continue.
    """

    DEFAULT_THRESHOLD = 0.50

    FALLBACK_PROBABILITY = 0.0

    # =========================================================
    # Construction
    # =========================================================

    def __init__(
        self,
        model_path: str | Path | None = None,
        feature_builder: FeatureBuilder | None = None,
        prediction_service: ChurnPredictionService | None = None,
    ) -> None:
        """
        Initialize the churn engine.

        Parameters
        ----------
        model_path
            Optional event-level model artifact.

        feature_builder
            Impact-Layer FeatureBuilder.

        prediction_service
            Optional calibrated customer-level prediction
            service.

            This should only be supplied when the caller can
            provide the service's complete customer-level
            feature contract.

        Notes
        -----
        Unlike the earlier implementation, Release 0.1 does
        not require model_path to exist.

        A missing event-level model activates an explicit
        fallback path.
        """

        self._model_path = (
            Path(
                model_path
            )
            if model_path is not None
            else None
        )

        self._model: Any | None = None

        self._prediction_service = (
            prediction_service
        )

        self._feature_builder = (
            feature_builder
            if feature_builder is not None
            else FeatureBuilder()
        )

        # -----------------------------------------------------
        # Model lifecycle state
        # -----------------------------------------------------

        self._load_attempted = False

        self._model_available = False

        self._model_load_error: str | None = None

    # =========================================================
    # Model identity
    # =========================================================

    @property
    def model_name(self) -> str:
        """
        Return the configured model name.
        """

        if (
            self._prediction_service
            is not None
        ):
            return (
                "runtime_churn_prediction"
            )

        if self._model_path is None:
            return (
                "event_level_churn_fallback"
            )

        return self._model_path.stem

    # =========================================================
    # Model lifecycle
    # =========================================================

    def is_loaded(self) -> bool:
        """
        Return True when an inference backend is loaded.

        ChurnPredictionService owns its own lazy lifecycle.

        For the legacy event-level path, this is True only
        when a real model artifact has been loaded.
        """

        if (
            self._prediction_service
            is not None
        ):
            return True

        return (
            self._model
            is not None
        )

    @property
    def model_available(self) -> bool:
        """
        Return whether a real prediction backend is available.
        """

        if (
            self._prediction_service
            is not None
        ):
            return True

        return (
            self._model_available
        )

    def load(self) -> None:
        """
        Prepare the configured prediction backend.

        Service-backed path
        -------------------
        No action is required because
        ChurnPredictionService owns model lifecycle.

        Legacy path
        -----------
        Attempt to load the event-level joblib model.

        Missing legacy artifacts are NOT fatal for Release 0.1.

        Instead:

            model_available = False

        and predict() uses the explicit fallback path.

        RuntimeError is still raised when a model file exists
        but cannot be deserialized, because that indicates a
        corrupt/incompatible artifact rather than an optional
        missing artifact.
        """

        # -----------------------------------------------------
        # Runtime service owns its lifecycle.
        # -----------------------------------------------------

        if (
            self._prediction_service
            is not None
        ):
            return

        # -----------------------------------------------------
        # Avoid duplicate load attempts.
        # -----------------------------------------------------

        if self._load_attempted:
            return

        self._load_attempted = True

        # -----------------------------------------------------
        # No legacy artifact configured.
        # -----------------------------------------------------

        if self._model_path is None:

            self._model_available = False

            self._model_load_error = (
                "No event-level churn model path configured."
            )

            return

        # -----------------------------------------------------
        # Legacy artifact missing.
        #
        # This is an accepted Release 0.1 fallback condition.
        # -----------------------------------------------------

        if not self._model_path.exists():

            self._model_available = False

            self._model_load_error = (
                "Event-level churn model artifact "
                f"not found: {self._model_path}"
            )

            return

        # -----------------------------------------------------
        # Load real legacy model.
        # -----------------------------------------------------

        try:

            self._model = joblib.load(
                self._model_path,
            )

        except Exception as exc:

            self._model_available = False

            self._model_load_error = (
                "Failed to load event-level churn model "
                f"from '{self._model_path}'."
            )

            raise RuntimeError(
                self._model_load_error
            ) from exc

        self._model_available = (
            self._model
            is not None
        )

        self._model_load_error = None

    # =========================================================
    # Feature construction
    # =========================================================

    def _build_features(
        self,
        information: InformationResult,
    ) -> FeatureVector:
        """
        Build the event-level FeatureVector.

        Feature engineering remains fully owned by
        FeatureBuilder.
        """

        return self._feature_builder.build(
            information,
        )

    # =========================================================
    # Prediction
    # =========================================================

    def predict(
        self,
        information: InformationResult,
    ) -> ChurnResult:
        """
        Predict churn or return an explicit MVP fallback.

        Execution
        ---------

        InformationResult
            ↓
        FeatureBuilder
            ↓
        FeatureVector
            ↓
        backend selection

        Backend selection
        -----------------

        1. ChurnPredictionService, when explicitly supplied.

        2. Legacy event-level model, when available.

        3. Deterministic fallback when no compatible
           event-level model artifact exists.

        Important
        ---------
        The fallback does NOT represent a trained-model
        prediction.

        It exists only to allow the Release 0.1 event-level
        analytical/reporting pipeline to complete truthfully.
        """

        feature_vector = (
            self._build_features(
                information
            )
        )

        # =====================================================
        # Explicit service-backed path
        # =====================================================

        if (
            self._prediction_service
            is not None
        ):

            probability = (
                self._predict_with_service(
                    feature_vector
                )
            )

            backend = (
                "churn_prediction_service"
            )

            model_available = True

            fallback_used = False

            fallback_reason = None

        # =====================================================
        # Legacy event-level path
        # =====================================================

        else:

            if not self._load_attempted:
                self.load()

            if self._model is not None:

                probability = (
                    self._predict_with_legacy_model(
                        feature_vector
                    )
                )

                backend = (
                    "legacy_direct_model"
                )

                model_available = True

                fallback_used = False

                fallback_reason = None

            else:

                probability = (
                    self._fallback_probability(
                        feature_vector
                    )
                )

                backend = (
                    "event_level_fallback"
                )

                model_available = False

                fallback_used = True

                fallback_reason = (
                    self._model_load_error
                    or
                    (
                        "No compatible event-level churn "
                        "model is available."
                    )
                )

        # =====================================================
        # Classification
        # =====================================================

        predicted_churn = (
            probability
            >=
            self.DEFAULT_THRESHOLD
        )

        # =====================================================
        # Result
        # =====================================================

        return ChurnResult(
            predicted_churn_rate=(
                probability
            ),

            confidence=(
                self._calculate_confidence(
                    probability=probability,
                    fallback_used=fallback_used,
                )
            ),

            feature_vector=(
                feature_vector
            ),

            metadata={
                "model": (
                    self.model_name
                ),

                "backend": (
                    backend
                ),

                "feature_count": (
                    feature_vector
                    .feature_count
                ),

                "predicted_churn": (
                    predicted_churn
                ),

                "threshold": (
                    self.DEFAULT_THRESHOLD
                ),

                "model_available": (
                    model_available
                ),

                "fallback_used": (
                    fallback_used
                ),

                "fallback_reason": (
                    fallback_reason
                ),

                "fallback_probability": (
                    self.FALLBACK_PROBABILITY
                    if fallback_used
                    else None
                ),

                "interpretation": (
                    (
                        "Deterministic MVP fallback; "
                        "not a trained churn-model prediction."
                    )
                    if fallback_used
                    else
                    "Model-based churn prediction."
                ),
            },
        )

    # =========================================================
    # Runtime-service inference
    # =========================================================

    def _predict_with_service(
        self,
        feature_vector: FeatureVector,
    ) -> float:
        """
        Execute calibrated inference using
        ChurnPredictionService.

        This path requires the supplied feature vector to
        satisfy the service's complete model feature contract.
        """

        if (
            self._prediction_service
            is None
        ):
            raise RuntimeError(
                "ChurnPredictionService is not configured."
            )

        if not feature_vector.features:
            return 0.0

        request = ChurnPredictionRequest(
            records=[
                dict(
                    feature_vector.features
                )
            ],

            threshold=(
                self.DEFAULT_THRESHOLD
            ),
        )

        result = (
            self._prediction_service.predict(
                request
            )
        )

        if result.row_count == 0:
            return 0.0

        if not result.predictions:
            return 0.0

        probability = float(
            result
            .predictions[
                0
            ]
            .churn_probability
        )

        return self._bound_probability(
            probability
        )

    # =========================================================
    # Legacy-model inference
    # =========================================================

    def _predict_with_legacy_model(
        self,
        feature_vector: FeatureVector,
    ) -> float:
        """
        Execute event-level legacy-model inference.

        If no model is loaded, return the deterministic
        fallback probability.

        This keeps private-method compatibility with existing
        tests while avoiding a missing-model crash.
        """

        if self._model is None:

            return self._fallback_probability(
                feature_vector
            )

        if not feature_vector.features:
            return 0.0

        if not hasattr(
            self._model,
            "predict_proba",
        ):
            return 0.0

        X = pd.DataFrame(
            [
                feature_vector.features
            ],
        )

        probabilities = (
            self._model.predict_proba(
                X
            )
        )

        if probabilities is None:
            return 0.0

        if len(
            probabilities
        ) == 0:
            return 0.0

        row = probabilities[
            0
        ]

        if len(
            row
        ) < 2:
            return 0.0

        probability = float(
            row[
                1
            ]
        )

        return self._bound_probability(
            probability
        )

    # =========================================================
    # Explicit fallback
    # =========================================================

    def _fallback_probability(
        self,
        feature_vector: FeatureVector,
    ) -> float:
        """
        Return the deterministic Release 0.1 fallback.

        Notes
        -----
        This is deliberately NOT derived from customer-level
        ML features.

        It does not fabricate missing input values.

        It does not claim to be a learned prediction.

        The fallback value is currently 0.0.
        """

        _ = feature_vector

        return float(
            self.FALLBACK_PROBABILITY
        )

    # =========================================================
    # Backward-compatible private inference API
    # =========================================================

    def _predict_probability(
        self,
        feature_vector: FeatureVector,
    ) -> float:
        """
        Execute prediction through the configured backend.

        Existing Architecture v2.3 tests may exercise this
        private method directly.
        """

        if (
            self._prediction_service
            is not None
        ):

            return self._predict_with_service(
                feature_vector
            )

        if not self._load_attempted:
            self.load()

        if self._model is None:

            return self._fallback_probability(
                feature_vector
            )

        return self._predict_with_legacy_model(
            feature_vector
        )

    # =========================================================
    # Probability helper
    # =========================================================

    @staticmethod
    def _bound_probability(
        probability: float,
    ) -> float:
        """
        Bound a probability to [0.0, 1.0].
        """

        return max(
            0.0,
            min(
                1.0,
                float(
                    probability
                ),
            ),
        )

    # =========================================================
    # Confidence
    # =========================================================

    @staticmethod
    def _calculate_confidence(
        probability: float,
        fallback_used: bool = False,
    ) -> float:
        """
        Calculate the MVP confidence score.

        Model-backed predictions
        ------------------------
        Preserve the original Architecture v2.3 confidence
        calculation:

            abs(probability - 0.5) * 2

        Fallback predictions
        --------------------
        Confidence is explicitly 0.0 because no trained
        event-level model produced the probability.

        This prevents the previous mathematical rule from
        incorrectly assigning confidence=1.0 to a fallback
        probability of 0.0.
        """

        if fallback_used:
            return 0.0

        return min(
            1.0,
            abs(
                probability
                -
                0.5
            )
            *
            2.0,
        )

    # =========================================================
    # Dependency access
    # =========================================================

    @property
    def prediction_service(
        self,
    ) -> ChurnPredictionService | None:
        """
        Return the configured runtime prediction service.
        """

        return self._prediction_service

    @property
    def feature_builder(
        self,
    ) -> FeatureBuilder:
        """
        Return the configured FeatureBuilder.
        """

        return self._feature_builder

    @property
    def model_path(
        self,
    ) -> Path | None:
        """
        Return the configured event-level model path.
        """

        return self._model_path

    @property
    def model_load_error(
        self,
    ) -> str | None:
        """
        Return the reason the optional event-level model was
        unavailable.
        """

        return self._model_load_error