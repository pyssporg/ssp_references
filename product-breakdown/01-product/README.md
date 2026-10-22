# Product Decisions

This directory holds product-level decisions for the `ssp_references` repository,
one file per decision. Each file follows the ADR template structure (Context,
Options Considered, Decision, Rationale, Consequences, Trace) at the
product-decision scope.

This layer sits between [00-intent/intent.md](../00-intent/intent.md)
(Intent and Product Commitments) and
[System Architecture](../02-architecture/architecture.md)
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
      │
      ▼
PD-004: SysML SspModel Authoring
  └─ model definitions and parameter sets are authored in SysML
      │
      ▼
PD-005: Fixtures and Policy, Not Pipeline Code
  └─ generic build/run/compare/verify behavior belongs to pyssp_workflow
      │
      ▼
PD-006: Studies Consume Exported SSPs
  └─ studies supply scenarios and experiments; they are never SSPs
```

## Index

| ID | Title | Status | File |
|----|-------|--------|------|
| PD-003 | Supported Simulation Backends | Accepted | [PD-003-supported-backends.md](./decisions/PD-003-supported-backends.md) |
| PD-001 | Comparison Methodology — Engine-to-Engine Only | Accepted | [PD-001-comparison-engine-to-engine.md](./decisions/PD-001-comparison-engine-to-engine.md) |
| PD-002 | Simulation Registry Is the Single Source of Truth | Accepted | [PD-002-simulation-registry-source-of-truth.md](./decisions/PD-002-simulation-registry-source-of-truth.md) |
| PD-004 | SysML `SspModel` Definitions and Parameter Sets Are the Authoring Source | Accepted | [PD-004-sysml-sspmodel-authoring.md](./decisions/PD-004-sysml-sspmodel-authoring.md) |
| PD-005 | The Reference Repository Owns Fixtures and Policy Data, Not Pipeline Implementations | Accepted | [PD-005-fixtures-and-policy-not-pipeline.md](./decisions/PD-005-fixtures-and-policy-not-pipeline.md) |
| PD-006 | Studies Consume Exported SSPs and Are Never Exported | Accepted | [PD-006-studies-consume-exported-ssps.md](./decisions/PD-006-studies-consume-exported-ssps.md) |

## Forward Trace

These product decisions translate the commitments in
[00-intent/intent.md](../00-intent/intent.md) into durable promises. The
stable boundaries that preserve them are defined in the
[System Architecture](../02-architecture/architecture.md) and refined by the
[Technical Decisions](../02-architecture/decisions/README.md) (ADRs and DDs).