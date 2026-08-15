"""
Analytics Service Contracts

Runtime contracts shared by analytics services, analytics
tools, and later Analysis Agent integration.

Important
---------
These contracts belong to the application/runtime layer.

They must not depend on:

    scripts.synthetic_data.*

The synthetic-data package remains the offline development,
training, calibration, explainability, scenario-generation,
and validation environment.

Current contracts
-----------------
Step 11A
    ChurnPredictionRequest
    ChurnPredictionRecord
    ChurnPredictionResult

Step 11B-1
    ChurnSensitivityRequest
    ChurnSensitivityRecord
    ChurnSensitivityResult

Step 11B-2 / 11B-4
    TelecomScenarioRequest
    TelecomScenarioFeatureChange
    TelecomScenarioRecord
    TelecomScenarioResult

Step 11B-3 / 11B-4
    FinancialImpactCustomer
    FinancialImpactRequest
    FinancialImpactRecord
    FinancialImpactGroupResult
    FinancialImpactResult
"""

from __future__ import annotations

from dataclasses import (
    dataclass,
    field,
)

from typing import Any


# =============================================================
# Step 11A
# Churn prediction contracts
# =============================================================


@dataclass(frozen=True)
class ChurnPredictionRequest:
    """
    Request for calibrated churn prediction.

    Parameters
    ----------
    records
        One or more feature dictionaries.

        Every record must satisfy the feature contract stored
        in the persisted churn model artifact.

    threshold
        Probability threshold used for binary churn flags.

        Probability output remains the primary analytical
        quantity.
    """

    records: list[
        dict[
            str,
            Any,
        ]
    ]

    threshold: float = 0.50


@dataclass(frozen=True)
class ChurnPredictionRecord:
    """
    Prediction result for one input record.

    Attributes
    ----------
    row_index
        Zero-based position of the input record.

    churn_probability
        Calibrated probability of churn.

    predicted_churn
        Binary classification derived from the requested
        threshold.
    """

    row_index: int

    churn_probability: float

    predicted_churn: bool


@dataclass(frozen=True)
class ChurnPredictionResult:
    """
    Structured calibrated churn prediction result.

    Attributes
    ----------
    model_name
        Runtime model identifier.

    calibration_method
        Probability calibration method when available.

    feature_count
        Number of features expected by the persisted model.

    row_count
        Number of prediction records returned.

    threshold
        Binary decision threshold used.

    predictions
        Row-level prediction records.

    mean_churn_probability
        Mean calibrated churn probability.

    minimum_churn_probability
        Minimum calibrated churn probability.

    maximum_churn_probability
        Maximum calibrated churn probability.
    """

    model_name: str

    calibration_method: str | None

    feature_count: int

    row_count: int

    threshold: float

    predictions: list[
        ChurnPredictionRecord
    ] = field(
        default_factory=list
    )

    mean_churn_probability: float = 0.0

    minimum_churn_probability: float = 0.0

    maximum_churn_probability: float = 0.0


# =============================================================
# Step 11B-1
# Churn sensitivity contracts
# =============================================================


@dataclass(frozen=True)
class ChurnSensitivityRequest:
    """
    Request for model-based churn sensitivity analysis.

    Important
    ---------
    This is predictive sensitivity analysis.

    It is NOT causal inference.

    Parameters
    ----------
    records
        Input feature dictionaries satisfying the dedicated
        sensitivity-model feature contract.

    feature
        Sensitivity-model feature to perturb.

    change
        Numerical additive change applied to the selected
        feature.

        Example
        -------
        If:

            feature =
                "competitor_price_pressure_3m"

            change =
                0.10

        then:

            scenario_value
                =
            baseline_value + 0.10

    expected_direction
        Optional population-level direction guardrail.

        Allowed values:

            "increase"
            "decrease"
            None

        If supplied, the service compares the observed mean
        churn-probability response with this expectation.
    """

    records: list[
        dict[
            str,
            Any,
        ]
    ]

    feature: str

    change: float

    expected_direction: str | None = None


@dataclass(frozen=True)
class ChurnSensitivityRecord:
    """
    Sensitivity result for one input observation.

    Attributes
    ----------
    row_index
        Zero-based position of the input observation.

    baseline_probability
        Calibrated churn probability before perturbation.

    scenario_probability
        Calibrated churn probability after perturbation.

    probability_change
        Scenario probability minus baseline probability.

    relative_probability_change
        Probability change divided by baseline probability
        when baseline probability is positive.
    """

    row_index: int

    baseline_probability: float

    scenario_probability: float

    probability_change: float

    relative_probability_change: float


@dataclass(frozen=True)
class ChurnSensitivityResult:
    """
    Structured predictive churn-sensitivity result.

    Attributes
    ----------
    model_name
        Runtime sensitivity-model identifier.

    calibration_method
        Probability calibration method used by the model.

    feature
        Feature that was perturbed.

    requested_change
        Requested additive feature change.

    row_count
        Number of analyzed records.

    baseline_mean_probability
        Mean baseline calibrated churn probability.

    scenario_mean_probability
        Mean scenario calibrated churn probability.

    mean_probability_change
        Population mean of:

            scenario_probability
            -
            baseline_probability

    relative_probability_change
        Mean probability change relative to baseline mean
        probability.

    expected_incremental_churners
        Sum of observation-level probability changes.

        This is an expected-count equivalent across the input
        observations, not necessarily a count of unique real
        customers.

    expected_direction
        Optional requested business-direction guardrail.

    observed_direction
        Actual population-level sensitivity direction:

            increase
            decrease
            unchanged

    direction_validation_passed
        True
            Observed direction matches expectation.

        False
            Observed direction conflicts with expectation.

        None
            No expected direction was supplied.

    records
        Observation-level sensitivity records.

    analysis_type
        Explicit analytical classification.

    causal_interpretation
        Always False for this service.
    """

    model_name: str

    calibration_method: str | None

    feature: str

    requested_change: float

    row_count: int

    baseline_mean_probability: float

    scenario_mean_probability: float

    mean_probability_change: float

    relative_probability_change: float

    expected_incremental_churners: float

    expected_direction: str | None

    observed_direction: str

    direction_validation_passed: bool | None

    records: list[
        ChurnSensitivityRecord
    ] = field(
        default_factory=list
    )

    analysis_type: str = (
        "predictive_model_sensitivity"
    )

    causal_interpretation: bool = False


# =============================================================
# Step 11B-2 / Step 11B-4
# Telecom scenario contracts
# =============================================================


@dataclass(frozen=True)
class TelecomScenarioRequest:
    """
    Runtime request for a named telecom business scenario.

    Parameters
    ----------
    records
        Input sensitivity-model feature records.

    scenario_id
        Stable scenario identifier.

    intensity
        Positive scenario multiplier.

        Default scenario definitions use intensity=1.0.

        Examples:

            intensity=0.5
                half-strength scenario

            intensity=1.0
                standard scenario

            intensity=1.5
                stronger scenario

    segment
        Optional business segment label retained for future
        filtering or routing.

        The current service does not automatically filter
        records using this field.

    market_id
        Optional market identifier retained for future
        filtering or routing.
    """

    records: list[
        dict[
            str,
            Any,
        ]
    ]

    scenario_id: str

    intensity: float = 1.0

    segment: str | None = None

    market_id: str | None = None


@dataclass(frozen=True)
class TelecomScenarioFeatureChange:
    """
    One feature intervention within a telecom scenario.

    Attributes
    ----------
    feature
        Sensitivity-model feature modified by the scenario.

    requested_change
        Additive feature change after applying scenario
        intensity.

    expected_direction
        Expected churn-probability response to this feature
        intervention.
    """

    feature: str

    requested_change: float

    expected_direction: str


@dataclass(frozen=True)
class TelecomScenarioRecord:
    """
    Row-level runtime telecom scenario result.

    Step 11B-4
    -----------
    This contract enables exact downstream financial impact:

        probability_change
            ×
        customer monthly revenue

    Attributes
    ----------
    row_index
        Zero-based input-row position.

    baseline_probability
        Calibrated churn probability before scenario changes.

    scenario_probability
        Calibrated churn probability after all scenario
        interventions are applied.

    probability_change
        Scenario probability minus baseline probability.

    relative_probability_change
        Probability change divided by baseline probability
        when baseline probability is positive.
    """

    row_index: int

    baseline_probability: float

    scenario_probability: float

    probability_change: float

    relative_probability_change: float


@dataclass(frozen=True)
class TelecomScenarioResult:
    """
    Structured runtime telecom scenario result.

    Important
    ---------
    This is predictive model sensitivity.

    It is NOT causal inference.

    Step 11B-4 adds row-level scenario records so downstream
    financial analysis can use the exact customer-level
    probability delta instead of aggregate allocation.

    Attributes
    ----------
    scenario_id
        Stable scenario identifier.

    scenario_title
        Human-readable scenario title.

    category
        Business category such as:

            competitive
            defensive

    description
        Human-readable scenario interpretation.

    intensity
        Scenario intensity multiplier.

    row_count
        Number of analyzed records.

    baseline_mean_probability
        Population mean baseline churn probability.

    scenario_mean_probability
        Population mean scenario churn probability.

    mean_probability_change
        Mean scenario-minus-baseline probability change.

    relative_probability_change
        Mean probability change relative to baseline mean.

    expected_incremental_churners
        Sum of row-level probability changes.

    expected_direction
        Expected population-level scenario direction.

    observed_direction
        Observed population-level scenario direction.

    direction_validation_passed
        Whether observed direction matches expected direction.

    feature_changes
        Audit trail of scenario feature interventions.

    records
        Exact row-level scenario probability results.

    analysis_type
        Runtime analytical classification.

    causal_interpretation
        Always False.
    """

    scenario_id: str

    scenario_title: str

    category: str

    description: str

    intensity: float

    row_count: int

    baseline_mean_probability: float

    scenario_mean_probability: float

    mean_probability_change: float

    relative_probability_change: float

    expected_incremental_churners: float

    expected_direction: str

    observed_direction: str

    direction_validation_passed: bool

    feature_changes: list[
        TelecomScenarioFeatureChange
    ] = field(
        default_factory=list
    )

    records: list[
        TelecomScenarioRecord
    ] = field(
        default_factory=list
    )

    analysis_type: str = (
        "predictive_telecom_scenario_simulation"
    )

    causal_interpretation: bool = False


# =============================================================
# Step 11B-3 / Step 11B-4
# Financial impact contracts
# =============================================================


@dataclass(frozen=True)
class FinancialImpactCustomer:
    """
    Financial attributes for one analyzed customer record.

    Parameters
    ----------
    row_index
        Zero-based row index corresponding to the scenario
        input population.

        Step 11B-4 uses this field to join the customer's
        financial data to the exact TelecomScenarioRecord.

    monthly_service_revenue
        Monthly recurring service revenue represented by the
        customer observation.

    customer_segment
        Optional customer-segment label.

    market_id
        Optional market identifier.
    """

    row_index: int

    monthly_service_revenue: float

    customer_segment: str | None = None

    market_id: str | None = None


@dataclass(frozen=True)
class FinancialImpactRequest:
    """
    Request for runtime scenario financial translation.

    Parameters
    ----------
    scenario_result
        Structured result returned by TelecomScenarioService.

        Step 11B-4 requires this result to contain row-level
        TelecomScenarioRecord values.

    customer_financials
        One financial record per scenario population row.

        FinancialImpactCustomer.row_index must correspond to
        TelecomScenarioRecord.row_index.

    gross_margin_rate
        Gross-margin assumption.

        Must be between zero and one.

    clv_horizon_months
        Customer-lifetime-value horizon in months.

    annualization_months
        Number of months used to annualize revenue impact.
    """

    scenario_result: TelecomScenarioResult

    customer_financials: list[
        FinancialImpactCustomer
    ]

    gross_margin_rate: float = 0.35

    clv_horizon_months: int = 24

    annualization_months: int = 12


@dataclass(frozen=True)
class FinancialImpactRecord:
    """
    Financial impact for one input observation.

    Sign convention
    ---------------
    Positive net financial impact:
        benefit / value protected

    Negative net financial impact:
        loss / value at risk
    """

    row_index: int

    monthly_service_revenue: float

    expected_incremental_churners: float

    expected_additional_churners: float

    expected_churn_prevented: float

    monthly_revenue_at_risk: float

    monthly_revenue_protected: float

    net_monthly_revenue_impact: float

    annualized_revenue_impact: float

    annualized_gross_margin_impact: float

    clv_impact: float

    customer_segment: str | None = None

    market_id: str | None = None


@dataclass(frozen=True)
class FinancialImpactGroupResult:
    """
    Aggregated financial impact for a segment or market.
    """

    group_value: str

    row_count: int

    expected_incremental_churners: float

    net_monthly_revenue_impact: float

    net_annualized_revenue_impact: float

    net_annualized_gross_margin_impact: float

    net_clv_impact: float


@dataclass(frozen=True)
class FinancialImpactResult:
    """
    Structured runtime telecom financial-impact result.

    The result aggregates exact row-level probability changes
    from TelecomScenarioResult.records.

    Financial identities
    --------------------

    additional churn:
        max(probability_change, 0)

    churn prevented:
        max(-probability_change, 0)

    monthly revenue at risk:
        additional churn
        ×
        monthly service revenue

    monthly revenue protected:
        churn prevented
        ×
        monthly service revenue

    net monthly revenue impact:
        protected
        -
        at risk

    net annualized revenue:
        net monthly revenue
        ×
        annualization_months

    gross-margin impact:
        annualized revenue
        ×
        gross_margin_rate

    CLV impact:
        net monthly revenue
        ×
        gross_margin_rate
        ×
        clv_horizon_months
    """

    scenario_id: str

    scenario_title: str

    category: str

    row_count: int

    financial_direction: str

    expected_incremental_churners: float

    expected_additional_churners: float

    expected_churn_prevented: float

    monthly_revenue_at_risk: float

    monthly_revenue_protected: float

    net_monthly_revenue_impact: float

    net_annualized_revenue_impact: float

    net_annualized_gross_margin_impact: float

    net_clv_impact: float

    gross_margin_rate: float

    clv_horizon_months: int

    annualization_months: int

    records: list[
        FinancialImpactRecord
    ] = field(
        default_factory=list
    )

    segment_results: list[
        FinancialImpactGroupResult
    ] = field(
        default_factory=list
    )

    market_results: list[
        FinancialImpactGroupResult
    ] = field(
        default_factory=list
    )

    analysis_type: str = (
        "predictive_scenario_financial_translation"
    )

    causal_interpretation: bool = False