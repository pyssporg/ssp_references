# Architecture Decision Records

This directory holds Architecture Decision Records (ADRs) for the
`ssp_references` repository. ADRs document significant architectural choices:
the context that prompted them, the alternatives considered, and the
consequences of the chosen approach.

## When to Create an ADR

Create an ADR when a decision affects:

- The three-stage pipeline (Build → Simulate → Compare) or its interface
  contracts.
- The fixture hierarchy or the relationship between fixture classes.
- The runtime contract (`simulation_registry.json` → `setup.json` → artifacts).
- Entry point boundaries or the responsibilities of shared workflow modules.
- Backend adapter contracts or backend selection mechanisms.
- Repository layout, directory conventions, or documentation structure.

Smaller implementation choices (variable naming, one-off fix approaches,
internal function design) do not need an ADR. Use the design decisions (DD)
files in `../../03-implementation/decisions/` for those.

Product-level decisions (comparison methodology, backend commitment, registry
as source of truth) belong in the
[Product Decisions](../../01-product/README.md) directory, not
in this directory.

## ADR Lifecycle

1. **Proposed** — The ADR is drafted for discussion.
2. **Accepted** — The decision is adopted and the ADR becomes a stable reference.
3. **Superseded** — A later ADR replaced this decision.
4. **Rejected** — The proposal was evaluated and not adopted.

## Template

The canonical template is at
[`.opencode/templates/others/adr-template.md`](../../../../.opencode/templates/others/adr-template.md).

## Index

### Architecture Decision Records (ADRs)

| ADR | Title | Status | Layer |
|-----|-------|--------|-------|
| [ADR-001](./ADR-001.md) | Three-Stage Pipeline Architecture | Accepted | architecture-decision |
| [ADR-002](./ADR-002.md) | Fixture Hierarchy | Accepted | architecture-decision |
| [ADR-003](./ADR-003.md) | Runtime Configuration Belongs to the Simulation Registry | Accepted | technical-decision |
| [ADR-004](./ADR-004.md) | Use-Case Coverage Taxonomy as the Primary Coverage Lens | Accepted | technical-decision |
| [ADR-005](./ADR-005.md) | Adopt the pyssp Ecosystem Behind Existing Stage Boundaries | Accepted | architecture-decision |
| [ADR-006](./ADR-006.md) | Exchange Standardized Artifacts at Tool Boundaries | Accepted | architecture-decision |
| [ADR-007](./ADR-007.md) | Authoring SysML at the Build Boundary | Accepted | architecture-decision |
| [ADR-008](./ADR-008.md) | Workflow Capability Ownership and Node Boundaries | Accepted | architecture-decision |
| [ADR-009](./ADR-009.md) | `SspModel` and `Study` Marker Specialization | Accepted | architecture-decision |
| [ADR-010](./ADR-010.md) | Runtime Scenario and Experiment Application to Exported SSPs | Accepted | architecture-decision |

## Layer Map

Per KM-005's documentation-layer separation, ADRs in this directory occupy the following
layers:

- **architecture-decision** — Records the rationale behind a system-structure
  choice that is already described as a stable boundary in
  [architecture.md](../architecture.md).
  These ADRs explain *why* the architecture is the way it is.
- **technical-decision** — Bridges architecture to build details. These ADRs
  explain *how to implement* within the architecture's stable boundaries.

Product-level decisions (what the repository promises to do) are recorded in
[Product Decisions](../../01-product/README.md),
not in this directory.

> Implementation-level decisions (DDs) are in
> `../../03-implementation/decisions/README.md`.

## Decision Sequence

Technical decisions follow the architecture they implement. The sequence below
shows the dependency order — earlier decisions constrain later ones:

Architecture Decisions:
  ADR-001: Three-Stage Pipeline
    └─ establishes Build → Simulate → Compare with file-based contracts
        │
        ▼
  ADR-002: Fixture Hierarchy
    └─ establishes four-class fixture organization
        │
        ▼
Technical Decisions (bridging architecture to build details):
  ADR-003: Runtime Config → Registry
    └─ configuration flows through simulation_registry.json → setup.json
        │
        ├──► DD-001: Settings → Runtime Layer
        │     └─ runtime reads setup.json, not experiments.xml
        │
        ├──► DD-002: Artifacts Under artifacts/
        │     └─ simulation/comparison outputs are separate from build
        │
        ├──► DD-003: build.py Is Build-Only
        │     └─ stage boundary enforcement
        │
        ├──► DD-004: Deterministic FMU Blocks
        │     └─ fixture design for signal-propagation tests
        │
        └──► DD-005: Registry Technical Mechanism
              └─ JSON schema and maintenance convention
        │
        └──► ADR-004: Use-Case Coverage Taxonomy
              └─ coverage analysis defines what the pipeline should validate

  ADR-005: pyssp Ecosystem Adoption
    └─ pyssp_simulate substrate, VV gate, campaign, SysML round-trip
        │
        ▼
  ADR-006: Artifact Tool Boundaries
    └─ external tools exchange SSP files; no cross-library model shims
        │
        ▼
  ADR-007: SysML Authoring at the Build Boundary
    └─ pyssp_workflow invokes the pyssp CLI; no pyssp_sysml2 import
        │
        ▼
  ADR-008: Workflow Capability Ownership
    └─ generic build/run/measure/judge/report behavior moves to pyssp_workflow
        │
        ▼
  ADR-009: SspModel/Study Markers
    └─ models are exportable; studies are never SSPs
        │
        ▼
  ADR-010: Runtime Scenario Injection
    └─ studies apply SSV/SSM and experiment data to an exported SSP

## Maintenance Note

ADR-001 (pipeline), ADR-002 (fixture hierarchy), and ADR-004 (coverage taxonomy) describe system-structure
choices that are also documented in
[architecture.md](../architecture.md).
When either ADR or the architecture doc is updated, verify both documents stay
consistent. The architecture doc describes *what* the architecture is; the ADRs
describe *why* those choices were made.

## Backward Trace

These ADRs satisfy the System Architecture described in
[architecture.md](../architecture.md) and the product commitments in
[README.md](../../00-intent/intent.md).

---

*This file was created in Phase 1 of IMP-CAND-A from the former
`docs/03-technical-decisions/README.md`.*
