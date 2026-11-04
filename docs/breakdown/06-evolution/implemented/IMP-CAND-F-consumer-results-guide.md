# IMP-CAND-F: Consumer-Facing Results Interpretation Guide

## Status

Proposed

## Layer

Operation (05) — consumer/user experience

## Theme

Results interpretation for non-runner consumers

## Evidence

- Architecture doc Sections 4–5 describe data flow and runtime contract
- Test strategy describes comparison policy but not concrete output format
- No documented `metrics.csv` column schema
- No example `comparisons.json` or `simulation.json` output
- No interpretation guidance for metrics (MAE, RMSE, max error)

## Current Pain Or Risk

A consumer who wants to understand what the repository produces without running the pipeline must piece together output formats from path descriptions and source code inference. Comparison metrics are not documented with interpretation guidance.

## Proposed Improvement

Create a results interpretation document at `05-operation/results-interpretation.md` that: (1) documents the `metrics.csv` schema, (2) shows annotated example `comparisons.json`, (3) documents per-signal comparison metrics with interpretation guidance, (4) maps fixture classes to expected tolerance ranges, (5) links to test strategy's comparison policy.

## Expected Benefit

A consumer can inspect the `artifacts/comparisons/` directory and understand every file without reading source code.

## Risk And Blast Radius

Low. Single new file. Risk of format changes in comparison code — mitigated by maintenance note.

## Suggested Priority

Medium

## Task Contract Seed

Create `05-operation/results-interpretation.md` documenting: `metrics.csv` column schema, annotated example `comparisons.json`, per-signal metric definitions (max absolute error, MAE, RMSE) with interpretation guidance, fixture-class-specific tolerance expectations, maintenance note linking to comparison source code.

## Out Of Scope

Changing comparison code or metric definitions. Modifying test strategy.

## Traceability

- Intent: Result trajectories against baselines determine correctness — guide makes results interpretable
- Product: PD-001 (comparison methodology) — documents concrete output of engine-to-engine comparison
- Architecture: Runtime contract artifacts from `02-architecture/architecture.md`
- Verification: References `04-verification/co_simulation_test_strategy.md`