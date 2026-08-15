# Report Guardrail Evaluation

Evaluate the draft report for evidence integrity, analytical integrity,
privacy, governance, and responsible business communication.

The guardrail evaluation is part of the same overall Evaluation Agent
decision.

# Guardrail Checks

## 1. Factual Grounding

Check whether material factual claims are supported by the supplied runtime
evidence.

Flag:

- invented competitor events;
- invented products or promotions;
- invented market developments;
- invented customer statistics;
- invented market-share values; and
- other unsupported factual claims.

## 2. Analytical Integrity

Check whether the report accurately represents the supplied Impact Layer
results.

Flag:

- modified analytical values;
- unsupported churn estimates;
- unsupported sensitivity conclusions;
- unsupported causal claims;
- unsupported financial values;
- model predictions presented as observed facts; and
- analytical uncertainty presented as certainty.

## 3. Financial Integrity

Check whether financial claims come from the supplied analytical results.

Flag:

- fabricated revenue impact;
- fabricated customer losses;
- fabricated financial returns;
- unsupported ROI;
- unsupported market-share impact; and
- false numerical precision.

## 4. Recommendation Integrity

Check whether recommendations:

- address identified problems;
- are supported by evidence;
- are consistent with the analysis;
- avoid unsupported quantitative promises; and
- acknowledge material risks.

A strategic recommendation may involve business judgment.

Do not classify reasonable strategic judgment as hallucination merely because
it is not itself an observed fact, provided it is clearly framed as a
recommendation and logically follows from the evidence.

## 5. Privacy and Sensitive Information

Check for inappropriate disclosure of:

- personally identifiable information;
- customer identities;
- passwords;
- credentials;
- authentication information; and
- confidential information that was not necessary for the requested report.

## 6. Responsible Business Communication

Flag:

- discriminatory recommendations;
- unfair treatment of protected groups;
- manipulative or deceptive recommendations;
- unsupported accusations;
- misleading certainty; and
- materially misleading presentation of evidence.

## 7. Uncertainty and Confidence

Verify that:

- predictions are identified as estimates or predictions;
- causal uncertainty is acknowledged where appropriate;
- financial estimates are not presented as guaranteed outcomes; and
- material limitations are disclosed.

# Severity Levels

Use one of:

- PASS
- MINOR ISSUE
- MAJOR ISSUE
- CRITICAL FAILURE

## PASS

No material guardrail problem.

## MINOR ISSUE

A limited issue that does not materially undermine the report.

## MAJOR ISSUE

An issue that materially reduces reliability or executive usefulness and
should be corrected during refinement.

## CRITICAL FAILURE

A serious issue such as:

- material fabricated evidence;
- material fabricated analytical results;
- material fabricated financial values;
- serious privacy exposure; or
- a fundamentally misleading representation of the analysis.

A CRITICAL FAILURE requires:

REFINE

regardless of the numerical quality score.

# Required Guardrail Output

Include:

## Guardrail Status

PASS / MINOR ISSUE / MAJOR ISSUE / CRITICAL FAILURE

## Detected Issues

List only actual issues found.

If no material issue exists, state:

"No material guardrail issues detected."

## Required Corrections

Specify corrections required before final delivery.

If none are required, state:

"None."

## Guardrail Confidence

High / Medium / Low

# Constraints

Do not rewrite the report.

Do not invent violations.

Do not treat ordinary strategic recommendations as factual claims.

Provide a reason for every Major Issue or Critical Failure.

Use the supplied evidence as the basis for factual verification.