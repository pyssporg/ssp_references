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
internal function design) do not need an ADR. Use the design decisions log in
[design-decisions-log.md](./design-decisions-log.md) for those.

## ADR Lifecycle

1. **Proposed** — The ADR is drafted for discussion.
2. **Accepted** — The decision is adopted and the ADR becomes a stable reference.
3. **Superseded** — A later ADR replaced this decision.
4. **Rejected** — The proposal was evaluated and not adopted.

## Template

The canonical template is at
[`.opencode/templates/others/adr-template.md`](../../.opencode/templates/others/adr-template.md).

## Index

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-001](./ADR-001.md) | Three-Stage Pipeline Architecture | Accepted |
| [ADR-002](./ADR-002.md) | Fixture Hierarchy | Accepted |
| [ADR-003](./ADR-003.md) | Runtime Configuration Belongs to the Simulation Registry | Accepted |

## Backward Trace

These ADRs satisfy the System Architecture described in
[docs/architecture.md](../02-architecture/architecture.md) and the product commitments in
[docs/intent.md](../01-intent/intent.md).