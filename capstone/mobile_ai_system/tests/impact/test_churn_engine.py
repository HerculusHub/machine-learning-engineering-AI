"""
Unit tests for ChurnEngine.

Architecture v2.3 (Frozen MVP)
"""

from unittest.mock import patch

from mobile_ai_system.application.models.information_result import (
    InformationResult,
)
from mobile_ai_system.impact.engines.churn_engine import (
    ChurnEngine,
)
from mobile_ai_system.impact.models.churn_result import (
    ChurnResult,
)


class FakeChurnModel:
    """
    Minimal fake binary-classification model.
    """

    def predict_proba(self, X):
        return [
            [0.25, 0.75],
        ]


def build_information_result() -> InformationResult:
    """
    Build a minimal InformationResult.

    total_records is derived automatically
    from len(records).
    """

    records = [
        {
            "event_id": f"EVENT-{index}",
            "operator_name": "Verizon",
        }
        for index in range(10)
    ]

    return InformationResult(
        records=records,
        metadata={
            "fixture": True,
        },
    )


def test_predict():
    """
    ChurnEngine should return a ChurnResult
    using predict_proba().
    """

    information = build_information_result()

    with patch(
        "mobile_ai_system.impact.engines.churn_engine.Path.exists",
        return_value=True,
    ), patch(
        "mobile_ai_system.impact.engines.churn_engine.joblib.load",
        return_value=FakeChurnModel(),
    ):

        engine = ChurnEngine(
            model_path="fake_churn_model.joblib",
        )

        result = engine.predict(
            information,
        )

    assert isinstance(
        result,
        ChurnResult,
    )

    assert result.predicted_churn_rate == 0.75

    assert result.metadata["model"] == "fake_churn_model"

    assert result.metadata["feature_count"] == 1

    assert result.metadata["predicted_churn"] is True


def test_model_is_loaded_after_predict():
    """
    predict() should lazily load the model.
    """

    information = build_information_result()

    with patch(
        "mobile_ai_system.impact.engines.churn_engine.Path.exists",
        return_value=True,
    ), patch(
        "mobile_ai_system.impact.engines.churn_engine.joblib.load",
        return_value=FakeChurnModel(),
    ):

        engine = ChurnEngine(
            model_path="fake_churn_model.joblib",
        )

        assert engine.is_loaded() is False

        engine.predict(
            information,
        )

        assert engine.is_loaded() is True


def test_model_name():
    """
    model_name should come from the model filename.
    """

    engine = ChurnEngine(
        model_path="models/churn_model.joblib",
    )

    assert engine.model_name == "churn_model"


def test_predict_without_predict_proba_uses_zero_probability():
    """
    A model without predict_proba() should use
    the MVP zero-probability fallback.
    """

    class ModelWithoutPredictProba:
        pass

    information = build_information_result()

    with patch(
        "mobile_ai_system.impact.engines.churn_engine.Path.exists",
        return_value=True,
    ), patch(
        "mobile_ai_system.impact.engines.churn_engine.joblib.load",
        return_value=ModelWithoutPredictProba(),
    ):

        engine = ChurnEngine(
            model_path="fake_churn_model.joblib",
        )

        result = engine.predict(
            information,
        )

    assert result.predicted_churn_rate == 0.0

    assert result.metadata["predicted_churn"] is False


def test_predict_with_probability_above_threshold():
    """
    Probability >= 0.5 should produce
    a positive churn classification.
    """

    class HighChurnModel:

        def predict_proba(self, X):
            return [
                [0.10, 0.90],
            ]

    information = build_information_result()

    with patch(
        "mobile_ai_system.impact.engines.churn_engine.Path.exists",
        return_value=True,
    ), patch(
        "mobile_ai_system.impact.engines.churn_engine.joblib.load",
        return_value=HighChurnModel(),
    ):

        engine = ChurnEngine(
            model_path="fake_churn_model.joblib",
        )

        result = engine.predict(
            information,
        )

    assert result.predicted_churn_rate == 0.90

    assert result.metadata["predicted_churn"] is True


def test_predict_with_probability_below_threshold():
    """
    Probability < 0.5 should produce
    a negative churn classification.
    """

    class LowChurnModel:

        def predict_proba(self, X):
            return [
                [0.80, 0.20],
            ]

    information = build_information_result()

    with patch(
        "mobile_ai_system.impact.engines.churn_engine.Path.exists",
        return_value=True,
    ), patch(
        "mobile_ai_system.impact.engines.churn_engine.joblib.load",
        return_value=LowChurnModel(),
    ):

        engine = ChurnEngine(
            model_path="fake_churn_model.joblib",
        )

        result = engine.predict(
            information,
        )

    assert result.predicted_churn_rate == 0.20

    assert result.metadata["predicted_churn"] is False