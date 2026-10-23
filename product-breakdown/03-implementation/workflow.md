---
id: INFO-008
type: info
title: Build, study, and runtime workflow
summary: Build packages the study scenario into a runnable SSP; simulate runs the built SSP as-is.
date: 2026-10-23
status: current
---

# Build, study, and runtime workflow

- **Authoring**: `pyssp_workflow.authoring.derive_ssp_from_sysml` and `derive_study_from_sysml` invoke the `pyssp` CLI; no `pyssp_sysml2` import.
- **Layout**: a runnable SSP lives at `artifacts/models/<model>/<study>/<build>/`; study artifacts at `artifacts/studies/<model>/<study>/`.
- **Model build**: `build.py` is a thin runner. `pyssp_workflow.authoring.run_fixture` derives the model SSP from `architecture/*.sysml` and unpacks it into the build directory. `run_legacy_fixture` copies a checked-in SSP body instead.
- **Study build**: `pyssp generate study` writes the scenario SSV, the SSM, and `study.json` under `artifacts/studies/<model>/<study>/`; a model may build several studies.
- **Study descriptor**: `study.json` records model, composition, sut name, target SSD, the authored `Study` description, the experiment window (start, stop, step), and scenario paths. It carries no tolerance.
- **Scenario packaging**: each fixture passes one `pyssp_workflow.execute` form. Default is `package_scenario`: it copies the study SSV/SSM into the SSP and adds one root `ParameterBinding`. Other forms are `package_nothing`, `package_inline_root`, `package_external_target_named`, and `package_inline_with_mapping`; `apply_inline_components` covers per-component inline sets. Every form mutates through `pyssp_standard` and never rewrites the scenario SSV or SSM.
- **Tolerance**: the setup manifest carries no solver tolerance; each engine applies its own default. The gate tolerances are not part of the experiment.
- **Runtime**: `run_simulations.py` runs the built SSP as-is. No scenario injection. `pyssp_simulate.simulate` executes it; the spec carries `fixed_step=False`, `validate_ssd=False`, and the `omsimulator_options` tuple.
- **Canonicalization**: strip all runtime container names from result signals; `fmu.h` canonicalizes to `h`.
- **Comparison**: `pyssp_workflow.execute.compare_result_csvs` composes one pair and writes `metrics.csv`; `pyssp_vv.measure` aligns and measures; `pyssp_vv.evidence` owns the metric-row and summary schema; `pyssp_vv.judge` produces `pass`, `fail`, or `invalid`.
- **Gate policy**: tolerances, `SHIFT_TOLERANCE_SAMPLES`, and the verdict mapping live in `workflow/gate.py`.
- **Figures**: `pyssp_vv.measure.build_figure_spec` describes a figure; `render_figure` draws it and imports matplotlib inside the function.
- **Local code**: artifact layout, registry, gate, model policy, reference CSVs, and fixture bodies stay in this repository. Generic engine, packaging, comparison, figure, and authoring code lives in the pyssp packages (`DD-013`).
- **Model policy**: signal invariants live in `workflow/model_policy.py`; registry data carries tolerances and reference applicability.
- **Experiment packaging**: the build writes no `experiments.xml`; the study descriptor is the only experiment source.
- **Campaign**: build model, simulate, and compare run as `sequence_extensions` nodes.
- **Registry**: a case names its `study` and `build`; the registry resolves `artifacts/models/<model>/<study>/<build>/`.
- **Capability ownership**: `pyssp_workflow` composes `pyssp_standard`, `pyssp_simulate`, `pyssp_vv`, and `pyssp_sysml2`.

## Owns
- Concrete build, study, and runtime mechanism.

## Excludes
- Product promise: `CP-001`.
- Stage boundary: `INFO-002`.
- Verification: `EVAL-001`.
