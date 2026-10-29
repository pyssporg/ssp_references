---
id: EVAL-010
type: eval
title: pyssp project verification plan
summary: Audit of the six vendored pyssp_* and sequence_extensions test suites, the level ladder each one was missing, and the restructuring that closed the contract, determinism, and failure-path gaps.
date: 2026-10-28
status: current
pb_exempt: true
---

# pyssp project verification plan

## Scope

Six vendored projects plus the root contract suite. Snapshot 2026-10-28, Linux
x86_64, root `venv` (Python 3.11.14, pytest 9.1.1).

| Project | Path | Tests | Runtime |
|---|---|---|---|
| pyssp_standard (canonical) | `3rd_party/pyssp_workflow/3rd_party/pyssp_standard` | 467 | 5.6 s |
| pyssp_simulate | same tree | 148 (147 pass, 1 cosim skip) | 10.0 s |
| pyssp_sysml2 | same tree | 248 | 32 s |
| pyssp_workflow | `3rd_party/pyssp_workflow` | 74 | 4.2 s |
| pyssp_vv | same tree | 122 | 2.2 s |
| sequence_extensions | same tree | 434 | 14.0 s |
| root suite | `tests/` | 104 (1 strict-mode skip) | 101 s |

Excluded: the pinned `pyssp_sysml2/3rd_party/pyssp_standard` copy (not
editable), the root suite's engine-free integration tests (see EVAL-001,
EVAL-008), upstream CI matrices.

## Verdict

Static, unit, and component levels are credible in all six. The **contract
level now exists** where it was absent: measure→judge, tree→codec,
evidence→verdict, sysml2→standard, nodes→flow. Integration is restored in
pyssp_simulate and now covers failure paths as well as happy paths. Acceptance
is still the weakest level: byte determinism is tested, runtime budgets are not.

Fixture layout, provenance, and the write guards are owned by EVAL-011.
Remaining highest-risk gap: **real-engine composition**. The seams pinned by the
root suite stop at the simulated boundary; no test loads a runtime SSP through a
real engine from the cross-project suite, and `cosim` has never executed.

## Credibility gates

| Project | Distinct levels | Real oracle | Boundary fidelity | Determinism | Traceability | Signal |
|---|---|---|---|---|---|---|
| pyssp_standard | static/unit/component/contract/system/acceptance | strong (XSD + exact structure + byte identity) | fakes hand-written, each now behaviour-pinned | good (epoch default, mode normalised) | levels + fixture provenance | good |
| pyssp_simulate | unit/component/contract/integration/system | strong (analytic `y=t`, `t²/2`, exact sample grid) | **fixed** — fakes use the recorded real header | good (FMU manifest, event-row decision pinned) | levels + engine set selectable | good |
| pyssp_sysml2 | static/unit/component/contract/system | strong (goldens + `pyssp_standard` validator + exact bytes) | n/a | **fixed** — injected clock, pinned guid/version, no checkout writes | levels, CI added | good |
| pyssp_workflow | static/unit/component/contract | strong at the derive argv and compare grid | derive stub now recorded, argv contract separate | good | levels | good |
| pyssp_vv | static/unit/component/contract | strong (hand-computed metrics, known-answer digest) | **fixed** — `as_metric_view` contract | good | levels | good |
| sequence_extensions | unit/component/integration/system | strong (invariants, independent e2e oracle) | n/a | medium — 12 tests quarantined as `flaky_timing` | levels + quarantine | good |

## Evidence: mutation spot-check

40+ hand-injected defects across the six suites and the root contracts, each in
a `/tmp/opencode` copy; real checkouts never mutated. All previously escaped
defects now go red, each at the level that owns the fault:

| Suite | Escaped before | Escaped now | Closing test |
|---|---|---|---|
| pyssp_standard | 2 | 0 | `test_tree_contract.py`, codec `element` roundtrip |
| pyssp_vv | 3 | 0 | rmse/peak/digest oracles, `as_metric_view` |
| sequence_extensions | 1 | 0 | `test_settle.py` |
| pyssp_workflow | 3 | 0 | argv contract, grid `time_points`, bundle `out_dir` |
| pyssp_simulate | 5 | 0 | error paths, real-header contract, exact grid |
| pyssp_sysml2 | 1 narrow | 0 | pinned FMI version/guid + byte-identical goldens |
| root seams | n/a | 0 | 3 of 4 seams shown red under injected drift |

## Target structure

| Level | Lives in | Owns | Gate |
|---|---|---|---|
| static | `test_layering.py`, `tools/` | imports, layering, policy greps | every commit, ≤5 s |
| unit | `tests/<subject>/` | branch logic, arithmetic, parsing | every commit |
| component | same tree, one module | module-internal collaboration | every commit |
| contract | `tests/*contract*`, root suite | producer/consumer, fake/real, schema/parser | every merge |
| integration | `tests/*backends*`, process tests | real dependency semantics: zip fs, XSD, engines, process pool | nightly |
| system | orchestration, CLI, e2e | composition root, documented entry points | nightly |
| acceptance | determinism, budgets | rebuild equality, wall-clock budget | release |

Rules now enforced by tests or CI:

- Exactly one level marker per test, checked by a `test_markers.py` invariant in
  every project; engine sets selectable with `-m level_integration`.
- Test names state the fault. A test with no nameable defect is deleted.
- Every fake has a shared behaviour contract with the real implementation.
- Conversions keep native fixtures; expected output is a committed golden with
  an independent validator and a diffable, reviewed regeneration path.
- No wall clock in artifacts, no `sleep` as synchronisation, no host-dependent
  worker count, no writes into tracked paths, no ambient install in subprocess
  tests.
- Flakes are quarantined with a marker, never retried into a pass.

## Verification matrix (requirements × level)

`T` = covered, `p` = partial, `—` = absent.

| Requirement | static | unit | component | contract | integration | system | acceptance |
|---|---|---|---|---|---|---|---|
| SSP/SSD/SSV/SSM XML round-trips | — | — | T | T | p | T | p |
| XSD conformance on write | — | — | T | — | T | T | — |
| Archive byte determinism | — | — | p | — | p | — | T |
| Tree protocol behaviour (`iter_*`, refs) | T | — | T | T | — | — | — |
| Model⇄codec field agreement | T | — | T | T | — | — | — |
| Engine produces expected trajectory | — | — | T | — | T | p | p |
| Backend result mapping / column contract | — | T | T | T | T | — | — |
| Cross-engine agreement on one SSP | — | — | — | p | T | — | p |
| Metric schema: measure → evidence → judge | — | T | T | T | — | — | — |
| Gate verdicts (pass/fail/invalid) | — | T | T | T | — | p | p |
| Flow ordering, retry, timeout, drain, crash | — | T | T | — | T | p | p |
| CLI entry points return documented codes | — | — | p | — | — | p | — |
| Build → simulate → compare pipeline | — | — | — | p | p | p | — |

Remaining orphan requirement: the real-engine composition root (row 13).
Remaining orphan level: acceptance budgets.

## What changed

| Phase | Work | Acceptance | Status |
|---|---|---|---|
| P0 | Rebase the simulate fixture on the public facade | 28 errors → 0, engine tests run | done |
| P1 | Contract layer: vv, standard, workflow, root seams, sysml2 goldens | each contract red under injected drift | done |
| P2 | Failure paths: settle, crash, cancellation, engine errors | escaped list empty for these suites | done |
| P3 | Determinism: archive, sysml2 clock, e2e scratch, FMU cache | two clean rebuilds identical, no tracked writes | done |
| P4 | Goldens: sysml2 artifacts + validators, fixture provenance | golden diff reviewable, validator independent | done |
| P5 | Gates: markers, quarantine, sysml2 CI | `-m level_*` selects correct sets | partial — root CI missing |

Detail:

- `pyssp_simulate` rebuilt its test SSP on the facade; the whole engine
  boundary came back (83→139 passing), the fake now uses the recorded real
  OMSimulator header, and eight injected defects are caught.
- `pyssp_standard` gained tree/codec contracts, archive and codec negative
  paths, fixture provenance, epoch-default packaging, and 457 tests.
- `pyssp_sysml2` gained an injectable clock, pinned FMI version and guid, a
  warning for unapplied parameter sets, committed goldens validated by
  `pyssp_standard`, exact-text generation oracles, and its first CI workflow.
- `sequence_extensions` gained settle/crash/cancellation coverage, an
  in-flight concurrency oracle, an independent e2e oracle, and no tracked
  scratch.
- `pyssp_workflow` fixed the composition argument it passed to `build_analysis`,
  and now checks relative and dynamic imports.

## Remaining gaps

| # | Gap | Category | Risk | Next |
|---|---|---|---|---|
| 1 | `cosim` never executed (binary absent) | Missing level | engine claims unverified | run in an image with the binary |
| 2 | Root repo has no CI | Untraceable | cross-project suite runs only locally | add a workflow that runs it plus `pb check` |
| 3 | Real engine seam outside `pyssp_simulate` | Missing level | wiring still unproven end to end | one nightly system test through `scripts/run_simulations.py` |
| 4 | `level_integration` empty in `pyssp_standard` | Misplaced | some component tests are integration | reclassify at the next touch |
| 5 | Relative dynamic imports not resolved | Weak oracle | `import_module(".x", "pkg")` bypasses layering | resolve the package argument |
| 6 | e2e fixed scratch is serial-only | Flaky | xdist unsupported | per-worker scratch root |
| 7 | Installed dist metadata says 0.1.1 | Untraceable | version confusion until reinstall | reinstall after the version change |
| 8 | Python 3.12/3.13 and pytest 8 unverified locally | Untraceable | CI-only claims | matrix run |
| 9 | Root suite runtime ~100 s, no budget test | Weak oracle | silent slowdown | add a duration gate |

## Verified claims and their checks

Adopted rule: a suite is credible only when a named defect makes it red. The
closing tests above were each observed red under their defect. Two clean runs
per suite, distinct `--basetemp`, `-p no:cacheprovider`, identical outcomes.

## Non-goals

- SSP 1.0/2.0 conformance suite; fixtures stay representative.
- Production test infrastructure: no property-testing or fault-injection
  framework, no custom mutation tooling in CI.
- Windows/macOS parity beyond engine requirements.
- A single house style across upstream project suites.

## Traceability

- EVAL-001 — engine strategy and fixture levels.
- EVAL-002 — adoption assessment; its sequence_extensions limitations are now
  pinned by tests instead of prose.
- EVAL-005 — gate thresholds; the metric-schema contract row lives here.
- EVAL-008 — UC matrix; this plan supplies the project-level evidence under it.
- EVAL-009 — artifact boundary; the contract level is what enforces it.
- Archive: `ADR-004` (UC lens), `DD-010` (`pyssp_vv` owns measurement and
  judgment), `PD-003` (backend needs adapter, install, CI).
