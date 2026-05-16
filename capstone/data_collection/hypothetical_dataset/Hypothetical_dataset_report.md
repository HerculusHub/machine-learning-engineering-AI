**Hypothetical Dataset: U.S. Mobile Operator Competition**

**🔹 Dataset Description**

Provides a hypothetical dataset of competitor behavior among mobile network operators in the United States.
Below is a hypothetical dataset that captures competitor behavior among major U.S. mobile network operators like Verizon, AT&T, and T-Mobile.


Each row represents **monthly competitive behavior metrics** for a
carrier in a given region.

| **Column Name**        | **Description**                         |
|------------------------|-----------------------------------------|
| month                  | Time period                             |
| operator               | Carrier name                            |
| region                 | Market region (e.g., West, Midwest)     |
| avg_price_plan         | Average monthly plan price (\$)         |
| promo_intensity        | Scale (0–10) of promotions/discounts    |
| customer_churn_rate    | % of customers leaving                  |
| net_adds               | Net subscriber gain/loss                |
| avg_data_speed         | Mbps (network performance proxy)        |
| coverage_score         | Scale (0–100)                           |
| marketing_spend        | Monthly marketing spend (\$M)           |
| competitor_price_index | Relative price vs competitors (1 = avg) |
| customer_satisfaction  | Score (0–10)                            |

**1. Dataset Architecture (Realistic Design)**

Instead of one flat table, use a **multi-table schema** (like real
telecom data warehouses):

**🔹 Core Tables**

**1. market_monthly_metrics (FACT TABLE)**

| **Column**      | **Description**         |
|-----------------|-------------------------|
| month           | Monthly timestamp       |
| region          | Market (state or metro) |
| operator        | Carrier                 |
| subscribers     | Total subscribers       |
| net_adds        | Monthly net adds        |
| churn_rate      | % leaving               |
| arpu            | Avg revenue per user    |
| avg_price       | Plan pricing            |
| promo_intensity | 0–10                    |
| marketing_spend | \$                      |
| network_speed   | Mbps                    |
| coverage_score  | 0–100                   |
| satisfaction    | 0–10                    |

**2. competitor_actions**

Tracks **strategic moves** (critical for causal AI)

| **Column**     | **Description**            |
|----------------|----------------------------|
| month          | Timestamp                  |
| operator       | Carrier                    |
| action_type    | price_cut / promo / bundle |
| magnitude      | % change                   |
| target_segment | prepaid / postpaid         |

**3. market_context**

External factors (VERY important)

| **Column**        | **Description** |
|-------------------|-----------------|
| region            | Market          |
| month             | Timestamp       |
| population        | Market size     |
| median_income     | Economic factor |
| unemployment_rate | Macro signal    |
| iphone_release    | 0/1             |
| holiday_season    | 0/1             |

**4. customer_segments**

| **Column**        | **Description**            |
|-------------------|----------------------------|
| segment           | prepaid / premium / family |
| price_sensitivity | 0–1                        |
| churn_baseline    | baseline churn             |

