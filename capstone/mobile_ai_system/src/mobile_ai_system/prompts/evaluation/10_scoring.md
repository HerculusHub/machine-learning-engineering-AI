# Report Quality Scoring

## Runtime Inputs

Evaluate only the information supplied in the current runtime prompt.

Relevant inputs may include:

1. User Request
2. Retrieved Competitor Evidence
3. Impact Analysis Result
4. Draft Executive Report

Do not assume access to historical reports, memory, external research, or
other evidence unless explicitly supplied.

# Evaluation Dimensions

Evaluate the report on six dimensions.

All scores use the range:

0.00 to 1.00

## 1. Requirement Satisfaction — 20%

Determine whether the report:

- answers the user's actual request;
- addresses the requested competitor activity;
- addresses customer/churn impact when requested;
- addresses financial impact when requested; and
- provides strategic recommendations when requested.

Scoring guidance:

- 0.90–1.00: Fully satisfies the request.
- 0.80–0.89: Satisfies the request with only minor omissions.
- 0.70–0.79: Generally answers the request but has meaningful gaps.
- 0.60–0.69: Important requirements are missing.
- Below 0.60: Fails to answer major parts of the request.

## 2. Accuracy and Evidence Grounding — 25%

Determine whether:

- factual claims are supported by supplied evidence;
- analytical values match supplied analytical results;
- observed facts and model estimates are distinguished;
- unsupported facts are avoided;
- causal claims do not exceed supplied causal evidence; and
- financial claims are supported.

A material fabricated competitor event, customer statistic, analytical result,
or financial value should substantially reduce this score.

## 3. Completeness — 15%

Determine whether the report contains the material components required to
answer the user's request.

Relevant components may include:

- Executive Summary;
- Competitor Activity;
- Market Intelligence Assessment;
- Customer Churn Analysis;
- Causal Analysis;
- Financial Impact Assessment;
- Strategic Countermeasures;
- Key Risks;
- Supporting Evidence;
- Limitations; and
- Confidence Assessment.

Do not penalize a report merely because unavailable information is explicitly
identified as unavailable.

## 4. Logical Reasoning — 20%

Determine whether:

- conclusions follow from evidence;
- analytical results are interpreted correctly;
- assumptions are visible;
- uncertainty is acknowledged;
- strategic conclusions follow logically from the analysis; and
- recommendations address identified business problems.

Penalize unsupported leaps from evidence to conclusion.

## 5. Business Value — 15%

Determine whether the report:

- identifies decision-relevant findings;
- explains why findings matter;
- prioritizes important issues;
- provides actionable recommendations;
- communicates material risks; and
- supports executive decision making.

Avoid rewarding verbosity.

## 6. Report Organization — 5%

Determine whether the report has:

- clear structure;
- professional language;
- readable formatting;
- concise presentation;
- logical flow; and
- minimal unnecessary repetition.

# Overall Score

Calculate the weighted overall score:

Requirement Satisfaction × 0.20

Accuracy and Evidence Grounding × 0.25

Completeness × 0.15

Logical Reasoning × 0.20

Business Value × 0.15

Report Organization × 0.05

The overall score must be between:

0.00 and 1.00

# Quality Rating

Use:

- 0.90–1.00: Outstanding
- 0.80–0.89: Good
- 0.70–0.79: Acceptable
- 0.60–0.69: Weak
- Below 0.60: Poor

# Acceptance Threshold

The MVP acceptance threshold is:

0.80

Normally:

- Overall Score >= 0.80 → ACCEPT
- Overall Score < 0.80 → REFINE

However, a critical guardrail failure requires REFINE even when the numerical
score is 0.80 or higher.

# Required Evaluation Content

Provide:

## Overall Score

Return a decimal value from 0.00 to 1.00.

## Quality Rating

Outstanding / Good / Acceptable / Weak / Poor

## Detailed Scores

Provide scores for:

- Requirement Satisfaction
- Accuracy and Evidence Grounding
- Completeness
- Logical Reasoning
- Business Value
- Report Organization

## Strengths

Identify the most important strengths.

## Weaknesses

Identify material weaknesses only.

## Missing Information

Identify missing information that materially affects the report.

Do not describe information as missing when it was not required for the
user's request.

## Suggested Improvements

Provide specific changes that the Report Agent can perform during one
refinement pass.

## Evaluation Confidence

High / Medium / Low

# Constraints

Never rewrite the report.

Never fabricate errors.

Always justify material deductions.

Do not reward unsupported detail.

Do not penalize appropriate disclosure of uncertainty.