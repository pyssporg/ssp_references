# DD-002: Runtime Artifacts Stay Under `artifacts/`

**Status:** Accepted
**Layer:** technical-decision

---

## Context

Simulation results could be stored next to each model's exported SSP under
`artifacts/models/<model>/<build>/`.

## Decision

Runtime artifacts live in `artifacts/simulation/<model>/<study>/` and
`artifacts/comparisons/<model>/<study>/`, completely separate from exported
model artifacts under `artifacts/models/` and study data under
`artifacts/studies/`.

## Rationale

Keeps build output immutable once produced. Simulation and comparison runs can
be cleaned or re-run without affecting the built SSPs. Prevents accidental
coupling between build logic and runtime configuration.

## Consequences

- Four parallel directory trees under `artifacts/` (models, studies,
  simulation, comparisons).
- Cleanup must target each tree independently.
- Pipeline stages can be independently cleaned and re-run without rebuild.

## Trace

Satisfies the pipeline stage isolation described in Section 1 of
[02-architecture/architecture.md](../../02-architecture/architecture.md).

## See Also

- [ADR-001: Three-Stage Pipeline Architecture](../../02-architecture/decisions/ADR-001.md) — the pipeline
  structure that this artifact layout supports.