---
id: EVAL-005
type: eval
title: Comparison Metrics Gate Review
summary: Metric schema from pyssp_vv.evidence and the gate rules implemented in the local workflow.
date: 2026-10-23
status: current
pb_exempt: true
---

# Comparison Metrics Gate Review

**Review ID:** IMP-CAND-J
**Scope:** comparison metrics, summary fields, and the gate in
`scripts/workflow/gate.py`.

---

## 1. Metrics Inventory

Measurement is produced by `pyssp_vv.measure.metric_rows` and composed per pair
by `pyssp_workflow.compare.compare_csvs`. The reviewed column schema
lives in `pyssp_vv.evidence.METRIC_COLUMNS`; `MetricRow` keeps it verbatim.

### 1.1 Per-Signal Rows (`metrics.csv`)

- **Identity:** `signal`, `run_a_label`, `run_b_label`. `run_a` is the
  reference, `run_b` the candidate.
- **Pointwise error:** `max_abs_error`, `mean_abs_error`, `rmse`.
- **Shift-tolerant error:** `max_shift_abs_error`, `shift_samples`. The gate
  judges on this value, because ordinary co-simulation scheduling skew must not
  fail an otherwise matching signal.
- **Normalised error:** `normalisation`, `denominator`,
  `normalised_max_abs_error`.
- **Range context:** `run_a_min`, `run_a_max`, `run_b_min`, `run_b_max`.
- **Quality context:** `coverage`, `undefined`.

### 1.2 Per-Comparison Summary (`comparison.json`)

`pyssp_vv.evidence.ComparisonSummary` records:

- Labels: `run_a_label`, `run_b_label`.
- Shape: `time_points`, `compared_signal_count`.
- Errors: `max_abs_error`, `max_shift_abs_error`, `mean_abs_error`, `rmse`,
  `max_rel_error`.
- Quality: `min_coverage`.

The manifest also records the `gate` object with `status` and `reasons`.

### 1.3 Batch Summary (`comparisons.json`)

`_summarize_batch()` writes:

- `backend_count`, `comparison_count`.
- `max_signal_invariant_abs_error` across pairs.
- `gate_result`, the pessimistic combination of the pair verdicts.

---

## 2. Gate Specification

The gate is implemented in `scripts/workflow/gate.py`; judgment primitives come
from `pyssp_vv.judge`.

### 2.1 Configuration

`GateConfig` carries three values, frozen from the registry into `setup.json`:

- `atol = 1e-3`: absolute tolerance for trajectory comparison.
- `rtol = 1e-2`: relative tolerance for trajectory comparison.
- `max_invariant_abs_error = 1e-8`: absolute tolerance for model signal
  invariants.

Trajectory comparison uses `MetricName.MAX_ABS` on the shift-tolerant value,
with `SHIFT_TOLERANCE_SAMPLES = 2` searched lags and the same number of samples
excluded at each series edge.

### 2.2 Verdicts

- **`pass`:** every judged signal meets its criterion.
- **`fail`:** at least one judged signal misses its criterion.
- **`invalid`:** nothing was measured, or a comparison is not fit to judge.
- **`not_evaluated`:** no judgment ran.
- **Combination:** `invalid` dominates `fail`; `fail` dominates `pass`.

Reasons are recorded as `signal: code (detail)` strings.

---

## 3. Threshold Guidance

- Trajectory thresholds come from the registry `gate` entry per case, never
  from the study descriptor.
- Fixture classes differ: deterministic signal-propagation fixtures tolerate
  the least deviation, composite fixtures the most.
- Model signal invariants use the separate, tighter
  `max_invariant_abs_error`.
- A signal with a near-zero expected range is judged by absolute error; a
  scaled criterion is not implemented.

---

## 4. Pass / Fail / Invalid Criteria

- **PASS:** all compared signals are present and within tolerance; invariants
  hold.
- **FAIL:** a judged trajectory signal exceeds `atol`/`rtol`, or an invariant
  exceeds `max_invariant_abs_error`.
- **INVALID:** no signals were measured, or the measurement cannot support a
  judgment.
- **ERROR:** a run or comparison did not complete; no verdict is written.

---

## 5. Traceability

- **Metrics producer:** `pyssp_vv.measure.metric_rows`.
- **Schema:** `pyssp_vv.evidence.METRIC_COLUMNS`, `MetricRow`,
  `ComparisonSummary`.
- **Composition:** `pyssp_workflow.compare.compare_csvs`.
- **Gate:** `scripts/workflow/gate.py`, `evaluate_gate()` and
  `combine_gate_outcomes()`.
- **Policy inputs:** registry `gate` entry, `workflow/model_policy.py` signal
  invariants.
- **Comparisons:** `EVAL-004` backend adapter review, `EVAL-006` manifest field
  review, `EVAL-001` co-simulation test strategy.
