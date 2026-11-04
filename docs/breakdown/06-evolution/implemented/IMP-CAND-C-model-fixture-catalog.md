# IMP-CAND-C: Model Fixture Catalog

## Status

Proposed

## Layer

Implementation (03) — user/consumer discoverability

## Theme

Model catalog for fixture discoverability

## Evidence

- `models/ssp/` contains 15 entries with no aggregated listing
- `models/fmu/` contains 12 entries
- Architecture doc describes fixture hierarchy class names but no full model list
- Test strategy references models by name but no cross-reference table exists

## Current Pain Or Risk

No single document lists all available SSP fixtures with their fixture class, simulation purpose, backend compatibility, and expected behavior. A user must scan `models/ssp/` and open each FIXTURE.md individually.

## Proposed Improvement

Create a catalog document at `models/README.md` (or `03-implementation/fixture-catalog.md`) that lists all 15 SSP fixtures as a table with columns: Model Name, Fixture Class, Purpose, Expected Behavior Summary, Backend Support, Test Level, FIXTURE.md Link. Include a similar table for the 12 FMU building blocks.

## Expected Benefit

A visitor can understand the full fixture collection in one page. Test strategy authors can reference the catalog. New fixture authors can see what gaps exist.

## Risk And Blast Radius

Low. A single new documentation file. Risk of the catalog falling out of sync — mitigated by a maintenance note.

## Suggested Priority

High

## Task Contract Seed

Create a new file at `models/README.md` tabling all 15 SSP models with: Name, Fixture Class (per architecture.md hierarchy), One-line Purpose, Expected Behavior Summary, Backend Support, Test Level, Link to FIXTURE.md. Also table the 12 FMU building blocks. Add a maintenance note.

## Out Of Scope

Modifying existing FIXTURE.md files. Changing the model directory structure.

## Traceability

- Intent: Repository provides curated, reproducible fixture collection — catalog makes curation visible
- Architecture: Fixture class column references the 4-class hierarchy from `02-architecture/architecture.md`
- Implementation: Catalog lives beside the models it documents
- Verification: Test level references the 3-level hierarchy from test strategy