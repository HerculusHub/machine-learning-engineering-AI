"""
Impact Module

Architecture v2.3 (Frozen MVP)

Dependency-registration module for the Impact Layer.

Responsibilities
----------------
Construct and register:

    FeatureBuilder
    ChurnEngine
    SensitivityEngine
    CausalEngine
    FinancialEngine
    ImpactService

Important MVP boundary
----------------------
The Impact Layer operates on InformationResult event data.

The runtime analytics services introduced in Step 11 operate
on customer-level ML feature records and remain registered
separately in the application DI container.

They are NOT injected into the frozen event-level Impact
pipeline for Release 0.1 because the two layers use different
feature contracts.

This avoids invalid feature fabrication and preserves the
existing Architecture v2.3 Impact Layer.
"""

from __future__ import annotations

from pathlib import Path

from mobile_ai_system.core.container import (
    Container,
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


# =============================================================
# Legacy / event-level Impact model
# =============================================================

DEFAULT_CHURN_MODEL_PATH = Path(
    "models/churn/churn_model.joblib"
)


# =============================================================
# Registration
# =============================================================


def register(
    container: Container,
    churn_model_path: str | Path = DEFAULT_CHURN_MODEL_PATH,
) -> None:
    """
    Register all Impact Layer components.

    Parameters
    ----------
    container
        Application dependency-injection container.

    churn_model_path
        Persisted event-level churn model used by the
        Architecture v2.3 Impact Layer.

        This is intentionally separate from the customer-level
        calibrated churn model registered by the analytics
        runtime services.
    """

    # =========================================================
    # Feature Builder
    # =========================================================

    feature_builder = FeatureBuilder()

    # =========================================================
    # Churn Engine
    # =========================================================
    #
    # Important:
    #
    # Do NOT inject ChurnPredictionService here.
    #
    # FeatureBuilder currently creates event-level features,
    # while ChurnPredictionService requires the customer-level
    # engineered feature schema.
    # =========================================================

    churn_engine = ChurnEngine(
        model_path=churn_model_path,
        feature_builder=feature_builder,
    )

    # =========================================================
    # Remaining engines
    # =========================================================

    sensitivity_engine = SensitivityEngine()

    causal_engine = CausalEngine()

    financial_engine = FinancialEngine()

    # =========================================================
    # Impact Service
    # =========================================================

    impact_service = ImpactService(
        churn_engine=churn_engine,
        sensitivity_engine=sensitivity_engine,
        causal_engine=causal_engine,
        financial_engine=financial_engine,
    )

    # =========================================================
    # Container registration
    # =========================================================

    container.register_instance(
        "feature_builder",
        feature_builder,
    )

    container.register_instance(
        "churn_engine",
        churn_engine,
    )

    container.register_instance(
        "sensitivity_engine",
        sensitivity_engine,
    )

    container.register_instance(
        "causal_engine",
        causal_engine,
    )

    container.register_instance(
        "financial_engine",
        financial_engine,
    )

    container.register_instance(
        "impact_service",
        impact_service,
    )