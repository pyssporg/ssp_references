---
id: EVAL-012
type: eval
title: Fixture layer implementation record
summary: What the fixture restructuring built in each suite, the counts after the change, the defect injected to prove each gate red, and the gaps that remain.
date: 2026-10-28
status: current
---

# Fixture layer implementation record

Implementation of the fixtures and gates specified in EVAL-011. The two layout
gates from EVAL-013 are included in these totals. Two clean runs
per suite with distinct `--basetemp` and `-p no:cacheprovider` produced
identical outcomes.

## Implemented

| Gate | Suite | Test |
|---|---|---|
| fixture layout, case record, size budget, cwd-free paths | pyssp_standard | `tests/test_fixture_policy.py` (6) |
| explicit level table | pyssp_standard | `tests/test_level_table.py` (3) |
| fixture write guard | pyssp_standard, pyssp_sysml2, sequence_extensions, pyssp_simulate, pyssp_workflow, pyssp_vv | `support/fixture_guard.py` + session hooks |
| committed-golden validation | pyssp_sysml2 | `test_golden_artifacts.py::test_golden_artifacts_are_reproducible_and_valid` |
| update refusal in CI | pyssp_sysml2, sequence_extensions | code guard in the regeneration path |
| golden provenance | pyssp_sysml2 (2 cases), sequence_extensions (2 flows + case set), pyssp_simulate (1 case) | `case.md` |
| level markers and invariant | root | `pytest.ini`, `tests/conftest.py:LEVEL_BY_FILE`, `tests/test_markers.py` (5) |
| artifact corpus gate | root | `tests/test_artifact_corpus.py` (3) |
| skip-remedy and write policy | root, pyssp_workflow, pyssp_vv, pyssp_simulate | `test_suite_policy.py` / `test_fixture_policy.py` |
| fixture-twin drift | root | `tests/test_fixture_twins.py` (7) |
| inline-document extraction | pyssp_sysml2 | `tests/fixtures/<subject>/` (108 files) + AST gate |

### SysML documents moved out of test modules

`pyssp_sysml2` embedded 2,234 lines of SysML, FMI XML, and SSV XML in test
modules, including 17 expected artifacts compared as `dedent(...)` literals. The
documents now live in `tests/fixtures/<subject>/` — 15 subject directories, 108
data files, 2,280 lines — loaded through `tests/fixture_files.py`
(`fixture_text`, `render_fixture`, `assert_matches_fixture`). Templates keep
`$slot` placeholders; the slot values stay in the test, which is what makes each
case different. Expected artifacts are compared with a unified diff, not a
string equality failure.

The extraction removed `tests/variation_examples.py` (444 lines) and collapsed
four byte-identical duplicates. `tests/test_fixture_policy.py` gained the gate
that keeps it: a string literal of 15+ newlines in a test module is a red test,
unless an allowlisted reason says why it stays.

Restructuring: `pyssp_standard/tests/__fixture__` became `tests/fixtures/<case>/`
with a `case.md` per case and `support/fixtures.py` accessors; the vacuous
`binaries/` assertion now runs against a generated FMU that has a binary.
`pyssp_simulate` recording became `fixtures/omsimulator-recording/input.csv`
with a case record. `sequence_extensions` scratch is now per worker
(`tests/e2e/out/<worker>`) with a stable repo-relative alias so the golden log
bytes did not change.

Counts after the change, two clean runs, identical:

| Suite | Before | After |
|---|---|---|
| root | 87 (+12 artifact skips possible) | 104, 1 skipped |
| pyssp_workflow | 71 | 74 |
| pyssp_standard | 457 | 473 |
| pyssp_simulate | 140 | 148 (147 pass, 1 cosim skip) |
| pyssp_sysml2 | 241 | 258 |
| pyssp_vv | 119 | 122 |
| sequence_extensions | 428 | 434 |

## Red evidence

Each gate was observed failing under its own defect, then reverted.

| Gate | Injected defect | Observed |
|---|---|---|
| case record | delete `payload-plain-text/case.md` | `fixture cases without case.md: ['payload-plain-text']` |
| write guard | append a byte to a fixture from a probe test | test passed, session exit 1, path listed |
| level table | remove one file from `FILE_LEVELS` | `test files missing from FILE_LEVELS: [...]` |
| golden validation | change `version="1.0"` to `"9.0"` in a committed golden | byte mismatch, and the committed copy rejected by XSD |
| CI refusal | `CI=1 UPDATE_GOLDENS=1` | `Failed: refusing to update goldens in CI`, no write |
| artifact corpus | `CI=1` with `artifacts/studies/VanDerPol/baseline` renamed | missing path plus the `build_models.py` remedy |
| twin drift | append a byte to a canonical twin; rename the SSD model | byte test red; semantic test red |

## Remaining gaps

| # | Gap | Category | Next |
|---|---|---|---|
| 1 | `cosim` still never executed | Missing level | run in an image with the binary |
| 2 | Root repo still has no CI workflow | Untraceable | workflow running `pytest`, `SSP_REQUIRE_ARTIFACTS=1`, and `pb check` |
| 3 | `level_integration` still empty in `pyssp_standard` | Misplaced | the archive suites are integration, not acceptance |
| 4 | Root suite ~100 s with no budget test | Weak oracle | one duration gate at acceptance level |
| 5 | `pyssp_simulate` inline SSD/FMI literals (24 sites) | Untraceable | convert only those reused as a boundary contract; the rest are unit inputs by design |
| 6 | Twin drift allowlist is hand-maintained | Weak oracle | fails red when the pinned copy catches up; revisit at the next submodule bump |

## Acceptance

- Every suite green twice from a clean `--basetemp`.
- Each new gate observed red under its own defect, then reverted.
- `pb check --strict` and `pb node-size --strict` pass.
