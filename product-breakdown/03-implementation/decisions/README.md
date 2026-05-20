# Design Decisions

This directory holds Design Decision (DD) records for the `ssp_references`
repository. DDs document smaller implementation choices: the context that
prompted them, the alternatives considered, and the consequences of the
chosen approach.

## When to Create a DD

Create a DD when a decision affects:

- The internal design of a script, adapter, or workflow module.
- Variable naming, file layout, or convenience conventions within a single
  pipeline stage.
- One-off fix approaches or workarounds with long-term implications.
- Any implementation choice that future contributors might need to understand
  or revisit.

Larger architectural choices (pipeline boundaries, fixture hierarchy, runtime
contracts) belong in the
[Architecture Decision Record (ADR) directory](../../02-architecture/decisions/README.md).

## DD Lifecycle

1. **Proposed** — The DD is drafted for discussion.
2. **Accepted** — The decision is adopted and the DD becomes a stable reference.
3. **Superseded** — A later DD or ADR replaced this decision.
4. **Rejected** — The proposal was evaluated and not adopted.

## Template

There is no canonical DD template. Follow the general decision format in
[`.opencode/templates/product-breakdown/templates/decision-template.md`](../../../../.opencode/templates/product-breakdown/templates/decision-template.md).

## Index

### Design Decisions (DDs)

| DD | Title | Status | Layer |
|----|-------|--------|-------|
| [DD-001](./DD-001-simulation-settings-runtime-layer.md) | Simulation Settings Belong to the Runtime Layer | Accepted | technical-decision |
| [DD-002](./DD-002-runtime-artifacts-under-artifacts.md) | Runtime Artifacts Stay Under `artifacts/` | Accepted | technical-decision |
| [DD-003](./DD-003-build-py-remains-build-only.md) | `build.py` Remains Build-Only | Accepted | technical-decision |
| [DD-004](./DD-004-signal-propagation-deterministic-blocks.md) | Signal-Propagation Fixtures Use Deterministic Algebraic FMU Blocks | Accepted | technical-decision |
| [DD-005](./DD-005-simulation-registry-technical.md) | Simulation Registry Technical Mechanism | Accepted | technical-decision |

## Purpose

DDs occupy the **implementation-decision** layer of the documentation stack.
They are downstream of architecture decisions (ADRs) and describe specific
design choices made during implementation. Every DD traces to one or more ADRs
that define the architectural boundary within which the implementation choice
was made.

## Backward Trace

The DDs in this directory implement the architectural constraints defined by:

- [ADR-001](../../02-architecture/decisions/ADR-001.md) — Three-Stage Pipeline
- [ADR-002](../../02-architecture/decisions/ADR-002.md) — Fixture Hierarchy
- [ADR-003](../../02-architecture/decisions/ADR-003.md) — Runtime Configuration

---

*This file was created in Phase 1 of IMP-CAND-A from the former
`docs/03-technical-decisions/README.md`.*
