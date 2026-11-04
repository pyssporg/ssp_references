---
id: INFO-008
type: info
title: Build, analysis, and runtime workflow
summary: Build produces the analysis and model SSP; an explicit packaging step applies the scenario. Simulation runs the built SSP as-is.
date: 2026-10-23
status: current
---

# Build, analysis, and runtime workflow

- **Authoring**: `pyssp_workflow.authoring.derive_ssp_from_sysml` and `derive_analysis_from_sysml` invoke the `pyssp` CLI; no `pyssp_sysml2` import.
- **Layout**: a runnable SSP lives at `artifacts/models/<model>/<analysis>/<build>/`; analysis artifacts at `artifacts/analyses/<model>/<analysis>/`.
- **Model build**: `build.py` is a thin runner. `pyssp_workflow.authoring.build_fixture` derives one model SSP per analysis from `architecture/*.sysml` and returns their records; `report_builds` prints them. `build_legacy_fixture` copies a checked-in SSP body instead. Neither packages the scenario.
- **Analysis build**: `pyssp generate analysis` writes the scenario SSV, the SSM, and `analysis.json` under `artifacts/analyses/<model>/<analysis>/`; a model may build several analyses.
- **Analysis descriptor**: `analysis.json` records model, composition, sut name, target SSD, the authored `Analysis` description, the experiment window (start, stop, step), and scenario paths. It carries no tolerance.
- **Scenario packaging**: a separate explicit step after `build_fixture`; the fixture passes the returned `fixture.BuiltFixture` and the scenario SSV to `pyssp_workflow.binding.bind(build, ssv, *, mode=..., ssm=..., mapping=..., components=...)`. `mode` is `external` (default) or `inline`; `mapping` is `attach` (default) or `flatten`; `ssm` is optional; `components` is valid only for inline flatten and writes per-component sets. `set_name` overrides the SSV's name. `bind` mutates through `pyssp_standard`, returns a `BindingResult`, and never rewrites the scenario SSV or SSM.
- **Tolerance**: the analysis descriptor carries no solver tolerance. Composition names one only where an engine requires it: ssp4sim rejects a request without `simulation.tolerance`, so `scripts/workflow/simulate.py` supplies `BACKEND_REQUIRED_TOLERANCE` and the value is recorded in `simulation.json`. OMSimulator and FMPy apply their own defaults. Gate tolerances are not part of the experiment.
- **Runtime**: `run_simulations.py` runs the built SSP as-is. No scenario injection. `pyssp_simulate.simulate` executes it with the backend named by the registry — there is no automatic engine fallback; the library default `omsimulator` is used only when no backend is named. The spec carries `fixed_step=False`, `validate_ssd=False`, and the `omsimulator_options` tuple.
- **Canonicalization**: strip all runtime container names from result signals; `fmu.h` canonicalizes to `h`.
- **Result layout**: every engine writes the same CSV shape through one writer; `time` comes first, then signal names sorted, so a column present in two engines' results has the same name and the same relative position. Column sets may differ (for example OMSimulator parameter columns).
- **Comparison**: `pyssp_workflow.compare.compare_csvs` composes one pair and writes `metrics.csv`; `pyssp_vv.measure` aligns and measures; `pyssp_vv.evidence` owns the metric-row and summary schema; `pyssp_vv.judge` produces `pass`, `fail`, or `invalid`.
- **Gate policy**: tolerances, `SHIFT_TOLERANCE_SAMPLES`, and the verdict mapping live in `workflow/gate.py`.
- **Figures**: `pyssp_vv.measure.build_figure_spec` describes a figure; `render_figure` draws it and imports matplotlib inside the function.
- **Local code**: artifact layout, registry, gate, model policy, reference CSVs, and fixture bodies stay in this repository. Generic engine, packaging, comparison, figure, and authoring code lives in the pyssp packages (`DD-013`).
- **Model policy**: signal invariants live in `workflow/model_policy.py`; registry data carries tolerances and reference applicability.
- **Experiment packaging**: the build writes no `experiments.xml`; the analysis descriptor is the only experiment source.
- **Campaign**: one build node per model is submitted once and reused by all cases of that model; one prepare node per case runs `run_simulations.py --prepare-only` and writes `setup.json`; per-backend simulation nodes run without rewriting it, then compare through `sequence_extensions` nodes.
- **Registry**: a case names its `analysis` and `build`; the registry resolves `artifacts/models/<model>/<analysis>/<build>/`.
- **Capability ownership**: `pyssp_workflow` composes `pyssp_standard`, `pyssp_simulate`, `pyssp_vv`, and `pyssp_sysml2`.

## Owns
- Concrete build, analysis, and runtime mechanism.

## Excludes
- Product promise: `CP-001`.
- Stage boundary: `INFO-002`.
- Verification: `EVAL-001`.
