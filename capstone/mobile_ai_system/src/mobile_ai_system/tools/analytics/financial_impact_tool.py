"""
Financial Impact Tool

Step 11C
--------

Thin Analysis-Agent-facing wrapper around:

    FinancialImpactService

Responsibilities
----------------
- translate agent-friendly dictionaries into runtime
  contracts
- invoke FinancialImpactService
- serialize structured results

No financial calculation is implemented here.
"""

from __future__ import annotations

from typing import Any

from mobile_ai_system.services.analytics import (
    FinancialImpactCustomer,
    FinancialImpactRequest,
    FinancialImpactService,
    TelecomScenarioFeatureChange,
    TelecomScenarioRecord,
    TelecomScenarioResult,
)

from mobile_ai_system.tools.analytics._serialization import (
    analytics_result_to_dict,
)


class FinancialImpactTool:
    """
    Runtime scenario financial-impact tool.
    """

    name = "financial_impact"

    description = (
        "Translate telecom scenario churn impact into expected "
        "revenue, gross-margin, and CLV impact. Results are "
        "predictive scenario financial translations, not "
        "causal estimates."
    )

    def __init__(
        self,
        service: FinancialImpactService,
    ) -> None:

        if service is None:

            raise ValueError(
                "FinancialImpactTool requires a service."
            )

        if not hasattr(
            service,
            "calculate",
        ):

            raise TypeError(
                "FinancialImpactTool service must expose "
                "calculate()."
            )

        self._service = service

    @property
    def service(
        self,
    ) -> FinancialImpactService:

        return self._service

    def run(
        self,
        scenario_result: (
            TelecomScenarioResult
            |
            dict[
                str,
                Any,
            ]
        ),
        customer_financials: list[
            FinancialImpactCustomer
            |
            dict[
                str,
                Any,
            ]
        ],
        gross_margin_rate: float = 0.35,
        clv_horizon_months: int = 24,
        annualization_months: int = 12,
    ) -> dict[str, Any]:
        """
        Translate scenario output into financial impact.
        """

        scenario_contract = (
            self._to_scenario_result(
                scenario_result
            )
        )

        financial_contracts = [
            self._to_financial_customer(
                item
            )
            for item in customer_financials
        ]

        request = (
            FinancialImpactRequest(
                scenario_result=(
                    scenario_contract
                ),
                customer_financials=(
                    financial_contracts
                ),
                gross_margin_rate=float(
                    gross_margin_rate
                ),
                clv_horizon_months=int(
                    clv_horizon_months
                ),
                annualization_months=int(
                    annualization_months
                ),
            )
        )

        result = (
            self._service.calculate(
                request
            )
        )

        return analytics_result_to_dict(
            result
        )

    # =========================================================
    # Scenario translation
    # =========================================================

    @staticmethod
    def _to_scenario_result(
        value: (
            TelecomScenarioResult
            |
            dict[
                str,
                Any,
            ]
        ),
    ) -> TelecomScenarioResult:
        """
        Convert tool-friendly dictionary into runtime scenario
        contract.

        Existing TelecomScenarioResult values pass through.
        """

        if isinstance(
            value,
            TelecomScenarioResult,
        ):

            return value

        if not isinstance(
            value,
            dict,
        ):

            raise TypeError(
                "scenario_result must be "
                "TelecomScenarioResult or dictionary."
            )

        feature_changes = [
            (
                item
                if isinstance(
                    item,
                    TelecomScenarioFeatureChange,
                )
                else TelecomScenarioFeatureChange(
                    feature=str(
                        item[
                            "feature"
                        ]
                    ),
                    requested_change=float(
                        item[
                            "requested_change"
                        ]
                    ),
                    expected_direction=str(
                        item[
                            "expected_direction"
                        ]
                    ),
                )
            )
            for item in value.get(
                "feature_changes",
                [],
            )
        ]

        records = [
            (
                item
                if isinstance(
                    item,
                    TelecomScenarioRecord,
                )
                else TelecomScenarioRecord(
                    row_index=int(
                        item[
                            "row_index"
                        ]
                    ),
                    baseline_probability=float(
                        item[
                            "baseline_probability"
                        ]
                    ),
                    scenario_probability=float(
                        item[
                            "scenario_probability"
                        ]
                    ),
                    probability_change=float(
                        item[
                            "probability_change"
                        ]
                    ),
                    relative_probability_change=float(
                        item[
                            "relative_probability_change"
                        ]
                    ),
                )
            )
            for item in value.get(
                "records",
                [],
            )
        ]

        return TelecomScenarioResult(
            scenario_id=str(
                value[
                    "scenario_id"
                ]
            ),

            scenario_title=str(
                value[
                    "scenario_title"
                ]
            ),

            category=str(
                value[
                    "category"
                ]
            ),

            description=str(
                value.get(
                    "description",
                    "",
                )
            ),

            intensity=float(
                value.get(
                    "intensity",
                    1.0,
                )
            ),

            row_count=int(
                value[
                    "row_count"
                ]
            ),

            baseline_mean_probability=float(
                value[
                    "baseline_mean_probability"
                ]
            ),

            scenario_mean_probability=float(
                value[
                    "scenario_mean_probability"
                ]
            ),

            mean_probability_change=float(
                value[
                    "mean_probability_change"
                ]
            ),

            relative_probability_change=float(
                value[
                    "relative_probability_change"
                ]
            ),

            expected_incremental_churners=float(
                value[
                    "expected_incremental_churners"
                ]
            ),

            expected_direction=str(
                value[
                    "expected_direction"
                ]
            ),

            observed_direction=str(
                value[
                    "observed_direction"
                ]
            ),

            direction_validation_passed=bool(
                value[
                    "direction_validation_passed"
                ]
            ),

            feature_changes=(
                feature_changes
            ),

            records=(
                records
            ),
        )

    # =========================================================
    # Financial customer translation
    # =========================================================

    @staticmethod
    def _to_financial_customer(
        value: (
            FinancialImpactCustomer
            |
            dict[
                str,
                Any,
            ]
        ),
    ) -> FinancialImpactCustomer:
        """
        Convert tool-friendly customer dictionary into runtime
        financial contract.
        """

        if isinstance(
            value,
            FinancialImpactCustomer,
        ):

            return value

        if not isinstance(
            value,
            dict,
        ):

            raise TypeError(
                "customer_financials entries must be "
                "FinancialImpactCustomer or dictionary."
            )

        return FinancialImpactCustomer(
            row_index=int(
                value[
                    "row_index"
                ]
            ),

            monthly_service_revenue=float(
                value[
                    "monthly_service_revenue"
                ]
            ),

            customer_segment=(
                value.get(
                    "customer_segment"
                )
            ),

            market_id=(
                value.get(
                    "market_id"
                )
            ),
        )