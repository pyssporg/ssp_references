# IMP-CAND-A: Full Migration

## Status

Proposed

## Layer

Evolution (06-evolution) — affects all layers

## Theme

Documentation structure migration — full adoption of product-breakdown template

## Evidence

- `docs/` uses a different 6-layer structure than the product-breakdown template's 7-layer structure
- Layer names diverge on 4 of 6 layers (01-product-decisions vs 01-product, 02-system-architecture vs 02-architecture, 03-technical-decisions vs 03-implementation, 04-implementation vs 04-verification)
- `05-operation` has no equivalent in the current structure
- `plans/backlog/` is disconnected from the product-breakdown tree
- Template files exist but are unused by the current documentation structure

## Current Pain Or Risk

1. The `orchestrator-planner`, `orchestrator-discovery`, and `orchestrator-improvement` agents all reference `product-breakdown/` as the entry point, but the actual documentation lives in `docs/`. This creates a reference mismatch — agents loading the product-breakdown layer guidance find different expectations than what exists.
2. No `05-operation` layer means operational concerns have no documented home (deployment, monitoring, support).
3. The backlog at `plans/backlog/` is outside the product-breakdown tree, creating confusion about where evolution/backlog content belongs.
4. The `others/adr-template.md` referenced from docs doesn't exist — this known stale reference is a symptom of the structure divergence.

## Proposed Improvement

1. Rename `docs/` → `product-breakdown/`
2. Re-index all six existing directories to match the template's layer names:
   - `00-intent/` → keep (already matches)
   - `01-product-decisions/` → `01-product/decisions/` (move decisions into a `decisions/` subdirectory)
   - `02-system-architecture/` → `02-architecture/`
   - `03-technical-decisions/` → relocate ADRs and DDs into appropriate `decisions/` subdirectories at each layer
   - `04-implementation/` → `03-implementation/`
   - `05-verification/` → `04-verification/`
3. Create new layers: `05-operation/` (start empty or with a stub README), `06-evolution/backlog/` (relocate `plans/backlog/` here)
4. Adopt all templates: create `decision-log.md`, `traceability-map.md`
5. Rewrite all cross-references in every document
6. Add `naming.md` at the product-breakdown root

## Expected Benefit

- Agent instructions match the actual documentation structure
- All 7 product-breakdown layers are populated
- Backlog lives within the evolution layer as the template expects
- Decision log and traceability map provide cross-layer visibility
- Consistent naming conventions across all artifacts

## Risk And Blast Radius

- **High blast radius** — every cross-reference in every document, plus any external links, must be updated
- Risk of stale references — any missed cross-reference update creates a broken link (KM-007 risk)
- Risk of content loss during re-organization — careful migration is needed
- Risk of tool incompatibility — any tooling that reads from `docs/` paths would break
- Requires a decision record — ADR or PD documenting the adoption of product-breakdown structure
- Effort: High — likely 2-3 full guarded-workflow passes

## Suggested Priority

Medium

## Task Contract Seed

Create a migration plan for renaming `docs/` to `product-breakdown/`, re-indexing all six layer directories to match the 7-layer product-breakdown template, relocating the backlog from `plans/backlog/` to `06-evolution/backlog/`, and adopting all product-breakdown templates (`decision-log.md`, `naming.md`, `traceability-map.md`). The plan must include a cross-reference audit and a rollback strategy.

## Out Of Scope

- Any implementation of the improvements themselves (this is a proposal, not implementation approval)
- Editing any existing files
- Creating ADRs or decision records for this migration

## Traceability

- Intent: Repository documentation structure needs alignment with workflow agent expectations
- Product: Product decisions currently stored in `docs/01-product-decisions/`
- Architecture: Current 6-layer `docs/` tree versus 7-layer product-breakdown template structure
- Implementation: FIXTURE templates, workflow documentation
- Verification: Test strategy and fixture mapping documents

## Notes

Full migration touches every document and cross-reference in the repo. Candidate B (Light Alignment) may be a safer intermediate step.