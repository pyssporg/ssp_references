# DD-006: Time-Shift-Tolerant VV Metrics

**Status:** Accepted
**Layer:** implementation-decision

---

## Context

Cross-engine comparisons resample every result onto the case's fixed time grid.
Co-simulation masters do not expose source and downstream values on the same
sample: a step can reach a gain one or two communication steps before the gain
output changes. Strict pointwise comparison then reports the full signal
amplitude as an error at every discontinuity, even when the engines implement
the same model.

The first gate run made this visible:

- `signal_step_gain`: `gain.y` pointwise error 6.0, but the transition was
  offset by two samples.
- `signal_step_add`: `add.y` pointwise error 1.5 at the first recorded sample.
- `signal_algebraic_loop`: a genuine 0.0126 iteration difference.

## Decision

Keep two metrics per signal:

- `max_abs_error` — strict pointwise error, for diagnosis.
- `max_shift_abs_error` — error after comparing each sample against candidate
  samples shifted by up to two communication steps in either direction.

The gate uses `max_shift_abs_error`. The first and last two samples are excluded
because they are initialization/shutdown artifacts in several engines. Signal
invariants use the same idea: each input may independently be one step behind,
and the first recorded sample is not judged.

## Consequences

- Real model differences remain visible; scheduling skew does not dominate.
- A genuine timing difference smaller than two communication steps is treated
  as equivalent. The accumulated error is still reported.
- Metrics CSV schema changes from `max_abs_error`-only to the two-column form.
  Existing manifests without the new field load with `0.0` for the gate metric.
- Thresholds stay registry data; this decision only changes how the error is
  measured.
