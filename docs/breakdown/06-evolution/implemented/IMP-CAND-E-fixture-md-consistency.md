# IMP-CAND-E: FIXTURE.md Consistency Audit

## Status

Proposed

## Layer

Implementation (03) — documentation quality

## Theme

FIXTURE.md section coverage consistency

## Evidence

- `03-implementation/FIXTURE-template.md` defines 10 sections with Required/Optional/Recommended tags
- 15 `models/ssp/*/FIXTURE.md` files vary from 4–8 sections
- Section title mismatches: "Main Failures This Catches" vs "Main Risks Covered"
- Simple reference models lack "Expected Behavior" and "Structure" sections

## Current Pain Or Risk

The FIXTURE.md template defines a canonical structure, but deployed files vary significantly in section count and title naming. This inconsistency undermines the template's value and makes cross-fixture comparison harder.

## Proposed Improvement

Audit all 15 FIXTURE.md files against the template. For each file: normalize section titles to match template, add missing Required sections, add missing Recommended sections where justified, add HTML comment placeholders for intentionally omitted Optional sections.

## Expected Benefit

All 15 FIXTURE.md files follow the same structure. Missing sections become intentional rather than accidental.

## Risk And Blast Radius

Medium. 15 files need individual review. Low risk of content loss since sections are normalized, not deleted. Blast radius limited to `models/ssp/*/FIXTURE.md` files.

## Suggested Priority

Medium

## Task Contract Seed

Audit all 15 FIXTURE.md files under `models/ssp/` against the template at `03-implementation/FIXTURE-template.md`. For each: normalize section titles to match template, add missing Required sections (Origin, Overview, Strategy Role), add missing Recommended sections (Expected Behavior for deterministic fixtures), add HTML comment placeholders for intentionally omitted Optional sections.

## Out Of Scope

Writing new content for any section. Modifying the FIXTURE.md template or build scripts.

## Traceability

- Intent: Repository provides curated, reproducible fixtures with documented provenance
- Architecture: Fixture class categorization must match `02-architecture/architecture.md` hierarchy
- Implementation: The template is the canonical reference