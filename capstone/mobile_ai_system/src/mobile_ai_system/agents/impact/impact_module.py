"""
Impact Module

Architecture v2.3 (Frozen MVP)

Registers all Impact Layer components into the
dependency injection container.
"""

from __future__ import annotations

from mobile_ai_system.core.container import Container

from mobile_ai_system.impact.builders import (
    FeatureBuilder,
)

from mobile_ai_system.impact.engines.churn_engine import (
    ChurnEngine,
)

from mobile_ai_system.impact.engines.sensitivity_engine import (
    SensitivityEngine,
)

from mobile_ai_system.impact.engines.causal_engine import (
    CausalEngine,
)

from mobile_ai_system.impact.engines.financial_engine import (
    FinancialEngine,
)

from mobile_ai_system.impact.services.impact_service import (
    ImpactService,
)


def register(container: Container) -> None:
    """
    Register all Impact Layer services.
    """

    #
    # Engines
    #

    feature_builder = FeatureBuilder()

    churn_engine = ChurnEngine()

    sensitivity_engine = SensitivityEngine()

    causal_engine = CausalEngine()

    financial_engine = FinancialEngine()

    #
    # Service
    #

    impact_service = ImpactService(

        feature_builder=feature_builder,

        churn_engine=churn_engine,

        sensitivity_engine=sensitivity_engine,

        causal_engine=causal_engine,

        financial_engine=financial_engine,

    )

    #
    # Register
    #

    container.register_instance(

        FeatureBuilder,

        feature_builder,

    )

    container.register_instance(

        ChurnEngine,

        churn_engine,

    )

    container.register_instance(

        SensitivityEngine,

        sensitivity_engine,

    )

    container.register_instance(

        CausalEngine,

        causal_engine,

    )

    container.register_instance(

        FinancialEngine,

        financial_engine,

    )

    container.register_instance(

        ImpactService,

        impact_service,

    )