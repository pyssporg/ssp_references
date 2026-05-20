# IMP-CAND-J: Comparison Metrics Gate Review

## Status

Proposed

## Layer

Verification (04)

## Theme

Comparison metrics audit — decide which metrics are gate-worthy vs diagnostic

## Evidence

- Test strategy describes comparison using max_abs_error, MAE, RMSE
- No criteria exist for which metrics constitute acceptance vs diagnostics
- Open question in review-plan: "Which summary metrics should become acceptance criteria?"

## Current Pain Or Risk

Without gating criteria, every comparison result requires human interpretation. Automated pipeline gates cannot determine pass/fail, reducing the pipeline's value for CI/CD use.

## Proposed Improvement

Define which metrics are gate-worthy (trigger pipeline failure) vs diagnostic-only (informational). Document per-fixture-class tolerance thresholds. Produce a gate specification that can be implemented in the comparison pipeline.

## Expected Benefit

The comparison pipeline produces actionable pass/fail results, not just raw metrics. CI/CD integration becomes possible.

## Risk And Blast Radius

Medium. Affects comparison output interpretation. May require minor comparison code changes to implement the gate.

## Suggested Priority

Medium

## Task Contract Seed

Review the comparison metrics in `scripts/workflow/comparison.py` and the test strategy. Produce a gate specification: (1) which metrics are gate-worthy, (2) per-fixture-class tolerance thresholds, (3) what constitutes a pass/fail per combination, (4) implementation recommendation.

## Out Of Scope

Expanding the backend set or adding new models.

## Traceability

- Product: PD-001 (comparison methodology) — how comparison results are interpreted
- Verification: `04-verification/co_simulation_test_strategy.md` — comparison policy
- Implementation: `scripts/workflow/comparison.py` — metric calculation