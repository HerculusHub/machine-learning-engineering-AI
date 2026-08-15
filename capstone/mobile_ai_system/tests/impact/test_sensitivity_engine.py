"""
Unit tests for SensitivityEngine.

Architecture v2.3 (Frozen MVP)
"""

from mobile_ai_system.application.models.information_result import (
    InformationResult,
)
from mobile_ai_system.impact.engines.sensitivity_engine import (
    SensitivityEngine,
)
from mobile_ai_system.impact.models.churn_result import (
    ChurnResult,
)
from mobile_ai_system.impact.models.feature_vector import (
    FeatureVector,
)
from mobile_ai_system.impact.models.sensitivity_result import (
    SensitivityResult,
)


def build_information_result() -> InformationResult:
    """
    Minimal information-layer input.
    """

    return InformationResult(
        records=[
            {
                "event_id": "EVENT-1",
                "operator_name": "Verizon",
            }
        ],
        metadata={
            "fixture": True,
        },
    )


def build_churn_result() -> ChurnResult:
    """
    Churn result containing a FeatureVector.
    """

    vector = FeatureVector(
        features={
            "event_count": 1.0,
            "price_change": 0.20,
            "network_quality": 0.85,
        },
        metadata={
            "fixture": True,
        },
    )

    return ChurnResult(
        predicted_churn_rate=0.65,
        confidence=0.80,
        feature_vector=vector,
        metadata={
            "model": "fake_churn_model",
        },
    )


def test_sensitivity():
    """
    SensitivityEngine should return a structured
    SensitivityResult.
    """

    engine = SensitivityEngine()

    information = build_information_result()

    churn = build_churn_result()

    result = engine.analyze(
        information,
        churn,
    )

    assert isinstance(
        result,
        SensitivityResult,
    )

    assert result.total_features == 3

    assert result.model_name == "fake_churn_model"

    assert result.metadata["engine"] == "placeholder"

    assert result.metadata["method"] == "placeholder"

    assert result.metadata["feature_count"] == 3

    assert result.metadata["information_record_count"] == 1


def test_feature_names_are_preserved():
    """
    Feature names from the churn FeatureVector
    should appear in SensitivityResult.
    """

    engine = SensitivityEngine()

    result = engine.analyze(
        build_information_result(),
        build_churn_result(),
    )

    names = [
        feature.feature_name
        for feature in result.features
    ]

    assert names == [
        "event_count",
        "network_quality",
        "price_change",
    ]


def test_placeholder_scores_are_zero():
    """
    Frozen MVP uses zero-valued placeholder scores.
    """

    engine = SensitivityEngine()

    result = engine.analyze(
        build_information_result(),
        build_churn_result(),
    )

    for feature in result.features:

        assert feature.importance_score == 0.0

        assert feature.sensitivity_score == 0.0

        assert feature.shap_value is None

        assert feature.direction == "unknown"


def test_engine_name():
    """
    Engine name should identify the MVP implementation.
    """

    engine = SensitivityEngine()

    assert engine.engine_name == "placeholder"


def test_shap_not_supported():
    """
    SHAP is intentionally not implemented in Frozen MVP.
    """

    engine = SensitivityEngine()

    assert engine.supports_shap() is False


def test_global_importance_not_supported():
    """
    Global feature importance is not implemented
    in the placeholder engine.
    """

    engine = SensitivityEngine()

    assert engine.supports_global_importance() is False


def test_empty_feature_vector():
    """
    Empty FeatureVector should produce an empty
    SensitivityResult without error.
    """

    engine = SensitivityEngine()

    churn = ChurnResult(
        predicted_churn_rate=0.0,
        confidence=1.0,
        feature_vector=FeatureVector(),
        metadata={
            "model": "fake_churn_model",
        },
    )

    result = engine.analyze(
        build_information_result(),
        churn,
    )

    assert result.is_empty is True

    assert result.total_features == 0