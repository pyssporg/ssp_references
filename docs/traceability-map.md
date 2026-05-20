# Traceability Map

This document records the cross-layer trace chain for the `ssp_references`
repository. Per KM-005, traceability connects intent, product behavior,
architecture, implementation, verification, operation, and evolution.

## Trace Chain

```
Intent (00)
  └─► Product Decisions (01)
        └─► System Architecture (02)
              └─► Technical Decisions (03) [ADRs + DDs]
                    └─► Implementation (04)
                          └─► Verification (05-verification/)
                                └─► Operation (05-operation/) [stub - empty]
                                      └─► Evolution (06) [backlog]
```

## Layer Directories

| Layer | Directory | Contents |
| --- | --- | --- |
| Intent | [00-intent/](./00-intent/) | `intent.md` — repository purpose, commitments, non-goals |
| Product Decisions | [01-product-decisions/](./01-product-decisions/) | PD-001 (comparison methodology), PD-002 (registry source of truth), PD-003 (supported backends) |
| System Architecture | [02-system-architecture/](./02-system-architecture/) | `architecture.md` — stable boundaries, pipeline stages, fixture hierarchy, runtime contract |
| Technical Decisions | [03-technical-decisions/](./03-technical-decisions/) | ADR-001 through ADR-003 (architecture scope), DD-001 through DD-005 (implementation scope) |
| Implementation | [04-implementation/](./04-implementation/) | `FIXTURE-template.md`, `ls_ref_ssp_experiment_workflow.md` |
| Verification | [05-verification/](./05-verification/) | Test strategy, fixture mapping |
| Operation | [05-operation/](./05-operation/) | **Currently empty** — stub README only |
| Evolution | [06-evolution/](./06-evolution/) | Backlog artifacts (IMP-CAND candidates, completed IMP items, review plan) |

**Note on numbering:** Both `05-verification/` and `05-operation/` share the
`05` prefix. This pre-existing numbering is documented here for clarity and is
not being changed in this task.

## Cross-Layer Decision Index

| Decision Type | Prefix | Layer Directory | Purpose |
| --- | --- | --- | --- |
| Intent | INT | `00-intent/` | Repository purpose and scope |
| Product Decision | PD | `01-product-decisions/` | Durable product promises |
| Architecture Decision Record | ADR | `03-technical-decisions/` | Significant architectural rationale |
| Design Decision | DD | `03-technical-decisions/` | Smaller implementation choices |
| Improvement Candidate | IMP | `06-evolution/backlog/` | Deferred or scheduled work |

## Trace Rules (per KM-005)

1. **Backward-only:** Every artifact traces upward to intent, product commit-
   ments, or architectural constraints. No artifact links downward to
   implementation details or verification specifics.
2. **Explicit trace sections:** Every ADR and PD includes a `Trace` section at
   the bottom linking to the artifact it satisfies.
3. **Evolution items trace backward:** Improvement candidates identify the layer
   where the pain or gap was detected. They do not prescribe implementation.
4. **Decision log is index-only:** The root `decision-log.md` lists decisions
   without duplicating their rationale.

## Maintenance

When adding, renaming, superseding, or deprecating a decision or layer
artifact, update this map and the root decision log in the same change. Keep
entries short — full detail belongs in the artifact itself.