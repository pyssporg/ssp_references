# IMP-CAND-I: Manifest Field Review

## Status

Proposed

## Layer

Implementation (03)

## Theme

Manifest schema audit — review setup.json and simulation.json fields

## Evidence

- `setup.json` is the per-case setup manifest
- `simulation.json` is the per-run manifest
- No documented schema for either file
- Need to verify all required fields are present and no redundant fields exist

## Current Pain Or Risk

Without a documented schema, new backends or simulation cases may produce incomplete manifests. Redundant fields add maintenance overhead without value.

## Proposed Improvement

Document the `setup.json` and `simulation.json` schemas. Review each field for necessity, completeness, and consistency. Remove any redundant fields and add any missing required fields.

## Expected Benefit

Documented manifest schemas. Clean, minimal field sets for both manifest types.

## Risk And Blast Radius

Low. Read-only review of the setup and simulation manifest producers. Minor edits to the schema if redundant fields are found.

## Suggested Priority

Low

## Task Contract Seed

Document the `setup.json` and `simulation.json` schemas with: (1) required fields, (2) optional fields, (3) types and formats, (4) examples. Review against current producer code for missing or redundant fields.

## Out Of Scope

Changing comparison manifests or the registry.

## Traceability

- Architecture: Runtime contract from `02-architecture/architecture.md`
- Implementation: `scripts/workflow/setup.py`, `scripts/workflow/registry.py`