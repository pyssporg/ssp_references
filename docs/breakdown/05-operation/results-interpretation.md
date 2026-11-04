---
id: INFO-006
type: info
title: Results Interpretation Guide
summary: How to read simulation and comparison artifacts.
date: 2026-10-23
status: current
pb_exempt: true
---

# Results Interpretation Guide

This document explains the output files produced by the comparison pipeline.
Use it to understand comparison metrics, interpret the gate verdict, and
diagnose mismatches between simulation backends.

## Artifact Layout

After running the full pipeline, comparison artifacts appear under:

```
artifacts/comparisons/<model>/<analysis>/<backend_a>_vs_<backend_b>/
├── comparison.json        # pairwise comparison manifest
└── metrics.csv            # per-signal comparison metrics

artifacts/comparisons/<model>/<analysis>/comparisons.json   # batch summary
```

## `metrics.csv` Schema

One row per signal per comparison. `run_a` is the reference, `run_b` the
candidate. Columns, in declared order:

- **Identity:** `signal`, `run_a_label`, `run_b_label`.
- **Pointwise error:** `max_abs_error`, `mean_abs_error`, `rmse`.
- **Shift-tolerant error:** `max_shift_abs_error`, `shift_samples`.
- **Normalised error:** `normalisation`, `denominator`,
  `normalised_max_abs_error`.
- **Range:** `run_a_min`, `run_a_max`, `run_b_min`, `run_b_max`.
- **Quality:** `coverage`, `undefined`.

The schema is `pyssp_vv.evidence.METRIC_COLUMNS`.

### Metric Interpretation

- **`max_abs_error`:** worst single-step deviation; a spike here with a low
  `mean_abs_error` points at a timing offset.
- **`max_shift_abs_error`:** the same maximum after searching the declared lag
  window; the gate judges this value.
- **`mean_abs_error`:** average per-step deviation; a broad difference.
- **`rmse`:** RMS of the errors; penalises large deviations.
- **`coverage`:** fraction of the grid where both series carry a value.
- **`undefined`:** reasons a derived value could not be computed.

## `comparison.json` Schema (pairwise)

- **Labels:** `reference_label`, `candidate_label` (written as `run_a_label`
  and `run_b_label` inside `summary`).
- **Paths:** `metrics` relative to the manifest.
- **Summary:** `time_points`, `compared_signal_count`, `max_abs_error`,
  `max_shift_abs_error`, `mean_abs_error`, `rmse`, `max_rel_error`,
  `min_coverage`.
- **Gate:** `gate.status` and `gate.reasons`.
- **Run status:** `status` and `error`.

## `comparisons.json` Schema (batch)

- **Request:** the compared runs and their manifests.
- **Comparisons:** each pair's record, manifest path, and gate.
- **Summary:** `backend_count`, `comparison_count`,
  `max_signal_invariant_abs_error`, `gate_result`.
- **Gate:** the pessimistic combination of the pair verdicts.

## Gate Criteria

The gate records `pass`, `fail`, or `invalid` per pair and per reference
comparison. `invalid` means the comparison was not fit to judge; it is not a
`fail`.

- **Pass:** every judged signal meets `atol`/`rtol`; invariants hold.
- **Fail:** a signal or invariant misses its criterion.
- **Invalid:** no measurement supported a judgment.
- **Tolerance source:** the registry `gate` entry, frozen into `setup.json`.

`run_comparisons.py` records gates without failing; `--fail-on-gate` exits
nonzero when any gate fails or is invalid.

## Fixture-Specific Notes

- **Deterministic signal-propagation** models have algebraically predictable
  outputs, so the gate runs at tight tolerances.
- **Simple reference models** show small solver-dependent drift.
- **Composite models** (dcmotor, embrace) show wider divergence from
  multi-FMU coupling and cross-component signal routing.

## Related

- `EVAL-001` - test strategy, fixture classes, and acceptance philosophy.
- `INFO-002` - runtime contract and artifact connection chain.
- `EVAL-005` - metric schema and gate rules.
