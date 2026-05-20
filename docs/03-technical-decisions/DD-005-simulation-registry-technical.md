# DD-005: Simulation Registry Technical Mechanism

**Status:** Accepted
**Layer:** technical-decision

---

## Context

The run matrix could be derived from directory scanning of built SSPs, from
`experiments.xml` content, or from an explicit registry file. The product-level
decision (PD-002) established that the registry is the source of truth; this
decision specifies the technical mechanism and schema.

## Decision

`artifacts/simulation_registry.json` is a JSON file listing every model with:
- The signals to compare during post-processing (`compare_signals`).
- One or more named cases, each listing the backends to run.

The registry is not derived from the SSP directory tree or from any
`experiments.xml`. It is hand-maintained and version-controlled alongside the
model definitions.

## Rationale

A machine-readable JSON schema makes the registry parseable by any pipeline
stage without custom parsing logic. Keeping the registry hand-maintained avoids
hidden defaults and makes the active test matrix explicit in version control.

## Consequences

- Adding a new model or case requires editing the registry JSON.
- Removing a case requires only a registry change (no rebuild needed as long as
  the SSP root already exists).
- The registry is the single point of configuration for the run matrix.

## Trace

Satisfies the runtime contract described in Section 5 of
[docs/02-system-architecture/architecture.md](../02-system-architecture/architecture.md) and
the product decision
[PD-002: Simulation Registry Is the Single Source of Truth](../01-product-decisions/PD-002-simulation-registry-source-of-truth.md).

## See Also

- [PD-002: Simulation Registry Is the Single Source of Truth](../01-product-decisions/PD-002-simulation-registry-source-of-truth.md)
  — the product-level commitment that this technical mechanism implements.
- [ADR-003: Runtime Configuration Belongs to the Simulation Registry](./ADR-003.md)
  — describes how the registry feeds into the `setup.json` contract.