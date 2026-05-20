# IMP-CAND-G: Simulation Registry Coverage Review

## Status

Proposed

## Layer

Verification (04) / Implementation (03)

## Theme

Registry audit — determine which model/case/backend combinations should be kept

## Evidence

- `artifacts/simulation_registry.json` is the source of truth for case/backend selection
- No documented rationale exists for which models, cases, and backends are included vs excluded
- The review-plan item explicitly calls for confirming the combination set

## Current Pain Or Risk

Without a documented rationale for the registry contents, it's unclear whether a model/case/backend combination is intentionally present, accidentally present, or should be removed. This makes maintenance decisions (add/remove models, change backends) ad-hoc rather than principled.

## Proposed Improvement

Review all entries in `artifacts/simulation_registry.json` and produce a documented inventory of every model/case/backend combination with justification for inclusion or removal. Output a revised registry (or a confirmation that the current one is correct) plus a review document explaining the rationale.

## Expected Benefit

Clear documented rationale for every registry entry. Future maintainers can add/remove entries with reference to the review.

## Risk And Blast Radius

Low. Read-only review of the registry file. May result in a small number of registry edits (additions or removals). No pipeline code changes.

## Suggested Priority

Medium

## Task Contract Seed

Audit `artifacts/simulation_registry.json` and produce a review document listing each model/case/backend combination with: (1) reason for inclusion, (2) test level it serves, (3) whether it's actively maintained, (4) recommendation (keep/remove/add). If changes are needed, update the registry in the same pass.

## Out Of Scope

Changing pipeline code or backend adapters.

## Traceability

- Product: PD-003 (supported backends) — which backends should be in the registry
- Architecture: Runtime contract from `02-architecture/architecture.md` — registry is the source of truth
- Implementation: `scripts/workflow/registry.py` — registry loading logic