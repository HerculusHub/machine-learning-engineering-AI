"""
Tests for Impact Layer dependency composition.

Architecture v2.3 (Frozen MVP)

Release 0.1 boundary
--------------------
The frozen Impact Layer operates on event-level features
derived from InformationResult.

The Step 11 analytics ChurnPredictionService operates on a
customer-level engineered feature contract.

Therefore ChurnPredictionService remains registered as an
independent analytics capability but is intentionally NOT
injected into the event-level ChurnEngine.

This prevents incompatible customer-level and event-level
feature contracts from being mixed.
"""

from __future__ import annotations

from pathlib import Path

from mobile_ai_system.application.bootstrap import (
    Bootstrap,
)
from mobile_ai_system.application.registry import (
    CHURN_PREDICTION_SERVICE,
)
from mobile_ai_system.core.container import (
    Container,
)
from mobile_ai_system.impact import (
    impact_module,
)
from mobile_ai_system.impact.builders import (
    FeatureBuilder,
)
from mobile_ai_system.impact.engines.causal_engine import (
    CausalEngine,
)
from mobile_ai_system.impact.engines.churn_engine import (
    ChurnEngine,
)
from mobile_ai_system.impact.engines.financial_engine import (
    FinancialEngine,
)
from mobile_ai_system.impact.engines.sensitivity_engine import (
    SensitivityEngine,
)
from mobile_ai_system.impact.services.impact_service import (
    ImpactService,
)
from mobile_ai_system.services.analytics import (
    ChurnPredictionService,
)


# =============================================================
# Standalone Impact Layer
# =============================================================


def test_register_creates_impact_components():
    """
    impact_module.register() should construct all frozen
    Impact Layer components.
    """

    container = Container()

    impact_module.register(
        container,
    )

    assert isinstance(
        container.resolve(
            "feature_builder"
        ),
        FeatureBuilder,
    )

    assert isinstance(
        container.resolve(
            "churn_engine"
        ),
        ChurnEngine,
    )

    assert isinstance(
        container.resolve(
            "sensitivity_engine"
        ),
        SensitivityEngine,
    )

    assert isinstance(
        container.resolve(
            "causal_engine"
        ),
        CausalEngine,
    )

    assert isinstance(
        container.resolve(
            "financial_engine"
        ),
        FinancialEngine,
    )

    assert isinstance(
        container.resolve(
            "impact_service"
        ),
        ImpactService,
    )


# =============================================================
# Event-level churn backend
# =============================================================


def test_register_preserves_event_level_churn_engine():
    """
    The frozen Impact Layer should construct ChurnEngine
    using the event-level model path rather than the
    customer-level analytics service.
    """

    container = Container()

    model_path = Path(
        "models/churn/churn_model.joblib"
    )

    impact_module.register(
        container,
        churn_model_path=model_path,
    )

    churn_engine = container.resolve(
        "churn_engine"
    )

    assert isinstance(
        churn_engine,
        ChurnEngine,
    )

    assert (
        churn_engine.prediction_service
        is None
    )

    assert (
        churn_engine.model_path
        ==
        model_path
    )


# =============================================================
# Missing event-level model
# =============================================================


def test_missing_event_level_model_is_allowed(
    tmp_path,
):
    """
    Release 0.1 must allow Impact Layer composition when the
    optional event-level model artifact does not exist.

    The ChurnEngine will use its explicit deterministic
    fallback during prediction.
    """

    container = Container()

    missing_model = (
        tmp_path
        /
        "missing_event_churn.joblib"
    )

    assert not missing_model.exists()

    impact_module.register(
        container,
        churn_model_path=missing_model,
    )

    churn_engine = container.resolve(
        "churn_engine"
    )

    assert isinstance(
        churn_engine,
        ChurnEngine,
    )

    assert (
        churn_engine.model_path
        ==
        missing_model
    )

    assert (
        churn_engine.prediction_service
        is None
    )

    assert not churn_engine.is_loaded()


# =============================================================
# Analytics service separation
# =============================================================


def test_registered_runtime_prediction_service_is_not_injected(
    tmp_path,
):
    """
    A separately registered customer-level
    ChurnPredictionService must NOT be automatically injected
    into the event-level ChurnEngine.

    This regression test protects the Release 0.1 feature
    contract boundary.
    """

    container = Container()

    service = ChurnPredictionService(
        model_path=(
            tmp_path
            /
            "runtime_churn.joblib"
        )
    )

    container.register_instance(
        CHURN_PREDICTION_SERVICE,
        service,
    )

    impact_module.register(
        container,
    )

    registered_service = container.resolve(
        CHURN_PREDICTION_SERVICE
    )

    churn_engine = container.resolve(
        "churn_engine"
    )

    # Analytics capability remains registered.
    assert (
        registered_service
        is
        service
    )

    # But it is deliberately separated from the
    # event-level Impact pipeline.
    assert (
        churn_engine.prediction_service
        is None
    )


# =============================================================
# Bootstrap composition
# =============================================================


def test_bootstrap_registers_customer_analytics_service():
    """
    Full Bootstrap should continue registering the Step 11
    customer-level churn analytics capability.
    """

    container = Bootstrap().build()

    service = container.resolve(
        CHURN_PREDICTION_SERVICE
    )

    assert isinstance(
        service,
        ChurnPredictionService,
    )


def test_bootstrap_impact_churn_engine_is_event_level():
    """
    Full application composition must keep the frozen
    Impact ChurnEngine separate from the customer-level
    ChurnPredictionService.
    """

    container = Bootstrap().build()

    service = container.resolve(
        CHURN_PREDICTION_SERVICE
    )

    churn_engine = container.resolve(
        "churn_engine"
    )

    assert isinstance(
        service,
        ChurnPredictionService,
    )

    assert isinstance(
        churn_engine,
        ChurnEngine,
    )

    assert (
        churn_engine.prediction_service
        is None
    )

    assert (
        churn_engine.model_path
        is not None
    )


# =============================================================
# Dependency identity
# =============================================================


def test_impact_service_uses_registered_engines():
    """
    ImpactService should reference the exact engine instances
    registered by impact_module.
    """

    container = Container()

    impact_module.register(
        container,
    )

    impact_service = container.resolve(
        "impact_service"
    )

    churn_engine = container.resolve(
        "churn_engine"
    )

    sensitivity_engine = container.resolve(
        "sensitivity_engine"
    )

    causal_engine = container.resolve(
        "causal_engine"
    )

    financial_engine = container.resolve(
        "financial_engine"
    )

    assert (
        impact_service.churn_engine
        is
        churn_engine
    )

    assert (
        impact_service.sensitivity_engine
        is
        sensitivity_engine
    )

    assert (
        impact_service.causal_engine
        is
        causal_engine
    )

    assert (
        impact_service.financial_engine
        is
        financial_engine
    )