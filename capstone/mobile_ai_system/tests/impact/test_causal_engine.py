from mobile_ai_system.impact.engines.causal_engine import (
    CausalEngine,
)

from mobile_ai_system.application.models.information_result import (
    InformationResult,
)

from mobile_ai_system.impact.models.churn_result import (
    ChurnResult,
)

from mobile_ai_system.impact.models.sensitivity_result import (
    SensitivityResult,
)


def test_causal():

    engine = CausalEngine()

    result = engine.infer(

        InformationResult(),

        ChurnResult(),

        SensitivityResult(),

    )

    assert result is not None