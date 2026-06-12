# Improvement Backlog Overview

## Usage

This overview indexes continuous-improvement candidates for SSP parameter binding
permutations, signal propagation testing, usecase coverage, and test infrastructure
gaps identified in the IMP-041 gap analysis and the IMP-011 use-case coverage analysis.

Each candidate is proposed. None is approved for implementation until it has
a scoped task contract.

## Individual Candidates

| File | ID | Theme | Status | Priority | Blast radius |
| --- | --- | --- | --- | --- | --- |
| `complete/IMP-011.md` | IMP-011 | System simulation use-case coverage analysis and gap tracking | Completed | High | Low |
| `candidates/IMP-012.md` | IMP-012 | Parameter binding pipeline tests (pipeline-context only) | Proposed | High | Low |
| `candidates/IMP-013.md` | IMP-013 | End-to-end pipeline integration test | Proposed | High | Medium |
| `candidates/IMP-014.md` | IMP-014 | Gate pass/fail enforcement in comparison pipeline | Proposed | High | Medium |
| `candidates/IMP-015.md` | IMP-015 | Backend adapter integration tests | Proposed | Medium | Low |
| `candidates/IMP-016.md` | IMP-016 | Update fixture mapping for signal_nested_parameter_bindings | Proposed | Low | Low |
| `candidates/IMP-017.md` | IMP-017 | Signal propagation pipeline coverage tests | Proposed | High | Low |

## Summary

| ID | Theme | Priority | Prerequisite | Blast radius |
| --- | --- | --- | --- | --- |
| IMP-011 | Use-case coverage taxonomy, gap analysis framework, engine-test flagging | Completed | None — artifact only | Low — documentary artifact, no code changes |
| IMP-012 | Parameter binding pipeline tests (pipeline-context only) | High | IMP-011 (taxonomy context) | Low — new test functions only |
| IMP-013 | End-to-end pipeline integration test | High | None — requires simulated SSP artifacts | Medium — creates integration test infrastructure |
| IMP-014 | Gate pass/fail enforcement | High | Existing metrics gate review (IMP-CAND-J) | Medium — changes to comparison pipeline |
| IMP-015 | Backend adapter integration tests | Medium | Existing backend adapters | Low — new test functions |
| IMP-016 | Fixture mapping documentation for signal_nested_parameter_bindings | Low | None | Low — documentation only |
| IMP-017 | Signal propagation pipeline coverage tests (structural/registry/parseability, not algebra) | High | IMP-011 (taxonomy), existing fixtures | Low — new test functions only |

## Cross-Cutting Constraints

- New tests must follow the existing pytest conventions in `tests/`.
- New test functions must use `tmp_path` fixtures for isolation where applicable.
- Tests that invoke backend adapters must not require installed simulation engines
  unless explicitly guarded with `pytest.mark.skipif` or similar.
- **New tests must validate system simulation use-case coverage, not low-level
  programmatic function behavior.** Algebraic relationship checks (e.g.,
  verifying `add.y = step_a.y + step_b.y`) belong in the simulation engine
  repositories, not in this repo's test suite.
- **Engine-level verification tests must be flagged for transfer.** The two
  identified tests (`test_reference_csvs_are_not_inverted`,
  `test_modelica_block_fmus_expose_dependency_metadata`) should be moved to
  engine repos.
- No modifications to existing fixture `build.py` scripts or `SystemStructure.ssd`
  checked-in files as part of test-only additions.

## Use-Case Coverage Matrix

The use-case coverage matrix (UC-1 through UC-16) is maintained in the
[System Simulation Use-Case Coverage Analysis](../use_case_coverage_analysis.md)
document. That document is the canonical reference for coverage status, gap
assessments, and prioritization. This section is replaced by a cross-reference
to avoid duplication.
