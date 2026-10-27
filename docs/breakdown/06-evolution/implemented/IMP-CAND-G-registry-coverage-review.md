# IMP-CAND-G: Simulation Registry Coverage Review

## Status

Completed

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

## Completed

Implemented via IMP-CAND-G builder task. The review document is at
`04-verification/simulation_registry_coverage_review.md`.

Actions taken:
- Added 3 missing models (dcmotor, pyfmu_csv_source_sink, scenario) to `simulation_registry.json`
- Added FMPy backend documentation to `models/README.md` (Backend Key + model tables)
- Added `## Backends` sections to all 15 FIXTURE.md files
- Created `04-verification/simulation_registry_coverage_review.md` with per-model rationale
- Updated `review-plan.md` item 1 status

## Out Of Scope

Changing pipeline code or backend adapters.

## Traceability

- Product: PD-003 (supported backends) — which backends should be in the registry
- Architecture: Runtime contract from `02-architecture/architecture.md` — registry is the source of truth
- Implementation: `scripts/workflow/registry.py` — registry loading logic