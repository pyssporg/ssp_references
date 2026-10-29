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
