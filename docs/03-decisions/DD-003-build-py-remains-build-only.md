# DD-003: `build.py` Remains Build-Only

**Status:** Accepted
**Layer:** technical-decision

---

## Context

A model's `build.py` could optionally run a smoke simulation after building to
validate the SSP immediately.

## Decision

`build.py` is strictly build-only. It transforms an authored model definition
into a built SSP root. It does not invoke any simulation backend, write runtime
configs, or register cases.

## Rationale

Keeps the build stage fast and isolated. Simulation failures do not block the
build pipeline. Each stage can be invoked independently for debugging or
incremental work.

## Consequences

- Validation of a built SSP requires a separate simulation step.
- There is no "build and smoke test" shortcut at the model level.
- Build scripts remain simple and simulation-backend-independent.

## Trace

Satisfies the stage-boundary invariants described in Section 3 of
[docs/02-architecture/architecture.md](../02-architecture/architecture.md)
(entry point ownership and forbidden shortcuts).

## See Also

- [ADR-001: Three-Stage Pipeline Architecture](./ADR-001.md) — the pipeline
  structure that this boundary enforces.