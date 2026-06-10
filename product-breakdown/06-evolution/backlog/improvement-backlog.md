# Improvement Backlog Overview

## Usage

This overview indexes continuous-improvement candidates for the SSP fixture
parameter binding coverage gap identified in the IMP-041 gap analysis.

Each candidate is proposed. None is approved for implementation until it has
a scoped task contract.

## Individual Candidates

| File | ID | Theme | Status | Priority | Blast radius |
| --- | --- | --- | --- | --- | --- |
| `candidates/IMP-009.md` | IMP-009 | Fixture: flat inline SSV + external SSM | Proposed | Medium | Low |
| `candidates/IMP-010.md` | IMP-010 | Fixture: nested external SSV+SSM bindings | Proposed | Medium | Low |

## Summary

| ID | Theme | Priority | Prerequisite | Blast radius |
| --- | --- | --- | --- | --- |
| IMP-009 | Flat inline SSV + external SSM fixture | Medium | None | Low — new fixture directory, no existing file changes |
| IMP-010 | Nested external SSV+SSM bindings fixture | Medium | None | Low — new fixture directory, no existing file changes |

## Cross-Cutting Constraints

- New fixtures must follow the existing `signal_<descriptive_name>` naming
  convention.
- New fixtures must have a `FIXTURE.md` following the
  `product-breakdown/03-implementation/FIXTURE-template.md`.
- New fixtures must be registered in `artifacts/simulation_registry.json` and
  listed in `models/README.md`.
- The packaging coverage table in
  `product-breakdown/04-verification/co_simulation_fixture_mapping.md` should be
  updated to include the new fixtures and `signal_nested_parameter_bindings`.
- Do not modify existing fixtures, build scripts, or checked-in SSD files as
  part of this work.
