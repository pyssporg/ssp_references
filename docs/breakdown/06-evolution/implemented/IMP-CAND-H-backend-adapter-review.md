# IMP-CAND-H: Backend Adapter Review

## Status

Completed — moved to `backlog/complete/IMP-CAND-H-backend-adapter-review.md`.

## Layer

Implementation (03)

## Theme

Backend adapter audit — verify ssp4sim and OMSimulator adapters match config and CSV contracts

## Evidence

- Two backend adapters: ssp4sim and OMSimulator
- Config shape and result CSV contract need verification against current adapters
- No documented contract for what adapters must produce/consume

## Current Pain Or Risk

If the adapters have drifted from each other or from the expected config/CSV contract, comparison results may be unreliable. Without a documented contract, adapter behavior cannot be verified independently.

## Proposed Improvement

Review both backend adapters against a documented config shape and result CSV contract. Produce a document specifying: (1) required config.json fields, (2) required result.csv columns and naming, (3) adapter-specific differences, (4) any gaps or bugs found.

## Expected Benefit

Both adapters have a documented contract they must satisfy. Comparison becomes more reliable because both backends produce comparable output.

## Risk And Blast Radius

Low. Read-only review. May result in adapter patches if discrepancies are found.

## Suggested Priority

Medium

## Task Contract Seed

Review `scripts/workflow/ssp4sim_adapter.py` and `scripts/workflow/omsimulator_adapter.py` against the config shape produced by `setup.json` and the result CSV format consumed by comparison. Document the expected config fields, CSV columns, adapter-specific behaviors, and any discrepancies found.

## Out Of Scope

Changing the comparison pipeline or registry.

## Traceability

- Architecture: Pipeline stage contracts from `02-architecture/architecture.md`
- Implementation: Adapter source code