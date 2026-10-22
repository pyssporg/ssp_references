# PD-002: Simulation Registry Is the Single Source of Truth

**Status:** Accepted
**Layer:** product-decision

---

## Context

The run matrix could be derived from directory scanning of built SSPs, from
`experiments.xml` content, or from a registry file.

## Options Considered

1. **Directory scanning** — Walk `artifacts/models/` to discover built SSPs and
   derive the run matrix from directory structure.
2. **`experiments.xml` parsing** — Read each built SSP's `experiments.xml` to
   determine simulation cases and backends.
3. **Explicit registry file** — A single JSON file lists every model/case/backend
   combination explicitly.

## Decision

`artifacts/simulation_registry.json` is the exclusive source of truth for which
model/case/backend combinations are active.

## Rationale

A single explicit registry avoids hidden defaults, makes the active test matrix
visible without running any code, and allows selective enablement/disablement of
cases without modifying model sources or build scripts.

## Consequences

- Adding a new model or case requires a registry update.
- Removing a case requires only a registry change (no rebuild needed as long as
  the SSP root already exists).
- The registry is the single place where the full run matrix is visible.

## Trace

Satisfies the "build, simulate, and compare workflow is driven by shared entry
points" commitment in [00-intent/intent.md](../../00-intent/intent.md).

*This decision was migrated from the former design decisions log entry #6.*

## See Also

- [DD-005: Simulation Registry Technical Mechanism](../../03-implementation/decisions/DD-005-simulation-registry-technical.md)
  describes the JSON schema and implementation details.
- [ADR-003: Runtime Configuration Belongs to the Simulation Registry](../../02-architecture/decisions/ADR-003.md)
  describes how the registry feeds into `setup.json`.

## Amendment (2026-10-22): Build and Study Are Separate Registry Fields

The registry remains the exclusive source of truth for the active run matrix.
The model/study split adds two explicit fields:

- `build` selects the exported model SSP under
  `artifacts/models/<model>/<build>/`;
- a case's `study` selects the study artifacts under
  `artifacts/studies/<model>/<study>/`.

A case is no longer assumed to be the same name as the built SSP directory.
`build` defaults to `model` and `study` defaults to the case name for transition
compatibility. See
[DD-009](../../03-implementation/decisions/DD-009-runtime-scenario-injection.md).