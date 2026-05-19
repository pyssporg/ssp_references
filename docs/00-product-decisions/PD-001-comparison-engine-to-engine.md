# PD-001: Comparison Methodology — Engine-to-Engine Only

**Status:** Accepted
**Layer:** product-decision

---

## Context

The repository could compare simulation results against analytical expectations,
CSV baselines, or other engineered references. Early discussions considered
several comparison strategies.

## Options Considered

1. **Analytical truth comparison** — Each fixture would carry an analytical
   solution or reference CSV. Comparison would measure deviation from truth.
2. **Engine-to-engine comparison** — At least two distinct backend runs are
   required. Comparison measures pairwise deviation between backends.
3. **Hybrid** — Some fixtures use analytical truth, others use engine-to-engine.

## Decision

Comparison is always pairwise engine-to-engine. At least two distinct backend
runs are required. Baselines stored under `models/fmu/<model>/references/` are
used as fixture reference data, not as comparison targets in the pipeline.

## Rationale

Engine-to-engine comparison detects behavioral differences in the orchestration
layer without requiring analytical truth for every fixture. It keeps the
comparison pipeline symmetric and avoids maintaining engine-specific pass/fail
criteria for each model. Adding analytical truth would require per-fixture
mathematical analysis that is out of scope for a curated reference collection.

## Consequences

- A single-backend run cannot be compared.
- Adding a new backend requires at least one other backend run for the
  comparison to produce results.
- Absolute correctness checks against analytical solutions are out of scope.

## Trace

Satisfies the "Engine comparison results are the primary quality gate"
commitment in [docs/01-intent/intent.md](../01-intent/intent.md).

*This decision was migrated from the former design decisions log entry #2.*

## See Also

- [PD-003: Supported Simulation Backends](./PD-003-supported-backends.md)
  establishes the engine set that makes engine-to-engine comparison possible.