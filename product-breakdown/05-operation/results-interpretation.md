# Results Interpretation Guide

This document explains the output files produced by the comparison pipeline.
Use it to understand comparison metrics, interpret pass/fail results, and
diagnose mismatches between simulation backends.

## Artifact Layout

After running the full pipeline, comparison artifacts appear under:

```
artifacts/comparisons/<model>/<case>/<backend_a>_vs_<backend_b>/
├── comparison.json        # pairwise comparison manifest
└── metrics.csv            # per-signal comparison metrics

artifacts/comparisons/<model>/<case>/comparisons.json   # batch summary
```

## `metrics.csv` Schema

One row per signal per model per comparison. Columns:

| Column | Type | Description |
|--------|------|-------------|
| `model` | string | Model name (e.g. `BouncingBall`) |
| `signal` | string | Signal name as listed in `compare_signals` in the registry |
| `backend_a` | string | First backend in the pair (e.g. `ssp4sim`) |
| `backend_b` | string | Second backend in the pair (e.g. `omsimulator`) |
| `max_abs_error` | float | Maximum absolute difference across all time steps |
| `mae` | float | Mean absolute error across all time steps |
| `rmse` | float | Root mean square error across all time steps |
| `n_points` | int | Number of time steps compared |

### Metric Interpretation

| Metric | What It Measures | Interpretation |
|--------|-----------------|----------------|
| `max_abs_error` | Worst single-step deviation | A single outlier indicates a spike or timing shift; broad agreement otherwise is acceptable |
| `mae` | Average per-step deviation | Low MAE + spikes in max_abs_error → occasional glitch; both high → systematic difference |
| `rmse` | RMS of errors (penalizes large deviations) | RMSE >> MAE → large but infrequent errors; RMSE ≈ MAE → uniform small errors |

### Tolerance Guidance

| Fixture Class | Typical Tolerance | Rationale |
|--------------|-------------------|-----------|
| Deterministic signal-propagation | `max_abs_error < 1e-12` | Algebraically predictable; any deviation is a bug |
| Simple reference models | `max_abs_error < 1e-6` | Slight numerical drift across solvers is expected |
| Composite SSPs | `max_abs_error < 1e-4` | Multi-FMU coupling introduces solver-dependent variation |

## `comparison.json` Schema (pairwise)

```json
{
  "model": "BouncingBall",
  "case": "baseline",
  "backend_a": "ssp4sim",
  "backend_b": "omsimulator",
  "signals": ["h", "v", "t"],
  "status": "completed",
  "metrics_path": "artifacts/comparisons/BouncingBall/baseline/ssp4sim_vs_omsimulator/metrics.csv",
  "n_signals_matched": 3,
  "n_signals_total": 3,
  "start_time": 0.0,
  "end_time": 20.0
}
```

| Field | Description |
|-------|-------------|
| `model` | Model name |
| `case` | Simulation case name |
| `backend_a`, `backend_b` | The two backends being compared |
| `signals` | List of signals successfully compared |
| `status` | `completed`, `partial`, or `failed` |
| `metrics_path` | Relative path to the metrics CSV |
| `n_signals_matched` | Number of signals present in both backends' output |
| `n_signals_total` | Total signals requested for comparison |
| `start_time`, `end_time` | Simulation time window |

## `comparisons.json` Schema (batch)

```json
{
  "model": "BouncingBall",
  "case": "baseline",
  "pairs": ["ssp4sim_vs_omsimulator"],
  "comparisons": [
    "artifacts/comparisons/BouncingBall/baseline/ssp4sim_vs_omsimulator/comparison.json"
  ]
}
```

Lists all pairwise comparisons completed for a model/case combination.

## Pass/Fail Criteria

The comparison pipeline is **diagnostic** — it produces metrics but does not
enforce pass/fail gates. That decision belongs to the consumer.

As a rule of thumb:

| Condition | Assessment |
|-----------|-----------|
| All signals matched, all metrics within tolerance | ✅ Pass |
| All signals matched, metrics outside tolerance | ⚠️ Investigate — likely numerical drift or scheduling difference |
| Signals missing (`n_signals_matched < n_signals_total`) | ❌ Fail — output schema mismatch or backend limitation |
| Status is `failed` | ❌ Fail — comparison script error or incompatible output format |

## Fixture-Specific Notes

- **Deterministic signal-propagation** models (signal_step_gain, signal_step_add, etc.): these have algebraically predictable outputs. Any `max_abs_error > 1e-12` across backends is a strong signal of a scheduling, propagation, or algebraic-loop issue.
- **Simple reference models** (BouncingBall, VanDerPol, etc.): small numerical tolerance differences between solvers are normal. Tighter tolerances (`1e-8`) can be used if both backends use the same solver.
- **Composite models** (dcmotor, embrace): broader tolerances are expected due to multi-FMU coupling and cross-component signal routing.

## Related

- [Test Strategy](../04-verification/co_simulation_test_strategy.md) — comparison policy, fixture classes, and acceptance philosophy
- [Architecture — Runtime Contract](../02-architecture/architecture.md#5-runtime-contract) — how comparison artifacts connect to simulation artifacts
- [Comparison Source Code](../../scripts/workflow/comparison.py) — source of truth for metric calculation

---

*Maintenance note: if the metric definitions or output format change in
`scripts/workflow/comparison.py` or `scripts/utils/comparison.py`, update
this document to match.*