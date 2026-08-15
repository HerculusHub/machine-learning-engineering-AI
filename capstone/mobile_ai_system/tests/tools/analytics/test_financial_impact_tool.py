"""
Tests for FinancialImpactTool.
"""

from __future__ import annotations

from mobile_ai_system.services.analytics import (
    FinancialImpactRecord,
    FinancialImpactResult,
    TelecomScenarioRecord,
    TelecomScenarioResult,
)

from mobile_ai_system.tools.analytics import (
    FinancialImpactTool,
)


class FakeFinancialService:

    def __init__(
        self,
    ):
        self.last_request = None

    def calculate(
        self,
        request,
    ):
        self.last_request = request

        return FinancialImpactResult(
            scenario_id=(
                request
                .scenario_result
                .scenario_id
            ),

            scenario_title=(
                request
                .scenario_result
                .scenario_title
            ),

            category="competitive",
            row_count=1,
            financial_direction="loss",

            expected_incremental_churners=0.01,
            expected_additional_churners=0.01,
            expected_churn_prevented=0.0,

            monthly_revenue_at_risk=1.0,
            monthly_revenue_protected=0.0,

            net_monthly_revenue_impact=-1.0,
            net_annualized_revenue_impact=-12.0,
            net_annualized_gross_margin_impact=-4.2,
            net_clv_impact=-8.4,

            gross_margin_rate=(
                request.gross_margin_rate
            ),

            clv_horizon_months=(
                request.clv_horizon_months
            ),

            annualization_months=(
                request.annualization_months
            ),

            records=[
                FinancialImpactRecord(
                    row_index=0,
                    monthly_service_revenue=100.0,
                    expected_incremental_churners=0.01,
                    expected_additional_churners=0.01,
                    expected_churn_prevented=0.0,
                    monthly_revenue_at_risk=1.0,
                    monthly_revenue_protected=0.0,
                    net_monthly_revenue_impact=-1.0,
                    annualized_revenue_impact=-12.0,
                    annualized_gross_margin_impact=-4.2,
                    clv_impact=-8.4,
                )
            ],
        )


def make_scenario():

    return TelecomScenarioResult(
        scenario_id="test",
        scenario_title="Test Scenario",
        category="competitive",
        description="Test.",
        intensity=1.0,
        row_count=1,

        baseline_mean_probability=0.02,
        scenario_mean_probability=0.03,
        mean_probability_change=0.01,
        relative_probability_change=0.50,

        expected_incremental_churners=0.01,

        expected_direction="increase",
        observed_direction="increase",
        direction_validation_passed=True,

        feature_changes=[],

        records=[
            TelecomScenarioRecord(
                row_index=0,
                baseline_probability=0.02,
                scenario_probability=0.03,
                probability_change=0.01,
                relative_probability_change=0.50,
            )
        ],
    )


def test_financial_tool_accepts_contract():

    service = FakeFinancialService()

    tool = FinancialImpactTool(
        service=service
    )

    result = tool.run(
        scenario_result=(
            make_scenario()
        ),
        customer_financials=[
            {
                "row_index": 0,
                "monthly_service_revenue": 100.0,
            }
        ],
    )

    assert (
        service.last_request
        is not None
    )

    assert (
        result[
            "financial_direction"
        ]
        ==
        "loss"
    )


def test_financial_tool_accepts_scenario_dictionary():

    service = FakeFinancialService()

    tool = FinancialImpactTool(
        service=service
    )

    scenario = {
        "scenario_id": "test",
        "scenario_title": "Test Scenario",
        "category": "competitive",
        "description": "Test.",
        "intensity": 1.0,
        "row_count": 1,

        "baseline_mean_probability": 0.02,
        "scenario_mean_probability": 0.03,
        "mean_probability_change": 0.01,
        "relative_probability_change": 0.50,

        "expected_incremental_churners": 0.01,

        "expected_direction": "increase",
        "observed_direction": "increase",
        "direction_validation_passed": True,

        "feature_changes": [],

        "records": [
            {
                "row_index": 0,
                "baseline_probability": 0.02,
                "scenario_probability": 0.03,
                "probability_change": 0.01,
                "relative_probability_change": 0.50,
            }
        ],
    }

    result = tool.run(
        scenario_result=scenario,

        customer_financials=[
            {
                "row_index": 0,
                "monthly_service_revenue": 100.0,
                "customer_segment": "premium",
                "market_id": "M1",
            }
        ],
    )

    request = service.last_request

    assert (
        request
        .scenario_result
        .records[
            0
        ]
        .probability_change
        ==
        0.01
    )

    assert (
        request
        .customer_financials[
            0
        ]
        .customer_segment
        ==
        "premium"
    )

    assert (
        result[
            "net_monthly_revenue_impact"
        ]
        ==
        -1.0
    )


def test_financial_tool_passes_assumptions():

    service = FakeFinancialService()

    tool = FinancialImpactTool(
        service=service
    )

    tool.run(
        scenario_result=(
            make_scenario()
        ),

        customer_financials=[
            {
                "row_index": 0,
                "monthly_service_revenue": 100.0,
            }
        ],

        gross_margin_rate=0.40,
        clv_horizon_months=36,
        annualization_months=12,
    )

    assert (
        service.last_request
        .gross_margin_rate
        ==
        0.40
    )

    assert (
        service.last_request
        .clv_horizon_months
        ==
        36
    )