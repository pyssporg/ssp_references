---
id: EVAL-011
type: eval
title: Test suite restructuring and fixture credibility
summary: Critical audit of the six vendored pyssp_* and sequence_extensions suites plus the root contract suite, focused on the file-fixture layer, and the restructuring that makes every fixture traceable, layout-checked, and write-protected.
date: 2026-10-28
status: current
---

# Test suite restructuring and fixture credibility

Supersedes the fixture section of EVAL-010. EVAL-010 remains the level-ladder
and mutation record; this leaf owns the fixture layer and the suite hygiene
gates. EVAL-012 records what was built, the red evidence, and the gaps.

## Scope

Six vendored suites plus the root suite. Before the change: 457 tests in
`pyssp_standard`, 140 in `pyssp_simulate`, 241 in `pyssp_sysml2`, 71 in
`pyssp_workflow`, 119 in `pyssp_vv`, 428 in `sequence_extensions`, 87 in the
root suite. Counts after are in EVAL-012. Excluded: the pinned `pyssp_sysml2/3rd_party/pyssp_standard`, vendored
`3rdParty/` suites, engine installation.

## Verdict

Every suite is green and every level is present. The fixture layer was not
credible, for five reasons:

1. `pyssp_standard` kept 6.4 MB of fixtures in one flat `__fixture__` dump whose
   only provenance was one README table.
2. The pinned copy duplicates 5.8 MB of the same fixtures, and its
   `mixed_example.ssd` is a **serialized variant**, not a copy: `prefix="Plant."`
   against `prefix="Plant"`, `ns0:` element prefixes. Undetected.
3. No suite failed when a test wrote into its own committed fixtures. Two suites
   have a regeneration path (`UPDATE_GOLDENS`, `UPDATE_REF`) with no in-code
   refusal under CI.
4. `pyssp_standard` derived the level marker from directory-name substrings, so
   moving one file silently reclassified its level.
5. The root suite had no level markers, no marker invariant, and twelve
   `pytest.skip` guards on missing `artifacts/**`; a checkout without build
   output was green and proved nothing.

## Fixture policy (adopted)

One convention, all suites. Level stays a marker; the path names the case.

```
tests/fixtures/<subject>/<case>/
├── input.<ext>      # native format, committed, minimal
├── expected.<ext>   # committed golden, only for conversions
└── case.md          # provenance, oracle, comparison, update policy
```

- Paths resolve from `Path(__file__)`, never the process cwd.
- A fixture the code under test generates is a **golden**, not an input; it is
  committed, diffable, and paired with an independent validator.
- A generated archive (`.ssp`, `.fmu`) is built into `tmp_path` from a committed
  directory tree; binaries are not committed when the tree reproduces them.
- `case.md` is the unit of provenance; a directory README is an index only.
- A document of 15+ lines is a fixture file; the fragment that makes the case
  stays in the test. A suite with no data files commits none, and its policy
  test enforces that tests write to `tmp_path`, not the checkout.
- Update is explicit (`UPDATE_GOLDENS=1`, `UPDATE_REF=1`), refused when `CI` is
  set, and reviewed as a diff.

## Gates added

| Gate | Fault it catches | Form |
|---|---|---|
| Fixture layout check | untraceable fixture, cwd-relative load, oversize fixture | static test per suite |
| Inline-document gate | a SysML document re-embedded in a test | AST check: 15+ newlines must be a fixture |
| Fixture write guard | a test mutating committed fixtures | session hash compare in `conftest.py` |
| Level table invariant | silent level reclassification | static test; explicit file→level table |
| Committed-golden validation | golden blessed but never validated | validator run on committed bytes |
| Update refusal | regeneration inside CI | code guard on `CI` |
| Artifact corpus gate | missing build reported as pass | `SSP_REQUIRE_ARTIFACTS=1` strict run |
| Fixture-twin drift | pinned copy diverging silently | documented allowlist, red on new drift |

## Target layout

| Suite | Before | After |
|---|---|---|
| pyssp_standard | `tests/__fixture__/{embrace,mixed_example.ssd,…}` | `tests/fixtures/<case>/` with `case.md`; `support/fixtures.py` accessors |
| pyssp_sysml2 | `tests/golden/<case>/` | same paths, plus `case.md` and committed-byte validation |
| sequence_extensions | `tests/e2e/{cases,ref}` + fixed `out/` | `case.md` per flow; one case set for the inputs; per-worker scratch |
| pyssp_simulate | `tests/fixtures/omsimulator_result.csv` | `fixtures/omsimulator-recording/input.csv` + `case.md` |
| pyssp_workflow, pyssp_vv | inline literals only | values unchanged; `tests/README.md` states the policy |
| root | no markers, no policy test | explicit level table, marker invariant, corpus gate, twin-drift test |

## Non-goals

- Converting every short literal. A placeholder that makes a parser fail is a
  unit-test input, not a fixture.
- Property-based testing, mutation tooling in CI, or a custom fixture database.
- Rewriting upstream suites to one house style beyond the fixture layer.
- Replacing the real `embrace` example with a smaller synthetic one; its size is
  the point of the archive tests.
