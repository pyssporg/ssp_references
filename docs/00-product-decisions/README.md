# Product Decisions

This directory holds product-level decisions for the `ssp_references` repository,
one file per decision. Each file follows the ADR template structure (Context,
Options Considered, Decision, Rationale, Consequences, Trace) at the
product-decision scope.

This layer sits between [docs/01-intent/intent.md](../01-intent/intent.md)
(Intent and Product Commitments) and
[docs/02-architecture/architecture.md](../02-architecture/architecture.md)
(System Architecture) in the documentation chain.

## Decision Sequence

Product decisions are ordered by dependency — earlier decisions constrain later
ones:

```
PD-003: Supported Backends
  └─ establishes which engines we commit to
      │
      ▼
PD-001: Engine-to-Engine Comparison
  └─ how we compare results between those engines
      │
      ▼
PD-002: Registry as Source of Truth
  └─ how we configure which cases run on them
```

## Index

| ID | Title | Status | File |
|----|-------|--------|------|
| PD-003 | Supported Simulation Backends | Accepted | [PD-003-supported-backends.md](./PD-003-supported-backends.md) |
| PD-001 | Comparison Methodology — Engine-to-Engine Only | Accepted | [PD-001-comparison-engine-to-engine.md](./PD-001-comparison-engine-to-engine.md) |
| PD-002 | Simulation Registry Is the Single Source of Truth | Accepted | [PD-002-simulation-registry-source-of-truth.md](./PD-002-simulation-registry-source-of-truth.md) |

## Forward Trace

These product decisions translate the commitments in
[docs/01-intent/intent.md](../01-intent/intent.md) into durable promises. The
stable boundaries that preserve them are defined in the
[System Architecture](../02-architecture/architecture.md) and refined by the
[Technical Decisions](../03-decisions/README.md) (ADRs and DDs).