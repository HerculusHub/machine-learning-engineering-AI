"""
Tests for Synthetic Causal Benchmark Generator.

Post-MVP Synthetic Analytics Environment

These tests validate:

- benchmark construction
- treatment/control observations
- potential-outcome identities
- propensity-score validity
- ATE / ATT / ATU ground truth
- heterogeneous treatment effects
- sampling behavior
- reproducibility
"""

from __future__ import annotations

from datetime import date

import pandas as pd

from scripts.synthetic_data.config import (
    SyntheticDataConfig,
)
from scripts.synthetic_data.customer_master import (
    CustomerMasterGenerator,
)
from scripts.synthetic_data.operator_events import (
    OperatorEventGenerator,
)
from scripts.synthetic_data.customer_market_exposure import (
    CustomerMarketExposureGenerator,
)
from scripts.synthetic_data.customer_monthly_panel import (
    CustomerMonthlyPanelGenerator,
)
from scripts.synthetic_data.customer_churn_outcomes import (
    CustomerChurnOutcomeGenerator,
)
from scripts.synthetic_data.causal_benchmark import (
    CausalBenchmarkGenerator,
)


# ============================================================
# Test fixture builder
# ============================================================


def build_benchmark(
    sample_size: int = 2_000,
    seed: int = 42,
):
    """
    Build a small but complete synthetic causal pipeline.

    This intentionally generates all upstream datasets so the
    causal benchmark is tested against the real Step 1-5 data
    contracts rather than mocked data.
    """

    config = SyntheticDataConfig(
        random_seed=seed,
        customer_count=1_000,
        operator_event_count=1_000,
        exposure_customers_per_event=30,
        exposure_event_chunk_size=100,
        panel_customer_chunk_size=200,
        panel_start_date=date(
            2025,
            1,
            1,
        ),
        panel_end_date=date(
            2026,
            6,
            1,
        ),
        causal_benchmark_sample_size=sample_size,
    )

    # --------------------------------------------------------
    # Step 1
    # --------------------------------------------------------

    customers = CustomerMasterGenerator(
        config=config,
    ).generate()

    # --------------------------------------------------------
    # Step 2
    # --------------------------------------------------------

    events = OperatorEventGenerator(
        config=config,
    ).generate()

    # --------------------------------------------------------
    # Step 3
    # --------------------------------------------------------

    exposures = CustomerMarketExposureGenerator(
        config=config,
    ).generate(
        customers=customers,
        events=events,
    )

    # --------------------------------------------------------
    # Step 4
    # --------------------------------------------------------

    panel = CustomerMonthlyPanelGenerator(
        config=config,
    ).generate(
        customers=customers,
        exposures=exposures,
    )

    # --------------------------------------------------------
    # Step 5
    # --------------------------------------------------------

    outcomes = CustomerChurnOutcomeGenerator(
        config=config,
    ).generate(
        panel=panel,
    )

    # --------------------------------------------------------
    # Step 7
    # --------------------------------------------------------

    benchmark = CausalBenchmarkGenerator(
        config=config,
    ).generate(
        panel=panel,
        outcomes=outcomes,
        sample_size=sample_size,
    )

    return (
        config,
        panel,
        outcomes,
        benchmark,
    )


# ============================================================
# Basic construction
# ============================================================


def test_generate_returns_dataframe():
    """
    Generator should return a pandas DataFrame.
    """

    _, _, _, benchmark = build_benchmark()

    assert isinstance(
        benchmark,
        pd.DataFrame,
    )


def test_benchmark_is_not_empty():
    """
    Causal benchmark should contain observations.
    """

    _, _, _, benchmark = build_benchmark()

    assert len(
        benchmark
    ) > 0


def test_sample_size_respected():
    """
    Generated benchmark should respect configured sample size
    when enough source observations exist.
    """

    _, _, _, benchmark = build_benchmark(
        sample_size=1_500
    )

    assert len(
        benchmark
    ) == 1_500


def test_benchmark_ids_are_unique():
    """
    benchmark_id should uniquely identify observations.
    """

    _, _, _, benchmark = build_benchmark()

    assert benchmark[
        "benchmark_id"
    ].is_unique


# ============================================================
# Required schema
# ============================================================


def test_required_columns_exist():
    """
    Benchmark should expose treatment, potential outcomes,
    causal truth, and adjustment variables.
    """

    _, _, _, benchmark = build_benchmark()

    required = {
        "benchmark_id",
        "customer_id",
        "month",
        "market_id",
        "customer_segment",

        "treatment",
        "treatment_price_exposure",
        "treatment_promotion_exposure",

        "propensity_score_true",
        "propensity_log_odds_true",

        "observed_outcome",
        "observed_outcome_probability",

        "potential_outcome_y0",
        "potential_outcome_y1",
        "individual_treatment_effect",

        "ate_true",
        "att_true",
        "atu_true",

        "price_sensitivity_segment",
        "promotion_sensitivity_segment",
        "loyalty_segment",
        "baseline_risk_segment",

        "cate_price_sensitivity_true",
        "cate_customer_segment_true",

        "baseline_churn_propensity",
        "price_sensitivity_score",
        "promotion_sensitivity_score",
        "brand_loyalty_score",

        "churn_probability_true",
        "counterfactual_churn_probability",
        "incremental_churn_probability_true",

        "at_risk_flag",
    }

    assert required.issubset(
        benchmark.columns
    )


# ============================================================
# Risk-set integrity
# ============================================================


def test_only_at_risk_observations_are_used():
    """
    Causal analysis must not include post-churn observations.
    """

    _, _, _, benchmark = build_benchmark()

    assert benchmark[
        "at_risk_flag"
    ].all()


# ============================================================
# Treatment
# ============================================================


def test_treatment_is_binary():
    """
    Treatment should contain only 0 and 1.
    """

    _, _, _, benchmark = build_benchmark()

    assert set(
        benchmark[
            "treatment"
        ].unique()
    ).issubset(
        {
            0,
            1,
        }
    )


def test_contains_treated_and_control():
    """
    Benchmark should contain both treatment and control
    observations.
    """

    _, _, _, benchmark = build_benchmark()

    assert set(
        benchmark[
            "treatment"
        ].unique()
    ) == {
        0,
        1,
    }


def test_treatment_matches_price_or_promotion():
    """
    Main treatment should equal:

        price exposure OR promotion exposure.
    """

    _, _, _, benchmark = build_benchmark()

    expected = (
        (
            benchmark[
                "treatment_price_exposure"
            ] == 1
        )
        |
        (
            benchmark[
                "treatment_promotion_exposure"
            ] == 1
        )
    ).astype(
        int
    )

    assert (
        benchmark[
            "treatment"
        ]
        ==
        expected
    ).all()


# ============================================================
# Propensity score
# ============================================================


def test_propensity_score_is_bounded():
    """
    True propensity must be a valid probability.
    """

    _, _, _, benchmark = build_benchmark()

    score = benchmark[
        "propensity_score_true"
    ]

    assert (
        score >= 0.0
    ).all()

    assert (
        score <= 1.0
    ).all()


def test_propensity_score_has_variation():
    """
    Propensity scores should vary across observations.
    """

    _, _, _, benchmark = build_benchmark()

    assert benchmark[
        "propensity_score_true"
    ].nunique() > 1


# ============================================================
# Potential outcomes
# ============================================================


def test_potential_outcomes_are_probabilities():
    """
    Y(0) and Y(1) should remain valid probabilities.
    """

    _, _, _, benchmark = build_benchmark()

    for column in [
        "potential_outcome_y0",
        "potential_outcome_y1",
    ]:

        assert (
            benchmark[
                column
            ] >= 0.0
        ).all()

        assert (
            benchmark[
                column
            ] <= 1.0
        ).all()


def test_y0_matches_counterfactual_probability():
    """
    Y(0) should equal the published no-competitor
    counterfactual churn probability.
    """

    _, _, _, benchmark = build_benchmark()

    assert (
        benchmark[
            "potential_outcome_y0"
        ].round(
            6
        )
        ==
        benchmark[
            "counterfactual_churn_probability"
        ].round(
            6
        )
    ).all()


def test_y1_matches_observed_structural_probability():
    """
    Y(1) should equal:

        counterfactual probability
        +
        incremental competitive effect

    subject to the benchmark probability bounds.
    """

    _, _, _, benchmark = build_benchmark()

    expected = (
        benchmark[
            "counterfactual_churn_probability"
        ]
        +
        benchmark[
            "incremental_churn_probability_true"
        ]
    ).clip(
        lower=0.0001,
        upper=0.95,
    )

    assert (
        benchmark[
            "potential_outcome_y1"
        ].round(
            6
        )
        ==
        expected.round(
            6
        )
    ).all()


def test_ite_identity():
    """
    Individual treatment effect must satisfy:

        ITE = Y(1) - Y(0)
    """

    _, _, _, benchmark = build_benchmark()

    expected = (
        benchmark[
            "potential_outcome_y1"
        ]
        -
        benchmark[
            "potential_outcome_y0"
        ]
    )

    assert (
        benchmark[
            "individual_treatment_effect"
        ]
        ==
        expected
    ).all()


# ============================================================
# Observed potential outcome
# ============================================================


def test_observed_probability_follows_treatment():
    """
    Observed potential-outcome probability must follow the
    fundamental consistency relationship:

        Y_obs =
            T * Y(1)
            +
            (1-T) * Y(0)
    """

    _, _, _, benchmark = build_benchmark()

    expected = (
        benchmark[
            "treatment"
        ]
        * benchmark[
            "potential_outcome_y1"
        ]
        +
        (
            1
            - benchmark[
                "treatment"
            ]
        )
        * benchmark[
            "potential_outcome_y0"
        ]
    )

    assert (
        benchmark[
            "observed_outcome_probability"
        ].round(
            6
        )
        ==
        expected.round(
            6
        )
    ).all()


def test_observed_outcome_is_binary():
    """
    Sampled observed outcome should contain only 0 and 1.
    """

    _, _, _, benchmark = build_benchmark()

    assert set(
        benchmark[
            "observed_outcome"
        ].unique()
    ).issubset(
        {
            0,
            1,
        }
    )


# ============================================================
# Population causal estimands
# ============================================================


def test_ate_identity():
    """
    Published ATE should equal mean ITE in final benchmark.
    """

    _, _, _, benchmark = build_benchmark()

    expected = round(
        float(
            benchmark[
                "individual_treatment_effect"
            ].mean()
        ),
        8,
    )

    assert (
        benchmark[
            "ate_true"
        ].nunique()
        == 1
    )

    assert benchmark[
        "ate_true"
    ].iloc[
        0
    ] == expected


def test_att_identity():
    """
    Published ATT should equal mean ITE among treated rows.
    """

    _, _, _, benchmark = build_benchmark()

    treated = benchmark[
        benchmark[
            "treatment"
        ] == 1
    ]

    assert not treated.empty

    expected = round(
        float(
            treated[
                "individual_treatment_effect"
            ].mean()
        ),
        8,
    )

    assert benchmark[
        "att_true"
    ].iloc[
        0
    ] == expected


def test_atu_identity():
    """
    Published ATU should equal mean ITE among controls.
    """

    _, _, _, benchmark = build_benchmark()

    untreated = benchmark[
        benchmark[
            "treatment"
        ] == 0
    ]

    assert not untreated.empty

    expected = round(
        float(
            untreated[
                "individual_treatment_effect"
            ].mean()
        ),
        8,
    )

    assert benchmark[
        "atu_true"
    ].iloc[
        0
    ] == expected


# ============================================================
# Heterogeneous treatment effects
# ============================================================


def test_price_sensitivity_segments_valid():
    """
    Price-sensitivity segmentation should be interpretable.
    """

    _, _, _, benchmark = build_benchmark()

    assert set(
        benchmark[
            "price_sensitivity_segment"
        ].unique()
    ).issubset(
        {
            "low",
            "medium",
            "high",
        }
    )


def test_customer_segment_cate_identity():
    """
    Published customer-segment CATE should equal group mean
    of individual treatment effects.
    """

    _, _, _, benchmark = build_benchmark()

    expected = (
        benchmark.groupby(
            "customer_segment",
            observed=True,
        )[
            "individual_treatment_effect"
        ]
        .mean()
    )

    for segment, true_cate in (
        expected.items()
    ):

        rows = benchmark[
            benchmark[
                "customer_segment"
            ]
            == segment
        ]

        assert not rows.empty

        actual = rows[
            "cate_customer_segment_true"
        ].iloc[
            0
        ]

        assert round(
            float(
                actual
            ),
            10,
        ) == round(
            float(
                true_cate
            ),
            10,
        )


def test_price_segment_cate_identity():
    """
    Published price-sensitivity CATE should equal group mean
    ITE for that segment.
    """

    _, _, _, benchmark = build_benchmark()

    expected = (
        benchmark.groupby(
            "price_sensitivity_segment",
            observed=True,
        )[
            "individual_treatment_effect"
        ]
        .mean()
    )

    for segment, true_cate in (
        expected.items()
    ):

        rows = benchmark[
            benchmark[
                "price_sensitivity_segment"
            ]
            == segment
        ]

        assert not rows.empty

        actual = rows[
            "cate_price_sensitivity_true"
        ].iloc[
            0
        ]

        assert round(
            float(
                actual
            ),
            10,
        ) == round(
            float(
                true_cate
            ),
            10,
        )


# ============================================================
# Treatment-effect diversity
# ============================================================


def test_contains_nonzero_treatment_effects():
    """
    Benchmark should contain meaningful causal effects.
    """

    _, _, _, benchmark = build_benchmark()

    assert (
        benchmark[
            "individual_treatment_effect"
        ].abs()
        > 0
    ).any()


def test_contains_positive_treatment_effects():
    """
    Some competitive treatments should increase churn risk.
    """

    _, _, _, benchmark = build_benchmark()

    assert (
        benchmark[
            "individual_treatment_effect"
        ] > 0
    ).any()


def test_contains_negative_treatment_effects_when_available():
    """
    Upstream synthetic system supports negative competitive
    effects, e.g. competitor outages.

    The benchmark should preserve them when they are present
    in the sampled source observations.
    """

    _, _, _, benchmark = build_benchmark()

    source_negative = (
        benchmark[
            "incremental_churn_probability_true"
        ] < 0
    )

    if source_negative.any():

        assert (
            benchmark.loc[
                source_negative,
                "individual_treatment_effect",
            ] < 0
        ).all()


# ============================================================
# No leakage / key integrity
# ============================================================


def test_customer_month_unique():
    """
    Each causal benchmark observation should map to a unique
    customer-month.
    """

    _, _, _, benchmark = build_benchmark()

    assert not benchmark.duplicated(
        [
            "customer_id",
            "month",
        ]
    ).any()


def test_month_is_datetime():
    """
    Benchmark month should remain a datetime type.
    """

    _, _, _, benchmark = build_benchmark()

    assert pd.api.types.is_datetime64_any_dtype(
        benchmark[
            "month"
        ]
    )


# ============================================================
# Reproducibility
# ============================================================


def test_reproducible():
    """
    Same seed and configuration should generate the same
    benchmark.
    """

    first = build_benchmark(
        sample_size=1_000,
        seed=123,
    )[
        3
    ]

    second = build_benchmark(
        sample_size=1_000,
        seed=123,
    )[
        3
    ]

    pd.testing.assert_frame_equal(
        first,
        second,
    )


def test_different_seed_changes_benchmark():
    """
    Different random seeds should generate different
    benchmark populations.
    """

    first = build_benchmark(
        sample_size=1_000,
        seed=100,
    )[
        3
    ]

    second = build_benchmark(
        sample_size=1_000,
        seed=200,
    )[
        3
    ]

    assert not first.equals(
        second
    )