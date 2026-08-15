"""
Runtime Financial Impact Service

Step 11B-3 / Step 11B-4
-----------------------

Purpose
-------
Translate runtime telecom scenario churn sensitivity into
revenue, gross-margin, and CLV impact.

Dependency direction
--------------------

Analysis Agent
      ↓
Analytics Tool
      ↓
FinancialImpactService
      ↓
TelecomScenarioResult

This service does NOT:

- retrain models
- simulate scenarios
- perform causal inference
- import scripts.synthetic_data.*

Financial conventions
---------------------
For each observation:

    expected incremental churners
        =
    scenario probability - baseline probability

If positive:
    additional churn

If negative:
    churn prevented

Monthly revenue impact:

    protected revenue
        -
    revenue at risk

Annualized revenue impact:

    monthly impact
        *
    annualization_months

Annualized gross-margin impact:

    annualized revenue impact
        *
    gross_margin_rate

CLV impact:

    monthly revenue impact
        *
    gross_margin_rate
        *
    clv_horizon_months

Sign convention
---------------
Positive financial impact:
    benefit / value protected

Negative financial impact:
    loss / value at risk

Step 11B-4
----------
The preferred runtime path consumes exact row-level scenario
probability changes from:

    TelecomScenarioResult.records

and applies:

    probability_change_i
        ×
    monthly_service_revenue_i

However, Step 11B-3 aggregate-only scenario results remain
supported for backward compatibility.

When scenario.records is empty, aggregate incremental churn is
allocated across financial rows proportionally to monthly
service revenue.

This means Step 11B-4 EXTENDS Step 11B-3 rather than breaking
the earlier service contract.
"""

from __future__ import annotations

from collections import defaultdict

import numpy as np

from mobile_ai_system.services.analytics.contracts import (
    FinancialImpactCustomer,
    FinancialImpactGroupResult,
    FinancialImpactRecord,
    FinancialImpactRequest,
    FinancialImpactResult,
    TelecomScenarioResult,
)


class FinancialImpactService:
    """
    Runtime telecom scenario financial translator.

    Preferred execution path
    ------------------------
    TelecomScenarioResult.records exists:

        exact row ΔP
            ×
        exact row revenue

    Compatibility execution path
    ----------------------------
    TelecomScenarioResult.records is empty:

        aggregate expected churn
            ↓
        revenue-weighted row allocation

    The compatibility path preserves Step 11B-3 callers.
    """

    # =========================================================
    # Public API
    # =========================================================

    def calculate(
        self,
        request: FinancialImpactRequest,
    ) -> FinancialImpactResult:
        """
        Translate scenario churn sensitivity into financial
        impact.

        The service automatically selects:

        - exact Step 11B-4 row-level calculation when scenario
          records are available;

        - backward-compatible Step 11B-3 allocation otherwise.
        """

        self._validate_request(
            request
        )

        scenario = (
            request.scenario_result
        )

        # =====================================================
        # Resolve row-level incremental churn
        # =====================================================

        row_incremental_churners = (
            self._resolve_row_incremental_churners(
                request=request,
            )
        )

        # =====================================================
        # Row-level financial translation
        # =====================================================

        records: list[
            FinancialImpactRecord
        ] = []

        for customer, incremental in zip(
            request.customer_financials,
            row_incremental_churners,
            strict=True,
        ):

            revenue = float(
                customer
                .monthly_service_revenue
            )

            incremental = float(
                incremental
            )

            # -------------------------------------------------
            # Churn decomposition
            # -------------------------------------------------

            additional = max(
                incremental,
                0.0,
            )

            prevented = max(
                -incremental,
                0.0,
            )

            # -------------------------------------------------
            # Monthly revenue at risk
            # -------------------------------------------------

            monthly_revenue_at_risk = (
                additional
                *
                revenue
            )

            # -------------------------------------------------
            # Monthly revenue protected
            # -------------------------------------------------

            monthly_revenue_protected = (
                prevented
                *
                revenue
            )

            # -------------------------------------------------
            # Signed monthly revenue impact
            #
            # Positive = benefit / protected value
            # Negative = loss / value at risk
            # -------------------------------------------------

            net_monthly_revenue = (
                monthly_revenue_protected
                -
                monthly_revenue_at_risk
            )

            # -------------------------------------------------
            # Annualized revenue
            # -------------------------------------------------

            annualized_revenue = (
                net_monthly_revenue
                *
                request
                .annualization_months
            )

            # -------------------------------------------------
            # Annualized gross margin
            # -------------------------------------------------

            annualized_margin = (
                annualized_revenue
                *
                request
                .gross_margin_rate
            )

            # -------------------------------------------------
            # CLV impact
            # -------------------------------------------------

            clv_impact = (
                net_monthly_revenue
                *
                request
                .gross_margin_rate
                *
                request
                .clv_horizon_months
            )

            records.append(
                FinancialImpactRecord(
                    row_index=(
                        customer
                        .row_index
                    ),

                    monthly_service_revenue=(
                        revenue
                    ),

                    expected_incremental_churners=(
                        incremental
                    ),

                    expected_additional_churners=(
                        additional
                    ),

                    expected_churn_prevented=(
                        prevented
                    ),

                    monthly_revenue_at_risk=(
                        monthly_revenue_at_risk
                    ),

                    monthly_revenue_protected=(
                        monthly_revenue_protected
                    ),

                    net_monthly_revenue_impact=(
                        net_monthly_revenue
                    ),

                    annualized_revenue_impact=(
                        annualized_revenue
                    ),

                    annualized_gross_margin_impact=(
                        annualized_margin
                    ),

                    clv_impact=(
                        clv_impact
                    ),

                    customer_segment=(
                        customer
                        .customer_segment
                    ),

                    market_id=(
                        customer
                        .market_id
                    ),
                )
            )

        # =====================================================
        # Population totals
        # =====================================================

        expected_incremental = float(
            sum(
                row.expected_incremental_churners
                for row in records
            )
        )

        expected_additional = float(
            sum(
                row.expected_additional_churners
                for row in records
            )
        )

        expected_prevented = float(
            sum(
                row.expected_churn_prevented
                for row in records
            )
        )

        monthly_at_risk = float(
            sum(
                row.monthly_revenue_at_risk
                for row in records
            )
        )

        monthly_protected = float(
            sum(
                row.monthly_revenue_protected
                for row in records
            )
        )

        net_monthly = float(
            sum(
                row.net_monthly_revenue_impact
                for row in records
            )
        )

        net_annualized = float(
            sum(
                row.annualized_revenue_impact
                for row in records
            )
        )

        net_margin = float(
            sum(
                row.annualized_gross_margin_impact
                for row in records
            )
        )

        net_clv = float(
            sum(
                row.clv_impact
                for row in records
            )
        )

        # =====================================================
        # Aggregate churn identity
        # =====================================================

        if not np.isclose(
            expected_incremental,
            float(
                scenario
                .expected_incremental_churners
            ),
            rtol=1e-10,
            atol=1e-12,
        ):

            raise ValueError(
                "Financial row-level incremental churn does "
                "not sum to scenario "
                "expected_incremental_churners."
            )

        # =====================================================
        # Financial direction
        # =====================================================

        financial_direction = (
            self._financial_direction(
                net_annualized
            )
        )

        # =====================================================
        # Segment aggregation
        # =====================================================

        segment_results = (
            self._aggregate_groups(
                records=records,
                attribute="customer_segment",
            )
        )

        # =====================================================
        # Market aggregation
        # =====================================================

        market_results = (
            self._aggregate_groups(
                records=records,
                attribute="market_id",
            )
        )

        # =====================================================
        # Structured result
        # =====================================================

        return FinancialImpactResult(
            scenario_id=(
                scenario
                .scenario_id
            ),

            scenario_title=(
                scenario
                .scenario_title
            ),

            category=(
                scenario
                .category
            ),

            row_count=len(
                records
            ),

            financial_direction=(
                financial_direction
            ),

            expected_incremental_churners=(
                expected_incremental
            ),

            expected_additional_churners=(
                expected_additional
            ),

            expected_churn_prevented=(
                expected_prevented
            ),

            monthly_revenue_at_risk=(
                monthly_at_risk
            ),

            monthly_revenue_protected=(
                monthly_protected
            ),

            net_monthly_revenue_impact=(
                net_monthly
            ),

            net_annualized_revenue_impact=(
                net_annualized
            ),

            net_annualized_gross_margin_impact=(
                net_margin
            ),

            net_clv_impact=(
                net_clv
            ),

            gross_margin_rate=float(
                request
                .gross_margin_rate
            ),

            clv_horizon_months=int(
                request
                .clv_horizon_months
            ),

            annualization_months=int(
                request
                .annualization_months
            ),

            records=(
                records
            ),

            segment_results=(
                segment_results
            ),

            market_results=(
                market_results
            ),
        )

    # =========================================================
    # Row-level incremental churn resolution
    # =========================================================

    def _resolve_row_incremental_churners(
        self,
        request: FinancialImpactRequest,
    ) -> list[float]:
        """
        Resolve one incremental-churn value per financial row.

        Preferred path
        --------------
        TelecomScenarioResult.records is populated.

        Uses exact row-level probability_change matched by
        row_index.

        Compatibility path
        ------------------
        TelecomScenarioResult.records is empty.

        Allocates aggregate scenario expected incremental churn
        according to monthly-service-revenue weights.
        """

        scenario = (
            request.scenario_result
        )

        if scenario.records:

            return (
                self._resolve_exact_row_effects(
                    request=request,
                )
            )

        return (
            self._resolve_aggregate_row_effects(
                request=request,
            )
        )

    # =========================================================
    # Exact Step 11B-4 row path
    # =========================================================

    @staticmethod
    def _resolve_exact_row_effects(
        request: FinancialImpactRequest,
    ) -> list[float]:
        """
        Resolve exact row-level ΔP values using row_index.
        """

        scenario = (
            request.scenario_result
        )

        scenario_lookup = {
            record.row_index: record
            for record in scenario.records
        }

        # Duplicates are also checked during request validation,
        # but keeping the lookup guard here protects this method
        # if later reused independently.

        if (
            len(
                scenario_lookup
            )
            !=
            len(
                scenario.records
            )
        ):

            raise ValueError(
                "Scenario row_index values must be unique."
            )

        values: list[
            float
        ] = []

        for customer in (
            request.customer_financials
        ):

            if (
                customer.row_index
                not in scenario_lookup
            ):

                raise ValueError(
                    "Financial row_index has no matching "
                    "scenario record: "
                    f"{customer.row_index}"
                )

            scenario_record = (
                scenario_lookup[
                    customer.row_index
                ]
            )

            values.append(
                float(
                    scenario_record
                    .probability_change
                )
            )

        return values

    # =========================================================
    # Backward-compatible Step 11B-3 allocation path
    # =========================================================

    @staticmethod
    def _resolve_aggregate_row_effects(
        request: FinancialImpactRequest,
    ) -> list[float]:
        """
        Allocate aggregate scenario incremental churn across
        financial rows.

        This preserves the Step 11B-3 behavior for callers that
        do not yet provide TelecomScenarioResult.records.

        Allocation rule
        ---------------
        If total monthly service revenue > 0:

            weight_i
                =
            revenue_i / total_revenue

        Otherwise:

            equal weights
        """

        scenario = (
            request.scenario_result
        )

        revenues = np.asarray(
            [
                float(
                    customer
                    .monthly_service_revenue
                )
                for customer
                in request.customer_financials
            ],
            dtype=float,
        )

        total_revenue = float(
            revenues.sum()
        )

        if total_revenue > 0.0:

            weights = (
                revenues
                /
                total_revenue
            )

        else:

            weights = np.full(
                len(
                    revenues
                ),
                1.0
                /
                len(
                    revenues
                ),
                dtype=float,
            )

        aggregate_incremental = float(
            scenario
            .expected_incremental_churners
        )

        row_values = (
            aggregate_incremental
            *
            weights
        )

        return [
            float(
                value
            )
            for value in row_values
        ]

    # =========================================================
    # Aggregation
    # =========================================================

    @staticmethod
    def _aggregate_groups(
        records: list[
            FinancialImpactRecord
        ],
        attribute: str,
    ) -> list[
        FinancialImpactGroupResult
    ]:
        """
        Aggregate runtime financial records by one dimension.

        Current supported dimensions:

            customer_segment
            market_id
        """

        grouped = defaultdict(
            list
        )

        for record in records:

            value = getattr(
                record,
                attribute,
            )

            if value is None:

                continue

            grouped[
                str(
                    value
                )
            ].append(
                record
            )

        results = []

        for group_value in sorted(
            grouped
        ):

            rows = grouped[
                group_value
            ]

            results.append(
                FinancialImpactGroupResult(
                    group_value=(
                        group_value
                    ),

                    row_count=len(
                        rows
                    ),

                    expected_incremental_churners=float(
                        sum(
                            row.expected_incremental_churners
                            for row in rows
                        )
                    ),

                    net_monthly_revenue_impact=float(
                        sum(
                            row.net_monthly_revenue_impact
                            for row in rows
                        )
                    ),

                    net_annualized_revenue_impact=float(
                        sum(
                            row.annualized_revenue_impact
                            for row in rows
                        )
                    ),

                    net_annualized_gross_margin_impact=float(
                        sum(
                            row.annualized_gross_margin_impact
                            for row in rows
                        )
                    ),

                    net_clv_impact=float(
                        sum(
                            row.clv_impact
                            for row in rows
                        )
                    ),
                )
            )

        return results

    # =========================================================
    # Financial direction
    # =========================================================

    @staticmethod
    def _financial_direction(
        annualized_impact: float,
    ) -> str:
        """
        Map signed financial impact to business direction.

        Returns
        -------
        benefit
            positive financial value

        loss
            negative financial value

        neutral
            effectively zero financial value
        """

        tolerance = 1e-12

        if annualized_impact > tolerance:

            return "benefit"

        if annualized_impact < -tolerance:

            return "loss"

        return "neutral"

    # =========================================================
    # Request validation
    # =========================================================

    @staticmethod
    def _validate_request(
        request: FinancialImpactRequest,
    ) -> None:
        """
        Validate runtime financial-impact request.

        Step 11B-4 row-level scenario validation is performed
        only when scenario.records is populated.
        """

        # -----------------------------------------------------
        # Request type
        # -----------------------------------------------------

        if not isinstance(
            request,
            FinancialImpactRequest,
        ):

            raise TypeError(
                "calculate expects FinancialImpactRequest."
            )

        # -----------------------------------------------------
        # Scenario result type
        # -----------------------------------------------------

        if not isinstance(
            request.scenario_result,
            TelecomScenarioResult,
        ):

            raise TypeError(
                "scenario_result must be "
                "TelecomScenarioResult."
            )

        scenario = (
            request.scenario_result
        )

        # -----------------------------------------------------
        # Financial population
        # -----------------------------------------------------

        if not (
            request
            .customer_financials
        ):

            raise ValueError(
                "Financial request must contain at least "
                "one customer financial record."
            )

        if (
            len(
                request
                .customer_financials
            )
            !=
            scenario
            .row_count
        ):

            raise ValueError(
                "Financial customer count must match "
                "scenario row_count."
            )

        # -----------------------------------------------------
        # Gross margin
        # -----------------------------------------------------

        if not np.isfinite(
            float(
                request
                .gross_margin_rate
            )
        ):

            raise ValueError(
                "gross_margin_rate must be finite."
            )

        if not (
            0.0
            <=
            request
            .gross_margin_rate
            <=
            1.0
        ):

            raise ValueError(
                "gross_margin_rate must be between "
                "0 and 1."
            )

        # -----------------------------------------------------
        # CLV horizon
        # -----------------------------------------------------

        if (
            request
            .clv_horizon_months
            <=
            0
        ):

            raise ValueError(
                "clv_horizon_months must be positive."
            )

        # -----------------------------------------------------
        # Annualization
        # -----------------------------------------------------

        if (
            request
            .annualization_months
            <=
            0
        ):

            raise ValueError(
                "annualization_months must be positive."
            )

        # -----------------------------------------------------
        # Financial row validation
        #
        # This intentionally runs BEFORE optional scenario-row
        # validation so invalid financial input preserves the
        # original Step 11B-3 error semantics.
        # -----------------------------------------------------

        seen_indices = set()

        for customer in (
            request
            .customer_financials
        ):

            if not isinstance(
                customer,
                FinancialImpactCustomer,
            ):

                raise TypeError(
                    "customer_financials must contain "
                    "FinancialImpactCustomer records."
                )

            revenue = float(
                customer
                .monthly_service_revenue
            )

            if not np.isfinite(
                revenue
            ):

                raise ValueError(
                    "monthly_service_revenue must be finite."
                )

            if revenue < 0.0:

                raise ValueError(
                    "monthly_service_revenue cannot be "
                    "negative."
                )

            if (
                customer
                .row_index
                in
                seen_indices
            ):

                raise ValueError(
                    "Financial row_index values must be "
                    "unique."
                )

            seen_indices.add(
                customer
                .row_index
            )

        # -----------------------------------------------------
        # Step 11B-4 row-level scenario validation
        #
        # IMPORTANT:
        # This is OPTIONAL for backward compatibility.
        # -----------------------------------------------------

        if scenario.records:

            FinancialImpactService._validate_row_level_scenario(
                request=request,
            )

    # =========================================================
    # Step 11B-4 scenario-record validation
    # =========================================================

    @staticmethod
    def _validate_row_level_scenario(
        request: FinancialImpactRequest,
    ) -> None:
        """
        Validate exact row-level TelecomScenarioRecord data.

        Called only when scenario.records is populated.
        """

        scenario = (
            request.scenario_result
        )

        # -----------------------------------------------------
        # Row count
        # -----------------------------------------------------

        if (
            len(
                scenario.records
            )
            !=
            scenario.row_count
        ):

            raise ValueError(
                "Scenario row-level record count must match "
                "scenario row_count."
            )

        # -----------------------------------------------------
        # Scenario row uniqueness
        # -----------------------------------------------------

        scenario_indices = [
            record.row_index
            for record in scenario.records
        ]

        if (
            len(
                scenario_indices
            )
            !=
            len(
                set(
                    scenario_indices
                )
            )
        ):

            raise ValueError(
                "Scenario row_index values must be unique."
            )

        # -----------------------------------------------------
        # Exact row-index alignment
        # -----------------------------------------------------

        scenario_index_set = set(
            scenario_indices
        )

        financial_index_set = {
            customer.row_index
            for customer in (
                request
                .customer_financials
            )
        }

        if (
            scenario_index_set
            !=
            financial_index_set
        ):

            missing_financial = sorted(
                scenario_index_set
                -
                financial_index_set
            )

            missing_scenario = sorted(
                financial_index_set
                -
                scenario_index_set
            )

            raise ValueError(
                "Scenario and financial row_index values "
                "must align exactly. "
                "Missing financial rows: "
                f"{missing_financial}; "
                "financial rows with no matching scenario "
                "record: "
                f"{missing_scenario}"
            )

        # -----------------------------------------------------
        # Probability identities
        # -----------------------------------------------------

        for record in (
            scenario.records
        ):

            baseline = float(
                record
                .baseline_probability
            )

            scenario_probability = float(
                record
                .scenario_probability
            )

            probability_change = float(
                record
                .probability_change
            )

            if not np.isfinite(
                baseline
            ):

                raise ValueError(
                    "Scenario baseline probability must "
                    "be finite."
                )

            if not np.isfinite(
                scenario_probability
            ):

                raise ValueError(
                    "Scenario probability must be finite."
                )

            if not np.isfinite(
                probability_change
            ):

                raise ValueError(
                    "Scenario probability change must "
                    "be finite."
                )

            if not (
                0.0
                <=
                baseline
                <=
                1.0
            ):

                raise ValueError(
                    "Scenario baseline probability must "
                    "be between 0 and 1."
                )

            if not (
                0.0
                <=
                scenario_probability
                <=
                1.0
            ):

                raise ValueError(
                    "Scenario probability must be between "
                    "0 and 1."
                )

            expected_change = (
                scenario_probability
                -
                baseline
            )

            if not np.isclose(
                probability_change,
                expected_change,
                rtol=1e-10,
                atol=1e-12,
            ):

                raise ValueError(
                    "Scenario probability_change must equal "
                    "scenario_probability minus "
                    "baseline_probability."
                )

        # -----------------------------------------------------
        # Aggregate ΔP identity
        # -----------------------------------------------------

        row_delta_sum = float(
            sum(
                record.probability_change
                for record in (
                    scenario.records
                )
            )
        )

        if not np.isclose(
            row_delta_sum,
            float(
                scenario
                .expected_incremental_churners
            ),
            rtol=1e-10,
            atol=1e-12,
        ):

            raise ValueError(
                "Scenario row-level probability changes do "
                "not sum to expected_incremental_churners."
            )