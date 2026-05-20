# IMP-CAND-B: Light Alignment

## Status

Proposed

## Layer

Evolution (06-evolution) — mainly affects backlog location

## Theme

Documentation alignment — minimal structural change, adopt templates at edges

## Evidence

- `orchestrator-improvement.md` specifies `plans/backlog/` as the working directory for backlog items
- The product-breakdown template specifies `06-evolution/backlog/` as the canonical location
- `docs/` structure has been stable through multiple IMP cycles and all cross-references work

## Current Pain Or Risk

1. The `orchestrator-improvement.md` agent instruction says "Use `plans/backlog/` as the working directory for tracking items" — but the backlog template says "Place the overview at... `product-breakdown/06-evolution/backlog/improvement-backlog.md`". This is a direct conflict in agent instructions.
2. New backlog items are being created without following the improvement-candidate-template format (Layer field, Out of scope, Traceability links are missing).
3. No `decision-log.md` or `traceability-map.md` exists, making it hard to find decisions or trace artifacts across layers.
4. The `others/adr-template.md` stale reference persists.

## Proposed Improvement

1. Relocate backlog: Create `docs/06-evolution/backlog/` as the canonical backlog location. Keep `plans/backlog/` as a symlink (or redirect) pointing to `docs/06-evolution/backlog/` to avoid breaking agent instructions that reference `plans/backlog/`.
2. Adopt templates for new backlog items: All future IMP candidates must use the improvement-candidate-template format with Layer, Out of scope, Traceability sections.
3. Reformat existing proposed IMPs (IMP-006/007/008) to match the candidate template (add Layer field, Out of scope section, Traceability links).
4. Add `decision-log.md` at `docs/decision-log.md` that indexes all PDs, ADRs, DDs, and future decisions with standardized table.
5. Add `traceability-map.md` at `docs/traceability-map.md` with the full trace chain.
6. Add `naming.md` at `docs/naming.md` documenting the naming conventions.
7. Create operation stub: Add `docs/05-operation/README.md` with a note that this layer is currently empty but available for operational documentation.
8. Fix the ADR template stale reference: Either create `.opencode/templates/others/adr-template.md` or update the docs to point to the product-breakdown `decision-template.md`.

## Expected Benefit

- Backlog lives in the canonical location within the docs tree
- All agent instructions remain valid (symlink preserves `plans/backlog/`)
- New candidates follow the template format consistently
- Decision log and traceability map improve cross-layer navigation
- Operation layer stub documents the gap intentionally
- No renaming or restructuring of existing docs needed
- No cross-reference rewrites needed

## Risk And Blast Radius

- Low blast radius — no existing content is moved or renamed
- Minimal risk — symlink can be safely removed once agent instructions are updated
- Risk of two backlog locations: If symlink is missed, agents could write to `plans/backlog/` while the canonical location is `docs/06-evolution/backlog/`. Mitigation: update `orchestrator-improvement.md` to reference the new location.
- Effort: Low-Medium — can be staged in 2-3 independent passes

## Suggested Priority

High

## Task Contract Seed

Relocate `plans/backlog/` content to `docs/06-evolution/backlog/`, create a symlink at `plans/backlog/` pointing to `docs/06-evolution/backlog/`, add `docs/decision-log.md`, `docs/traceability-map.md`, and `docs/naming.md` as root-level documentation artifacts, create `docs/05-operation/README.md` as a stub, and update `orchestrator-improvement.md` to reference the new backlog location.

## Out Of Scope

- Renaming `docs/` or any existing directories
- Rewriting cross-references in existing documents
- Modifying any existing IMP files beyond adding missing template fields
- Creating a `product-breakdown/` root directory

## Traceability

- Intent: Resolve agent instruction conflict between `plans/backlog/` and product-breakdown backlog location
- Product: Product decisions layer documentation
- Architecture: Current `docs/` tree structure
- Implementation: FIXTURE templates and workflow documentation
- Verification: Test strategy and fixture mapping

## Notes

This is the recommended approach. It achieves near-identical outcomes to Candidate A (Full Migration) at much lower cost and risk.