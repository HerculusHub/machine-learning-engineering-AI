"""
Churn Engine Interface

Architecture v2.3 (Frozen MVP)

Defines the contract for customer churn prediction
engines.

Concrete implementations may use:

    • Logistic Regression
    • Random Forest
    • XGBoost
    • LightGBM
    • CatBoost
    • TensorFlow / Keras
    • PyTorch

The remainder of the system depends only on this
interface.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from mobile_ai_system.application.models.information_result import (
    InformationResult,
)
from mobile_ai_system.impact.models.churn_result import (
    ChurnResult,
)


class IChurnEngine(ABC):
    """
    Interface for customer churn prediction.

    A churn engine estimates how business events are
    expected to influence customer churn.

    Implementations are responsible only for prediction,
    not business reasoning or financial analysis.
    """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """
        Name of the prediction model.

        Examples

            "xgboost"

            "lightgbm"

            "keras"

            "random_forest"
        """
        ...

    @abstractmethod
    def load(self) -> None:
        """
        Load the trained prediction model.

        Implementations may load from

            • pickle

            • joblib

            • TensorFlow SavedModel

            • ONNX

            • Torch checkpoint
        """
        ...

    @abstractmethod
    def predict(
        self,
        information: InformationResult,
    ) -> ChurnResult:
        """
        Predict customer churn from information events.

        Parameters
        ----------
        information
            Structured events produced by the
            Information Layer.

        Returns
        -------
        ChurnResult
        """
        ...

    @abstractmethod
    def is_loaded(self) -> bool:
        """
        Returns True if the prediction model has
        already been loaded.
        """
        ...