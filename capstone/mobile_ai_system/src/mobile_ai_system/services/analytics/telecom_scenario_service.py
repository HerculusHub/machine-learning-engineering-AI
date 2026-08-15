"""
Runtime Telecom Scenario Service

Step 11B-2 / Step 11B-4
-----------------------

Purpose
-------
Expose named telecom business scenarios to the runtime
application layer.

The service maps business scenarios into controlled feature
perturbations and delegates probability calculations to the
validated ChurnSensitivityService.

Dependency direction
--------------------

Analysis Agent
      ↓
Analytics Tool
      ↓
TelecomScenarioService
      ↓
ChurnSensitivityService
      ↓
SensitivityModelArtifact

Important
---------
This service performs predictive scenario sensitivity.

It does NOT provide causal estimates.

Step 11B-4
----------
The runtime scenario result now includes row-level scenario
records:

    baseline_probability
    scenario_probability
    probability_change
    relative_probability_change

These row-level records allow FinancialImpactService to use:

    row ΔP
        ×
    row monthly revenue

instead of allocating aggregate churn impact approximately.

This makes the runtime financial path consistent with the
offline Step-10D / Step-10E analytical identities.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from mobile_ai_system.services.analytics.churn_sensitivity_service import (
    ChurnSensitivityService,
)

from mobile_ai_system.services.analytics.contracts import (
    ChurnSensitivityRequest,
    TelecomScenarioFeatureChange,
    TelecomScenarioRecord,
    TelecomScenarioRequest,
    TelecomScenarioResult,
)


# =============================================================
# Internal scenario definition
# =============================================================


@dataclass(frozen=True)
class _ScenarioDefinition:
    """
    Internal immutable telecom scenario definition.

    Attributes
    ----------
    scenario_id
        Stable runtime scenario identifier.

    title
        Human-readable business title.

    category
        Scenario category:

            competitive
            defensive

    description
        Business interpretation.

    expected_direction
        Expected population-level churn-probability direction:

            increase
            decrease

    feature_changes
        Additive model-feature interventions for intensity=1.
    """

    scenario_id: str

    title: str

    category: str

    description: str

    expected_direction: str

    feature_changes: dict[
        str,
        float,
    ]


# =============================================================
# Runtime telecom scenario service
# =============================================================


class TelecomScenarioService:
    """
    Runtime named telecom scenario simulator.

    The service:

    - validates named scenarios
    - scales interventions by requested intensity
    - applies feature-domain clipping
    - scores baseline and scenario populations
    - validates population-level response direction
    - publishes row-level probability changes
    - remains explicitly non-causal
    """

    # =========================================================
    # Runtime scenario library
    # =========================================================

    SCENARIOS = {
        "moderate_price_attack": (
            _ScenarioDefinition(
                scenario_id=(
                    "moderate_price_attack"
                ),
                title=(
                    "Moderate Competitor Price Attack"
                ),
                category="competitive",
                description=(
                    "Moderate increase in competitor "
                    "price pressure."
                ),
                expected_direction="increase",
                feature_changes={
                    "competitor_price_pressure_3m": 0.05,
                },
            )
        ),

        "aggressive_price_attack": (
            _ScenarioDefinition(
                scenario_id=(
                    "aggressive_price_attack"
                ),
                title=(
                    "Aggressive Competitor Price Attack"
                ),
                category="competitive",
                description=(
                    "Strong increase in competitor "
                    "price pressure."
                ),
                expected_direction="increase",
                feature_changes={
                    "competitor_price_pressure_3m": 0.10,
                },
            )
        ),

        "promotion_blitz": (
            _ScenarioDefinition(
                scenario_id=(
                    "promotion_blitz"
                ),
                title=(
                    "Competitor Promotion Blitz"
                ),
                category="competitive",
                description=(
                    "Strong increase in competitor "
                    "promotion pressure."
                ),
                expected_direction="increase",
                feature_changes={
                    "competitor_promotion_pressure_3m": 0.10,
                },
            )
        ),

        "network_upgrade_attack": (
            _ScenarioDefinition(
                scenario_id=(
                    "network_upgrade_attack"
                ),
                title=(
                    "Competitor Network Upgrade"
                ),
                category="competitive",
                description=(
                    "Increase in competitor network "
                    "pressure."
                ),
                expected_direction="increase",
                feature_changes={
                    "competitor_network_pressure_3m": 0.10,
                },
            )
        ),

        "combined_competitive_attack": (
            _ScenarioDefinition(
                scenario_id=(
                    "combined_competitive_attack"
                ),
                title=(
                    "Combined Price and Promotion Attack"
                ),
                category="competitive",
                description=(
                    "Simultaneous increase in price and "
                    "promotion pressure."
                ),
                expected_direction="increase",
                feature_changes={
                    "competitor_price_pressure_3m": 0.10,
                    "competitor_promotion_pressure_3m": 0.10,
                },
            )
        ),

        "severe_competitive_attack": (
            _ScenarioDefinition(
                scenario_id=(
                    "severe_competitive_attack"
                ),
                title=(
                    "Severe Multi-Dimensional "
                    "Competitive Attack"
                ),
                category="competitive",
                description=(
                    "Simultaneous severe price, promotion, "
                    "and network competitive pressure."
                ),
                expected_direction="increase",
                feature_changes={
                    "competitor_price_pressure_3m": 0.15,
                    "competitor_promotion_pressure_3m": 0.15,
                    "competitor_network_pressure_3m": 0.10,
                },
            )
        ),

        "service_recovery": (
            _ScenarioDefinition(
                scenario_id=(
                    "service_recovery"
                ),
                title=(
                    "Service Recovery Program"
                ),
                category="defensive",
                description=(
                    "Reduced support burden and network "
                    "complaints combined with improved "
                    "customer satisfaction."
                ),
                expected_direction="decrease",
                feature_changes={
                    "support_calls_3m": -1.0,
                    "network_complaints_3m": -1.0,
                    "customer_satisfaction_score": 0.05,
                },
            )
        ),
    }

    # =========================================================
    # Feature-domain constraints
    # =========================================================

    UNIT_INTERVAL_FEATURES = {
        "price_sensitivity_score",
        "promotion_sensitivity_score",
        "network_quality_sensitivity_score",
        "brand_loyalty_score",
        "customer_satisfaction_score",
        "retention_risk_score",
    }

    NONNEGATIVE_FEATURES = {
        "competitor_price_pressure_3m",
        "competitor_promotion_pressure_3m",
        "competitor_network_pressure_3m",
        "support_calls_3m",
        "network_complaints_3m",
        "late_payment_count_3m",
        "tenure_months_current",
        "device_age_months_current",
        "number_of_lines",
        "monthly_arpu",
    }

    def __init__(
        self,
        sensitivity_service: ChurnSensitivityService,
    ) -> None:
        """
        Initialize scenario service.

        Parameters
        ----------
        sensitivity_service
            Validated runtime ChurnSensitivityService.
        """

        if not isinstance(
            sensitivity_service,
            ChurnSensitivityService,
        ):

            raise TypeError(
                "TelecomScenarioService requires "
                "ChurnSensitivityService."
            )

        self._sensitivity_service = (
            sensitivity_service
        )

    # =========================================================
    # Public API
    # =========================================================

    def available_scenarios(
        self,
    ) -> list[str]:
        """
        Return stable runtime scenario identifiers.
        """

        return sorted(
            self.SCENARIOS
        )

    def simulate(
        self,
        request: TelecomScenarioRequest,
    ) -> TelecomScenarioResult:
        """
        Run a named telecom business scenario.

        Steps
        -----
        1. Validate request.
        2. Score baseline population.
        3. Apply scenario interventions cumulatively.
        4. Score final scenario population.
        5. Calculate row-level probability deltas.
        6. Calculate population-level scenario metrics.
        7. Validate expected business direction.
        8. Return structured scenario result.
        """

        self._validate_request(
            request
        )

        definition = (
            self.SCENARIOS[
                request.scenario_id
            ]
        )

        frame = pd.DataFrame(
            request.records
        )

        if frame.empty:

            raise ValueError(
                "Scenario request dataset cannot be empty."
            )

        # =====================================================
        # Validate sensitivity-model feature contract early
        # =====================================================

        feature_columns = (
            self._sensitivity_service
            .feature_columns()
        )

        missing = [
            feature
            for feature in feature_columns
            if feature
            not in frame.columns
        ]

        if missing:

            raise ValueError(
                "Scenario dataset missing required "
                "sensitivity-model features: "
                f"{missing}"
            )

        # =====================================================
        # Baseline scoring
        # =====================================================

        baseline_probability = (
            self._score(
                frame
            )
        )

        # =====================================================
        # Construct cumulative scenario population
        # =====================================================

        scenario_frame = (
            frame.copy()
        )

        feature_changes: list[
            TelecomScenarioFeatureChange
        ] = []

        for feature, base_change in (
            definition.feature_changes.items()
        ):

            if feature not in (
                feature_columns
            ):

                raise ValueError(
                    "Scenario attempts to modify feature "
                    "outside the sensitivity-model contract: "
                    f"{feature}"
                )

            requested_change = (
                float(
                    base_change
                )
                *
                float(
                    request.intensity
                )
            )

            # -------------------------------------------------
            # Run lower-level sensitivity validation for this
            # intervention coordinate.
            #
            # This preserves the service dependency:
            #
            # TelecomScenarioService
            #       ↓
            # ChurnSensitivityService
            # -------------------------------------------------

            sensitivity_result = (
                self._sensitivity_service.analyze(
                    ChurnSensitivityRequest(
                        records=(
                            scenario_frame
                            .to_dict(
                                orient="records"
                            )
                        ),
                        feature=(
                            feature
                        ),
                        change=(
                            requested_change
                        ),
                        expected_direction=(
                            self._expected_feature_direction(
                                feature=(
                                    feature
                                ),
                                change=(
                                    requested_change
                                ),
                                scenario_direction=(
                                    definition
                                    .expected_direction
                                ),
                            )
                        ),
                    )
                )
            )

            # -------------------------------------------------
            # Apply requested intervention to the running frame.
            #
            # Multi-feature scenarios therefore accumulate
            # changes in sequence.
            # -------------------------------------------------

            values = pd.to_numeric(
                scenario_frame[
                    feature
                ],
                errors="coerce",
            )

            if values.isna().any():

                raise ValueError(
                    "Scenario feature contains "
                    "non-numeric values: "
                    f"{feature}"
                )

            values = (
                values.astype(
                    float
                )
                +
                requested_change
            )

            values = (
                self._clip_feature(
                    feature=(
                        feature
                    ),
                    values=(
                        values
                    ),
                )
            )

            scenario_frame[
                feature
            ] = values

            # -------------------------------------------------
            # Feature audit record.
            #
            # expected_direction represents the intended local
            # effect direction, not merely the observed one.
            # -------------------------------------------------

            local_expected_direction = (
                self._expected_feature_direction(
                    feature=(
                        feature
                    ),
                    change=(
                        requested_change
                    ),
                    scenario_direction=(
                        definition
                        .expected_direction
                    ),
                )
            )

            feature_changes.append(
                TelecomScenarioFeatureChange(
                    feature=(
                        feature
                    ),
                    requested_change=(
                        requested_change
                    ),
                    expected_direction=(
                        local_expected_direction
                    ),
                )
            )

            # -------------------------------------------------
            # If a local intervention direction was explicitly
            # checked and failed, do not silently ignore it.
            # -------------------------------------------------

            if (
                sensitivity_result
                .direction_validation_passed
                is False
            ):

                raise ValueError(
                    "Scenario feature intervention failed "
                    "sensitivity direction validation: "
                    f"{feature}"
                )

        # =====================================================
        # Final scenario scoring
        # =====================================================

        scenario_probability = (
            self._score(
                scenario_frame
            )
        )

        probability_change = (
            scenario_probability
            -
            baseline_probability
        )

        # =====================================================
        # Row-level scenario records
        # =====================================================

        scenario_records: list[
            TelecomScenarioRecord
        ] = []

        for index in range(
            len(
                frame
            )
        ):

            baseline_value = float(
                baseline_probability[
                    index
                ]
            )

            scenario_value = float(
                scenario_probability[
                    index
                ]
            )

            delta = float(
                probability_change[
                    index
                ]
            )

            if baseline_value > 0.0:

                relative_delta = float(
                    delta
                    /
                    baseline_value
                )

            else:

                relative_delta = 0.0

            scenario_records.append(
                TelecomScenarioRecord(
                    row_index=(
                        index
                    ),

                    baseline_probability=(
                        baseline_value
                    ),

                    scenario_probability=(
                        scenario_value
                    ),

                    probability_change=(
                        delta
                    ),

                    relative_probability_change=(
                        relative_delta
                    ),
                )
            )

        # =====================================================
        # Population-level metrics
        # =====================================================

        baseline_mean = float(
            np.mean(
                baseline_probability
            )
        )

        scenario_mean = float(
            np.mean(
                scenario_probability
            )
        )

        mean_change = float(
            np.mean(
                probability_change
            )
        )

        if baseline_mean > 0.0:

            relative_change = float(
                mean_change
                /
                baseline_mean
            )

        else:

            relative_change = 0.0

        expected_incremental_churners = float(
            np.sum(
                probability_change
            )
        )

        observed_direction = (
            self._direction_from_change(
                mean_change
            )
        )

        direction_passed = (
            observed_direction
            ==
            definition.expected_direction
        )

        # =====================================================
        # Cross-level consistency checks
        # =====================================================

        record_delta_sum = float(
            sum(
                record.probability_change
                for record in scenario_records
            )
        )

        if not np.isclose(
            record_delta_sum,
            expected_incremental_churners,
            rtol=1e-10,
            atol=1e-12,
        ):

            raise RuntimeError(
                "Scenario row-level probability changes "
                "do not sum to published incremental "
                "churners."
            )

        record_delta_mean = float(
            np.mean(
                [
                    record.probability_change
                    for record in scenario_records
                ]
            )
        )

        if not np.isclose(
            record_delta_mean,
            mean_change,
            rtol=1e-10,
            atol=1e-12,
        ):

            raise RuntimeError(
                "Scenario row-level mean probability change "
                "does not match published scenario mean."
            )

        # =====================================================
        # Structured result
        # =====================================================

        return TelecomScenarioResult(
            scenario_id=(
                definition.scenario_id
            ),

            scenario_title=(
                definition.title
            ),

            category=(
                definition.category
            ),

            description=(
                definition.description
            ),

            intensity=float(
                request.intensity
            ),

            row_count=len(
                frame
            ),

            baseline_mean_probability=(
                baseline_mean
            ),

            scenario_mean_probability=(
                scenario_mean
            ),

            mean_probability_change=(
                mean_change
            ),

            relative_probability_change=(
                relative_change
            ),

            expected_incremental_churners=(
                expected_incremental_churners
            ),

            expected_direction=(
                definition.expected_direction
            ),

            observed_direction=(
                observed_direction
            ),

            direction_validation_passed=(
                direction_passed
            ),

            feature_changes=(
                feature_changes
            ),

            records=(
                scenario_records
            ),
        )

    # =========================================================
    # Scoring
    # =========================================================

    def _score(
        self,
        frame: pd.DataFrame,
    ) -> np.ndarray:
        """
        Score the sensitivity artifact.

        Note
        ----
        This currently uses ChurnSensitivityService's loaded
        artifact internally.

        A later service-interface cleanup can expose a public
        predict_frame() method on ChurnSensitivityService and
        remove this private-method dependency.
        """

        model = (
            self._sensitivity_service
            ._get_model()
        )

        probabilities = (
            model.predict_proba(
                frame
            )
        )

        probabilities = np.asarray(
            probabilities,
            dtype=float,
        )

        if (
            probabilities.ndim
            != 2
            or probabilities.shape[
                1
            ]
            < 2
        ):

            raise ValueError(
                "Sensitivity model returned invalid "
                "probability matrix."
            )

        positive_probability = (
            probabilities[
                :,
                1,
            ]
        )

        if (
            len(
                positive_probability
            )
            !=
            len(
                frame
            )
        ):

            raise ValueError(
                "Sensitivity model returned unexpected "
                "scenario prediction count."
            )

        if not np.isfinite(
            positive_probability
        ).all():

            raise ValueError(
                "Sensitivity model returned NaN or infinite "
                "scenario probabilities."
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
                "Scenario probabilities must remain "
                "between 0 and 1."
            )

        return positive_probability

    # =========================================================
    # Validation
    # =========================================================

    def _validate_request(
        self,
        request: TelecomScenarioRequest,
    ) -> None:
        """
        Validate telecom scenario request.
        """

        if not isinstance(
            request,
            TelecomScenarioRequest,
        ):

            raise TypeError(
                "simulate expects TelecomScenarioRequest."
            )

        if not (
            request.records
        ):

            raise ValueError(
                "Scenario request must contain records."
            )

        for index, record in enumerate(
            request.records
        ):

            if not isinstance(
                record,
                dict,
            ):

                raise TypeError(
                    "Scenario record at index "
                    f"{index} must be a dictionary."
                )

        if (
            request.scenario_id
            not in
            self.SCENARIOS
        ):

            raise ValueError(
                "Unknown telecom scenario: "
                f"{request.scenario_id}"
            )

        try:

            intensity = float(
                request.intensity
            )

        except (
            TypeError,
            ValueError,
        ) as exc:

            raise ValueError(
                "Scenario intensity must be numeric."
            ) from exc

        if not np.isfinite(
            intensity
        ):

            raise ValueError(
                "Scenario intensity must be finite."
            )

        if intensity <= 0.0:

            raise ValueError(
                "Scenario intensity must be positive."
            )

    # =========================================================
    # Feature constraints
    # =========================================================

    @classmethod
    def _clip_feature(
        cls,
        feature: str,
        values: pd.Series,
    ) -> pd.Series:
        """
        Preserve basic feature-domain constraints.
        """

        result = values.astype(
            float
        )

        if feature in (
            cls.UNIT_INTERVAL_FEATURES
        ):

            result = result.clip(
                lower=0.0,
                upper=1.0,
            )

        if feature in (
            cls.NONNEGATIVE_FEATURES
        ):

            result = result.clip(
                lower=0.0
            )

        return result

    # =========================================================
    # Direction helpers
    # =========================================================

    @staticmethod
    def _direction_from_change(
        change: float,
    ) -> str:
        """
        Map population probability delta to direction.
        """

        tolerance = 1e-12

        if change > tolerance:

            return "increase"

        if change < -tolerance:

            return "decrease"

        return "unchanged"

    @staticmethod
    def _expected_feature_direction(
        feature: str,
        change: float,
        scenario_direction: str,
    ) -> str:
        """
        Determine expected local sensitivity direction.

        This is intentionally explicit because defensive
        scenarios contain feature changes whose numerical
        direction and churn-risk direction differ.

        Examples
        --------
        support_calls_3m -= 1
            expected churn direction = decrease

        network_complaints_3m -= 1
            expected churn direction = decrease

        customer_satisfaction_score += 0.05
            expected churn direction = decrease

        competitor_price_pressure_3m += 0.10
            expected churn direction = increase
        """

        positive_risk_features = {
            "competitor_price_pressure_3m",
            "competitor_promotion_pressure_3m",
            "competitor_network_pressure_3m",
            "support_calls_3m",
            "network_complaints_3m",
            "late_payment_count_3m",
        }

        protective_features = {
            "customer_satisfaction_score",
            "brand_loyalty_score",
            "autopay_flag",
            "retention_offer_received",
        }

        tolerance = 1e-12

        if abs(
            change
        ) <= tolerance:

            return (
                scenario_direction
            )

        if feature in positive_risk_features:

            return (
                "increase"
                if change > 0.0
                else "decrease"
            )

        if feature in protective_features:

            return (
                "decrease"
                if change > 0.0
                else "increase"
            )

        # -----------------------------------------------------
        # For unclassified features, use the scenario-level
        # business expectation as a conservative default.
        # -----------------------------------------------------

        return (
            scenario_direction
        )