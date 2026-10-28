---
id: EVAL-010
type: eval
title: pyssp project verification plan
summary: Audit of the six vendored pyssp_* and sequence_extensions test suites, the level ladder each one is missing, and the phased plan that turns them into credible evidence.
date: 2026-10-28
status: current
pb_exempt: true
---

# pyssp project verification plan

## Scope

Six vendored projects, one test suite each. Snapshot 2026-10-28, Linux x86_64,
root `venv` (Python 3.11.14, pytest 9.1.1).

| Project | Path | Tests | Runtime |
|---|---|---|---|
| pyssp_standard (canonical) | `3rd_party/pyssp_workflow/3rd_party/pyssp_standard` | 413 | 5.5 s |
| pyssp_simulate | same tree | 112 (111 pass, 1 cosim skip) | 9.0 s |
| pyssp_sysml2 | same tree | 216 | 31 s |
| pyssp_workflow | `3rd_party/pyssp_workflow` | 62 (61 pass, 1 skip) | 2 s |
| pyssp_vv | same tree | 102 | 1.8 s |
| sequence_extensions | same tree | 401 (397 without e2e) | 10 s |

Excluded: root repo suite (`tests/`, 8 files — see EVAL-001, EVAL-008), the
pinned `pyssp_sysml2/3rd_party/pyssp_standard` copy (not editable), upstream CI
matrices not runnable here.

`pyssp_sysml2` worktree was under concurrent edit during the audit; its numbers
are a moving target and its `tests/variation_examples.py` copies text out of
`06-evolution/` without a drift check.

## Verdict

Static and unit levels are credible in all six. Component level is credible in
pyssp_vv and sequence_extensions, weak in pyssp_sysml2 and pyssp_workflow.
**Contract level is absent everywhere** — no shared suite runs a fake and its
real counterpart, and no producer/consumer pair is pinned. Integration level was
absent in pyssp_simulate until 2026-10-28 (28/112 tests errored at fixture
setup); acceptance exists only as byte hashes and wall-clock guesses.

Single highest-risk gap: **no cross-project contract coverage**. `pyssp_standard`
→ `pyssp_simulate` (SSD construction), `pyssp_vv` → `pyssp_workflow` (metric
schema), `pyssp_vv` measure → judge (`MetricView`), `pyssp_sysml2` → fixtures
(generated SSD). Each is a hand-written edge that has already rotted once.

## Credibility gates

| Project | Distinct levels | Real oracle | Boundary fidelity | Determinism | Traceability | Signal |
|---|---|---|---|---|---|---|
| pyssp_standard | static/unit/component/system/acceptance, no contract | strong (XSD + exact structure) | n/a (fakes hand-written) | good | weak (no fixture index) | good |
| pyssp_simulate | unit/component, integration restored | strong where live (analytic `y=t`, `t²/2`) | **fails** — fake OMSimulator headers wrong | medium (env-var FMU reuse, `chdir`) | weak (no markers) | medium |
| pyssp_sysml2 | static/unit/component, no contract/acceptance | strong inline, no goldens | n/a | **fails** — `now()` in model descriptions, writes into checkout | weak (no CI) | medium |
| pyssp_workflow | static/unit/component | weak at derive seam | **fails** — derive stub hides CLI contract | good | weak | medium |
| pyssp_vv | static/unit/component + 2 subprocess probes | improved 2026-10-28 | **fails** — `MetricRow` ≠ `MetricView` | good | weak | good |
| sequence_extensions | unit/component/integration/system | strong (invariants, no `Mock`) | n/a | medium — 25 timing-based tests | weak (no levels) | good |

## Evidence: mutation spot-check

25 hand-injected defects across the six suites, one copy under `/tmp/opencode`
each, real checkouts never mutated.

| Suite | Injected | Escaped before | Escaped now |
|---|---|---|---|
| pyssp_standard | 9 | 2 (`iter_components` order, `System.element` drop) | 0 |
| pyssp_vv | 6 | 3 (`reference_peak` sign, digest names, `rmse=mean`) | 0 |
| sequence_extensions | 8 | 1 (outcome drain) | 0 |
| pyssp_workflow | 6 | 3 (time_points, `--skip-fmu-validation`, bundle `out_dir`) | 3 |
| pyssp_simulate | 7 | 5 (root-boundary direction, container prefix, last CSV row, ssp4sim exit, cosim prefix) | 5 |
| pyssp_sysml2 | 7 | 1 ordering (1/216 kill), FMI version caught only incidentally | 1 narrow |

Re-verify by repeating the four closed cases before claiming them: each has one
new test that goes red under its defect (see P1/P2 rows).

## Gaps, ranked

| # | Gap | Category | Project | Risk | Fix | Cost |
|---|---|---|---|---|---|---|
| 1 | Engine-boundary tests all errored at fixture setup | Broken harness | pyssp_simulate | total loss of integration evidence | done: facade-based builder | S |
| 2 | `_build_one` passes `study` into `build_study(composition=...)`; test fake encodes the bug | Weak oracle + product bug | pyssp_workflow | wrong composition silently built; needs owner decision | fix call + assert real `composition` | S |
| 3 | `MetricRow` cannot be judged: no `reference_min/max` | Fake drift (seam) | pyssp_vv | reviewer table not judgeable | adapter or protocol decision | S |
| 4 | No contract suite between projects | Missing level | all | drift lands silently, as it already did | `tests/contract/` per pair | M |
| 5 | No level markers; level = directory name only | Untraceable | all six | failures do not localise; no gate budgets | register + auto-tag markers | M |
| 6 | Fake engine headers disagree with real engines | Fake drift | pyssp_simulate | fake passes where real OMSimulator shape differs | run one shared contract against both | M |
| 7 | No engine failure paths (non-zero exit, missing CSV, hung engine) | Missing level | pyssp_simulate | failures hang or pass | timeouts + error-path tests | M |
| 8 | No worker crash / timeout-kill evidence | Missing level | sequence_extensions | process pool failures unproven | kill-worker tests | M |
| 9 | Generated artifacts not byte-stable: `now()`, `uuid5` namespace, `build/fmu_pre` in checkout | Flaky + determinism | pyssp_sysml2 | rebuild diffs, dirty tree | inject clock, freeze guid, tmp output | S |
| 10 | Conversion outputs have no committed goldens; 39 substring asserts | Weak oracle | pyssp_sysml2 | algorithm change unreviewable | native goldens + XSD validator | M |
| 11 | Archive determinism opt-in; document names derive from filename | Determinism | pyssp_standard | rebuild differs by path | default epoch, test name independence | S |
| 12 | e2e ref self-captured, scratch tracked, compared with SUT's own `diff` | Weak oracle | sequence_extensions | goldens cannot fail honestly | independent validator + review gate | M |
| 13 | 25 timing/sleep-based concurrency tests | Flaky | sequence_extensions | CI noise, false green | event-driven rewrites; quarantine policy | M |
| 14 | Layering test blind to relative and dynamic imports | Weak oracle | pyssp_workflow, pyssp_vv | policy bypass | normalize relative imports; add `importlib` scan | S |
| 15 | No CI at all | Untraceable | pyssp_sysml2 | suite never gates a change | workflow with lint + pytest | S |
| 16 | Dead suites/scripts: `legacy_unsupported`, `test_utils.py`, `resources/test.sh`, `demo` marker selects 0 | Redundant | standard, sysml2 | false sense of coverage | delete or promote | S |
| 17 | Orphan public API (flatten, `LSRefExperiments.*`, `copy_resource_directory` errors, `build_legacy_fixture`, `list_ext.to_strings`) | Missing level | all | untested public surface | one test per export, lowest level | M |
| 18 | Goldens/fixtures have no provenance index | Untraceable | pyssp_standard, pyssp_sysml2 | `mixed_example.ssd` is self-referential and unlabelled | `tests/__fixture__/README.md` + checksums | S |

## Target structure

Ladder per project, adapted to an evidence product — not a conformance suite.

| Level | Lives in | Owns | Gate |
|---|---|---|---|
| static | `tests/test_layering.py`, `tools/` | imports, layering, policy greps | every commit, ≤5 s |
| unit | `tests/<subject>/` | branch logic, arithmetic, parsing | every commit |
| component | same tree, one module | module-internal collaboration | every commit |
| contract | `tests/contract/` per project + cross-project | producer/consumer, fake/real, schema/parser | every merge |
| integration | `tests/integration/` | real dependency semantics: zip fs, XSD, engines, process pool | nightly |
| system | `tests/system/` | console scripts, documented entry points | nightly |
| acceptance | `tests/acceptance/` | determinism, wall-clock budget, rebuild equality | release |

Rules that apply to all six:

- One marker per level; marker applied by directory in `conftest.py`, never by hand.
  `pytest -m level_contract` must select exactly the contract suite.
- Test names state the fault, not the method. A test with no nameable defect is deleted.
- Every fake gets one shared contract test against the real implementation, or it is deleted.
- Conversions keep native-format fixtures; expected output is a committed golden with an
  independent validator (XSD, `pyssp_standard` reader, hand-computed value) and a diffable
  regeneration protocol. No golden may be regenerated by the code it checks.
- Determinism policy: no wall clock in artifacts, no `sleep` as synchronisation, no
  host-dependent worker count in assertions, no writes into tracked paths, no reuse of
  ambient `PYTHONPATH`/editable installs in subprocess tests.
- Flake policy: a flaky test is quarantined with owner and date; retries never manufacture a pass.
- Runtime budgets: fast levels ≤60 s total; integration ≤5 min; acceptance ≤10 min.
  Enforced by `--durations` review and CI `timeout-minutes`, not by hope.

## Verification matrix (requirements × level)

`T` = covered, `p` = partial/weak oracle, `—` = absent. Rows are the requirements
this repo actually depends on, not every library function.

| Requirement | static | unit | component | contract | integration | system | acceptance |
|---|---|---|---|---|---|---|---|
| SSP/SSD/SSV/SSM XML round-trips | — | — | T | T | p | T | p |
| XSD conformance on write | — | — | T | — | T | T | — |
| Archive byte determinism | — | — | p | — | p | — | T |
| Tree protocol behaviour (`iter_*`, refs) | T | — | T | T | — | — | — |
| Model⇄codec field agreement | T | — | T | T | — | — | — |
| Engine produces expected trajectory | — | — | T | — | T | p | p |
| Backend result mapping / column contract | — | T | T | p | T | — | — |
| Cross-engine agreement on one SSP | — | — | — | p | T | — | p |
| Metric schema: measure → evidence → judge | — | T | T | p | — | — | — |
| Gate verdicts (pass/fail/invalid) | — | T | T | — | — | p | p |
| Flow ordering, retry, timeout, drain | — | T | T | — | T | p | p |
| CLI entry points return documented codes | — | — | p | — | — | p | — |
| Build → simulate → compare pipeline | — | — | — | — | p | p | — |

Orphan requirements today: backend error paths, process-worker crash, CLI error
codes, pipeline composition root. Orphan level: contract (cells are `p`/`—`).
Orphan tests: 3 in `test_hardening.py`, `test_schema_targets.py`, `test_utils.py`.

## Phases

| Phase | Work | Acceptance | Status |
|---|---|---|---|
| P0 | Unblock: pyssp_simulate fixture rebased on the public facade | 28 errors → 0, engine tests run | done 2026-10-28 |
| P1 | Contract layer: vv measure↔judge, standard tree/codec, cross-project metric schema, sysml2 generated-artifact pins | each contract test red under one injected defect | partial — vv + standard done |
| P2 | Oracles: settle drain, engine error paths, worker crash, archive negative cases | escaped-mutation list for these suites empty | partial — settle done |
| P3 | Determinism: sysml2 clock/guid/output dir, sequence e2e ref protocol, standard archive default, tmp cleanup | two clean rebuilds byte-identical; no tracked writes | planned |
| P4 | Goldens: sysml2 SSD/SSV/FMI goldens + XSD validator, fixture provenance index | golden diff reviewable; validator independent | planned |
| P5 | Gates: markers in all six, per-project CI (sysml2 has none), budgets, flake quarantine, cross-project contract job | `-m level_*` selects correct sets; CI red on a seeded defect | planned |

Order matters: P0 before any other measurement (unreliable harness invalidates
findings), P1 before P2 (contract fixes stop fakes from hiding defects), P3
before P4 (regenerating goldens on a nondeterministic build is churn).

## Product defects surfaced, not fixed

| Defect | Where | Consequence |
|---|---|---|
| `study` passed as `composition` | `3rd_party/pyssp_workflow/src/pyssp_workflow/authoring/build.py:110-116` | every build ignores its composition argument; the fake test asserts the bug |
| `MetricRow` not a `MetricView` | `pyssp_vv/evidence/*` vs `judge/criteria.py` | a metrics.csv row cannot be judged without translation |
| Unbound parameter set is silent | `pyssp_sysml2/parameters.py:~850` | declared set produces empty SSV with no warning |
| FMI version/date unpinned in outputs | `pyssp_sysml2/fmi.py:147-166` | rebuild diff; FMI3 impossible to add safely |
| Archive mode+mtime inherited | `pyssp_standard/common/archive.py:41` | byte drift across checkouts unless epoch passed |

Out of scope: fixing these here. They belong to their own repositories; this leaf
records them so a "green suite" is not mistaken for correctness.

## Non-goals

- SSP 1.0/2.0 conformance suite. Fixtures stay representative, not exhaustive.
- Production test infrastructure: no property-testing framework, no fault-injection
  framework, no custom mutation tooling in CI.
- Windows/macOS parity beyond what the engines already require.
- Rewriting upstream project suites to a single house style.

## Traceability

- EVAL-001 — engine test strategy and three fixture levels; unchanged.
- EVAL-002 — adoption assessment; its sequence_extensions limitation list becomes P2/P3 work.
- EVAL-005 — gate thresholds; the metric-schema contract row belongs here.
- EVAL-008 — UC matrix; this plan supplies the project-level evidence under it.
- EVAL-009 — artifact boundary; the contract level is what enforces it mechanically.
- Archive: `ADR-004` (UC lens), `DD-010` (`pyssp_vv` owns measurement and judgment),
  `PD-003` (backend needs adapter, install, and CI — pyssp_sysml2 fails the CI leg).
