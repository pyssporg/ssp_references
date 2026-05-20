# IMP-CAND-K: Backend and Case Expansion Assessment

## Status

Proposed

## Layer

Evolution (06)

## Theme

Scope assessment — determine if additional backends or model cases should be added

## Evidence

- Current backends: ssp4sim, OMSimulator, FMPy (PD-003)
- Current simulation registry has specific model/case combinations
- Open question: "Which additional registry entries should be added?"

## Current Pain Or Risk

Without an assessment, it's unclear whether the current backend and case set is sufficient or if gaps exist. Adding backends or cases ad-hoc risks scope creep.

## Proposed Improvement

Produce an assessment document evaluating: (1) gaps in the current backend coverage, (2) model/case combinations that should be added, (3) cost/benefit of adding FMPy as a third comparison backend, (4) prioritization for any additions.

## Expected Benefit

Clear understanding of what backends and cases should be added, deferred, or declined. Principled scope management.

## Risk And Blast Radius

Low. Research-only deliverable. No code or configuration changes.

## Suggested Priority

Low

## Task Contract Seed

Produce an assessment document evaluating: (1) missing fixture classes or model types in the registry, (2) whether FMPy should be added as a third comparison backend, (3) cost/benefit analysis for each proposed addition, (4) recommendations with dependencies.

## Out Of Scope

Adding backends or cases (implementation is separate).

## Traceability

- Product: PD-003 (supported backends) — which backends to support
- Architecture: Fixture hierarchy from `02-architecture/architecture.md` — which fixture classes need coverage