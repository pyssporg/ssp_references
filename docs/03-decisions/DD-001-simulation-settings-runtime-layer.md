# DD-001: Simulation Settings Belong to the Runtime Layer

**Status:** Accepted
**Layer:** technical-decision

---

## Context

Early discussions considered using `experiments.xml` (from the LS-REF
convention) as the runtime configuration source for simulation dispatch.

## Decision

The simulation window is read from `experiments.xml` at setup time and frozen
into `setup.json`. The runtime layer (`run_simulations.py` and backend adapters)
reads from `setup.json`, not from `experiments.xml` directly.

## Rationale

Decouples the build pipeline (which produces SSPs with LS-REF metadata) from
the simulation pipeline (which needs a stable, flat configuration file). Keeps
`experiments.xml` as packaging metadata without making it the runtime contract.
Avoids re-parsing XML on every simulation dispatch.

## Consequences

- `setup.json` must be regenerated if the experiment window or tolerance changes.
- The `experiments.xml` file must still be present and valid in each built SSP
  root because it is the source of truth at setup time.

## Trace

Satisfies the runtime contract described in Section 5 of
[docs/02-architecture/architecture.md](../02-architecture/architecture.md).

## See Also

- [ADR-003: Runtime Configuration Belongs to the Simulation Registry](./ADR-003.md)
  — this ADR establishes the registry as the configuration source; DD-001
  specifies that the runtime layer consumes the frozen `setup.json` rather than
  `experiments.xml`.