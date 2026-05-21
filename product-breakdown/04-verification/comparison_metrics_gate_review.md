# Comparison Metrics Gate Review

**Review ID:** IMP-CAND-J  
**Date:** 2026-05-20  
**Type:** Read-only metrics gate specification  
**Scope:** All comparison pipeline metrics — per-signal, per-comparison summary, and batch summary

---

## 1. Metrics Inventory

All metrics are produced by `scripts/utils/comparison.py` and consumed via the comparison pipeline in `scripts/workflow/comparison.py`. The table below catalogs every metric, its location, and its role in a potential gate.

### 1.1 Per-Signal Metrics (written to metrics CSV)

| # | Metric | Type | Description | Gate Role |
|---|--------|------|-------------|-----------|
| 1 | `signal` | string | Canonical signal name | Identity (not a metric) |
| 2 | `max_abs_error` | float | Max absolute difference across resampled time grid | **Primary gate** |
| 3 | `mean_abs_error` | float | Mean absolute difference across resampled time grid | Diagnostic |
| 4 | `rmse` | float | Root mean square error | Diagnostic |
| 5 | `run_a_label` | string | Label for reference run A | Identity |
| 6 | `run_a_min` | float | Minimum value of run A signal (resampled) | Diagnostic — range context |
| 7 | `run_a_max` | float | Maximum value of run A signal (resampled) | Diagnostic — range context |
| 8 | `run_b_label` | string | Label for comparison run B | Identity |
| 9 | `run_b_min` | float | Minimum value of run B signal (resampled) | Diagnostic — range context |
| 10 | `run_b_max` | float | Maximum value of run B signal (resampled) | Diagnostic — range context |

**Producer:** `compare_result_sets()` in `scripts/utils/comparison.py` (line 152–165)  
**Consumer:** `compare_runs()` in `scripts/workflow/comparison.py` via `write_metrics_csv()` (line 300)

### 1.2 Per-Comparison Summary Metrics (stored in comparison manifest `comparison.json`)

| # | Metric | Type | Description | Gate Role |
|---|--------|------|-------------|-----------|
| 1 | `run_a_label` | string | Label for reference run A | Identity |
| 2 | `run_b_label` | string | Label for comparison run B | Identity |
| 3 | `time_points` | int | Number of resampled time points | Diagnostic — coverage check |
| 4 | `compared_signal_count` | int | Number of signals compared | Diagnostic — coverage check |
| 5 | `max_abs_error` | float | Max across all signals' `max_abs_error` | **Primary gate** (aggregate) |
| 6 | `mean_abs_error` | float | Mean across all signals' `mean_abs_error` | Diagnostic |
| 7 | `rmse` | float | Mean across all signals' `rmse` | Diagnostic |

**Producer:** `compare_result_sets()` in `scripts/utils/comparison.py` (line 167–175)  
**Consumer:** `ComparisonRun.to_dict()` → written to manifest via `write_manifest()`

### 1.3 Batch Summary Metrics (stored in batch manifest `comparison_batch.json`)

| # | Metric | Type | Description | Gate Role |
|---|--------|------|-------------|-----------|
| 1 | `backend_count` | int | Number of backends compared | Diagnostic — coverage check |
| 2 | `comparison_count` | int | Number of pairwise comparisons | Diagnostic — coverage check |
| 3 | `max_abs_error` | float | Max across all comparison `max_abs_error` | **Primary gate** (batch) |
| 4 | `max_rel_error` | float | Max relative error across all comparisons | **Stability gate** |
| 5 | `min_compared_signal_count` | int | Minimum signal count across all comparisons | **Stability gate** — signal integrity |

**Producer:** `_summarize_batch()` in `scripts/workflow/comparison.py` (line 265–287)  
**Consumer:** `ComparisonBatchRun.to_dict()` → written to batch manifest via `write_manifest()`

---

## 2. Gate Specification

### 2.1 Primary Gate Metric

**`max_abs_error`** — selected as the single primary gate metric because:

- **Clear:** A direct signal-level difference in the same units as the signal. No interpretation formula needed.
- **Interpretable:** A value of `0.005` means "the two simulations differ by at most 0.005 units at any time point."
- **Bounded:** Positive real number; zero for identical signals; grows unbounded for diverging signals.
- **Available at every level:** Per-signal, per-comparison summary, and batch summary.
- **Conservative:** Catches spikes and outliers that `mean_abs_error` or `rmse` would smooth over.

**Gate decision rule (per-comparison):**
- **PASS** if `max_abs_error < threshold` for **all** compared signals.
- **FAIL** if any signal's `max_abs_error >= threshold`.

### 2.2 Diagnostic Metrics

These metrics inform analysis but do not independently trigger gate failure:

| Metric | Diagnostic Purpose |
|--------|--------------------|
| `mean_abs_error` | Indicates typical error magnitude; a low mean + high max suggests an outlier/spike worth investigation |
| `rmse` | Amplifies large errors; useful to distinguish distributed noise (low rmse relative to max) from concentrated deviations (rmse close to max) |
| `run_a_min` / `run_a_max` / `run_b_min` / `run_b_max` | Signal range context; a `max_abs_error` of 0.01 means different things for a signal ranging ±100 vs ±0.01 |
| `time_points` | Validates the resampling grid; unexpected counts indicate window misconfiguration |
| `compared_signal_count` | Validates all expected signals were present and compared |

### 2.3 Stability Metrics (Batch Level)

| Metric | Gate Role | Rule |
|--------|-----------|------|
| `max_rel_error` | **Stability gate** | Flags backends whose relative deviation exceeds expectations. Fail if `max_rel_error > threshold` (threshold depends on fixture class — see Section 3). |
| `min_compared_signal_count` | **Signal integrity gate** | Fail if `min_compared_signal_count != expected_signal_count`. A lower count means a comparison pair silently dropped signals. |

---

## 3. Per-Fixture-Class Threshold Recommendations

Thresholds are based on the fixture hierarchy defined in ADR-002 and the tolerance guidance in `co_simulation_test_strategy.md`.

| Fixture Class | Examples | Max Abs Error Threshold | Max Rel Error Threshold | Rationale |
|---------------|----------|------------------------|------------------------|-----------|
| Simple Reference Models | `BouncingBall`, `VanDerPol`, `Dahlquist`, `Stair`, `Resource` | `< 1e-3` | `< 1e-2` | Isolated numerical behavior; small error expected across backends. Strategy: "tighter tolerances." |
| Deterministic Signal-Propagation | `Modelica.Blocks.Math.Add`, `Gain`, `Product`, `Step`, `Sine` composed SSPs | `< 1e-6` | `< 1e-5` | Purely algebraic/stepwise; nearly bitwise agreement expected. Strategy: "very tight tolerances." |
| Composite SSP Models | `dcmotor`, `embrace` | `< 1e-2` | `< 1e-1` | Multi-component coupling; solver and scheduling differences amplify. Strategy: "broader tolerances." |
| Special-Purpose | Custom test fixtures not fitting the above classes | `< 1e-3` | `< 1e-2` | Moderate default; adjust per-fixture as needed via registry annotatations. |

**Notes:**

- Thresholds apply to `max_abs_error` **per signal**, not to the summary aggregate. The gate checks every signal individually.
- `max_rel_error` is a batch-level stability metric. The threshold applies to the batch summary value.
- Deterministic propagation tests should additionally verify **exact signal relationships** (gain factor, summation, timing) as described in the test strategy, not only aggregate error pass/fail.
- If a signal's expected range is near-zero (e.g., a signal that should be identically zero), `max_abs_error` at 1e-6 may be misleadingly strict — consider `max_rel_error` or a scaled threshold in such cases. This is a future refinement, not a current gap.

---

## 4. Pass / Fail / Error Criteria

### 4.1 PASS

- All compared signals have `max_abs_error < threshold` (per fixture class).
- All expected signals are present (no `KeyError` from missing signals).
- All resampled series contain finite values (no NaN propagation).
- Batch-level stability checks pass: `max_rel_error < threshold` and `min_compared_signal_count == expected_signal_count`.

### 4.2 FAIL

- **Any signal** has `max_abs_error >= threshold`.
- **Missing signals:** `_select_signal_series()` raises `KeyError` because a configured compare signal is absent from one or both result sets.
- **NaN values detected:** After resampling, any signal series contains NaN values (indicating interpolation failure, data gaps, or unreachable time points).
- **Unstable spikes:** The `max_abs_error` gate above already catches large spikes at the per-signal level.
- **Batch signal count mismatch:** `min_compared_signal_count` differs from the configured signal list length.

### 4.3 ERROR (Simulation or comparison did not complete)

- Simulation run status is `"failed"` or `"skipped"` — comparison cannot proceed.
- Comparison pipeline exception (e.g., file not found, malformed CSV, time column missing).
- Comparison status is `"failed"` — comparison manifest records an error string.
- Batch validation raises `ValueError` (mismatched models/cases/windows/signals across runs).

---

## 5. Implementation Recommendation

Add gate check logic to `compare_runs()` in `scripts/workflow/comparison.py`.

**Recommended approach:**

1. **Add a `GateConfig` dataclass** (or extend `ComparisonRequest`) to hold per-fixture-class thresholds:

```python
@dataclass(frozen=True)
class GateConfig:
    max_abs_error_threshold: float
    max_rel_error_threshold: float
```

2. **Add a `gate_result` field to `ComparisonRun`** to record pass/fail/error:

```python
@dataclass(frozen=True)
class ComparisonRun:
    request: ComparisonRequest
    summary: dict[str, float | int | str]
    metrics_path: Path
    status: str = "completed"
    error: str | None = None
    gate_result: str | None = None  # "pass", "fail", or None (not evaluated)
```

3. **In `compare_runs()`**, after computing metrics, run gate checks:

```python
def _check_gate(
    metrics: list[dict[str, float | str]],
    threshold: float,
    expected_signals: tuple[str, ...],
) -> str:
    if len(metrics) != len(expected_signals):
        return "fail"  # missing signals
    for row in metrics:
        if row["max_abs_error"] >= threshold:
            return "fail"
        if not np.isfinite(row["max_abs_error"]):
            return "fail"  # NaN or inf
    return "pass"
```

4. **Propagate gate result to the batch summary.** Add an aggregate `gate_result` field to `ComparisonBatchRun`:

```python
@dataclass(frozen=True)
class ComparisonBatchRun:
    request: ComparisonBatchRequest
    comparisons: tuple[ComparisonRun, ...]
    summary: dict[str, float | int | str]
    status: str = "completed"
    error: str | None = None
    gate_result: str | None = None  # "pass" if ALL comparisons pass, "fail" if ANY fails
```

5. **Threshold selection** should come from a registry annotation or a lookup table keyed by fixture class. The simplest approach: add a `gate_thresholds` field to the simulation registry entry per model/case, defaulting to the special-purpose class thresholds (`1e-3` / `1e-2`).

6. **Write gate result to the comparison manifest** for downstream pipeline inspection. No separate gate report file is needed — the `gate_result` field on the existing manifest is sufficient.

### 5.1 Out of Scope for This Implementation

- Adding per-signal tolerance overrides (all signals use the same threshold per comparison).
- Adding the gate check to the batch-level `max_rel_error` (deferred until relative error calculation is confirmed correct).
- Adding a `--fail-on-gate` CLI flag to `run_comparisons.py` (the gate result is stored; the CI layer decides whether to fail on it).

---

## 6. Traceability

| Artifact | Layer | Relationship |
|----------|-------|-------------|
| `04-verification/comparison_metrics_gate_review.md` (this document) | Verification (04) | Gate specification produced by this review |
| `06-evolution/backlog/IMP-CAND-J-comparison-metrics-gate-review.md` | Evolution (06) | Task contract — proposed this review as a candidate |
| `04-verification/co_simulation_test_strategy.md` | Verification (04) | Comparison policy: per-class tolerances, signal presence, NaN handling |
| `02-architecture/decisions/ADR-002.md` | Architecture (02) | Fixture hierarchy (four classes) mapped to threshold recommendations |
| `02-architecture/decisions/ADR-001.md` | Architecture (02) | Three-stage pipeline: build → simulate → compare; gate check added to the compare stage |
| `scripts/utils/comparison.py` | Implementation (03) | Metrics producer — all per-signal and summary metrics |
| `scripts/workflow/comparison.py` | Implementation (03) | Comparison pipeline — `compare_runs()` is the recommended gate insertion point |
| `04-verification/backend_adapter_review.md` | Verification (04) | Sister review (IMP-CAND-H): backend adapter contracts |
| `04-verification/manifest_field_review.md` | Verification (04) | Sister review (IMP-CAND-I): manifest field schemas |
| `04-verification/README.md` | Verification (04) | Verification layer index — this document is referenced from the table |

---

## 7. Decision Record

**Review finding:** The existing metrics pipeline produces all the data needed for automated gating. No additional metrics are required. The gap is entirely in pass/fail decision logic, which should be implemented in the comparison pipeline itself.

**Recommended action:** Implement the gate check in `compare_runs()` per Section 5. This is a self-contained change to the comparison workflow with no impact on the build or simulation stages.

**Backward compatibility:** Adding `gate_result` as an optional field to `ComparisonRun` and `ComparisonBatchRun` maintains backward compatibility with existing comparison manifests (they will simply not have the field until re-run).