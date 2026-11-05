# Root test suite

The root suite is the repository's cross-project gate. It proves two things the
per-project suites cannot: that the hand-written seams between the vendored
projects still agree, and that the committed corpus the pipeline reads is
present and parseable. It does not certify engines and it does not judge
comparison trajectories — that is the build/simulate/compare workflow's job.

## Layout rule

Path names the subject, the marker names the level. A file owns one level, so
its tests share one marker; a single test that reads a different kind of
subject declares `@pytest.mark.level_*` itself and that marker wins.

| Level | Marker | What it selects | Command |
| --- | --- | --- | --- |
| static | `level_static` | source, marker and policy checks, no execution | `pytest -m level_static` |
| unit | `level_unit` | one function or object in isolation | `pytest -m level_unit` |
| component | `level_component` | one workflow module with collaborators faked | `pytest -m level_component` |
| contract | `level_contract` | seams between vendored projects, both sides real | `pytest -m level_contract` |
| integration | `level_integration` | committed fixtures plus generated outputs | `pytest -m level_integration` |
| system | `level_system` | build -> simulate -> compare end to end | `pytest -m level_system` |
| acceptance | `level_acceptance` | results judged against trusted baselines | `pytest -m level_acceptance` |

`tests/conftest.py` holds `LEVEL_BY_FILE` and applies the file default during
collection. `tests/test_markers.py` keeps the table total: every collected file
must appear, no entry may be stale, and every test must carry exactly one level
marker.

## Corpus gate and strict mode

`tests/test_artifact_corpus.py` always checks the tracked corpus:
`artifacts/simulation_registry.json` parses, the first case names an analysis, and
every reference CSV named by the registry or by a model's `build.py` exists and
parses. It asserts nothing about generated output in normal mode.

Set `SSP_REQUIRE_ARTIFACTS=1` (or `CI`) to also demand the generated corpus for
every registry case: `artifacts/models/<model>/<analysis>/model/SystemStructure.ssd`,
`artifacts/analyses/<model>/<analysis>/analysis.json`, and
`artifacts/simulation/<model>/<analysis>/setup.json`. A missing build fails with
the missing paths and the command that regenerates them:

```bash
python3 scripts/build_models.py run <model>
python3 scripts/run_simulations.py
```

## SysML standard gate

`tests/test_sysml_standard.py` proves the authored fixtures are portable beyond
this repository's own dialect parser. It loads each fixture's
`architecture/*.sysml` files in one `sysmlpy.load_files` call and runs
`sysmlpy.analyze(..., library=[PysspCore, ScalarValues])`. `sysmlpy` 0.96.4
generates its grammar from the OMG SysML v2 2026-05 specification, so a fixture
that parses and resolves there is valid SysML v2, not merely valid input to
`pycps_sysml2`. The gate asserts zero analyzer errors and reports every
unexpected finding as `fixture`, `file:line`, `code`, and `message`.

The gate is deterministic and needs no network. Two deviations from a plain
analyzer run are deliberate:

- **Allowlist.** Known dialect idioms — selection by feature value and nested
  variant chains in the `variation_*` fixtures — are listed by fixture and code
  with an exact expected count. A new code, a new fixture, or an extra
  occurrence fails the gate instead of being absorbed. The list and its
  justifications live in the test module and in
  `docs/breakdown/04-verification/sysml-standard-parser-gate.md`.
- **Cross-root include.** `models/ssp/GainOffset` reaches `Generator` through
  the FMU root. The gate mirrors `build_fixture(includes=...)` and adds
  `models/fmu/GainOffset/architecture` as a second `load_files` input, which
  removes the `UNDEFINED_SYMBOL` finding. Analyzing the SSP root alone still
  reports it, and that isolated analysis is asserted in the test.

`sysmlpy` resolves library symbols globally, so a missing `private import
PysspCore::*;` does not produce an analyzer error. The gate therefore also
checks that each fixture using a `PysspCore` or `ScalarValues` symbol declares
the matching import. A deleted import fails that check even though the analyzer
stays silent. Every analyze call in the module passes `library=`; a call
without it caches an empty index for the rest of the process.

## Adding a test

1. Choose the level first; put the test in the file whose subject matches.
2. If it is a new file, add its path (relative to `tests/`) to `LEVEL_BY_FILE`
   in `tests/conftest.py`. Never add a bare `pytestmark` level to a file; the
   table is the single mapping.
3. If one test genuinely belongs to another level, decorate it explicitly:
   `@pytest.mark.level_integration`.
4. Skip only when the missing thing is an engine or an artifact, and put the
   remedy in the message (`run build_models.py`, `scripts/run_simulations.py`,
   `pip install ...`). `tests/test_suite_policy.py` enforces this.
5. Write only under `tmp_path`; the policy test fails a write that resolves to
   `REPO_ROOT`, `__file__`, or a repo-relative path literal.

## Transitional tests

`test_legacy_sysml_shims.py` is a contract test for the `pyssp_sysml2` v0.4.0
re-export shims. It is deleted when the shims are removed in v0.5.0.

`test_fmu_artifacts.py` is the contract test for the SysML-authored `GainOffset`
FMU: `modelDescription.xml` and the generated C headers (build outputs under
`artifacts/build/GainOffset/`, carried for consumers by the committed
`Generator.fmu` archive), the compiled binary, and the packaged archive must
agree on one variable set. It also pins the architecture boundary by ownership:
`models/fmu/GainOffset/architecture/GainOffset.sysml` is the canonical home of
the FMU definitions, `models/ssp/GainOffset/architecture/` holds only
`System.sysml`, and the SSP build reaches the FMU definitions through
`build_fixture(includes=...)` on that canonical directory — never a copy or a
link. The exported identity (`modelName="Generator"`, its derived GUID, and
`MODEL_NAME` in the C source) must match the built `modelDescription.xml`.
Redeclaring a `pycps_sysml2` core definition is caught by
`test_dialect_core.py`. The public FMI 2.0 headers come from
`pyfmi_sysml2.fmi2_headers()`.
