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
- **Model build**: `build.py` derives the model SSP from `architecture/*.sysml` and unpacks it into the build directory.
- **Study build**: `pyssp generate study` writes the scenario SSV, the SSM, and `study.json` under `artifacts/studies/<model>/<study>/`; a model may build several studies.
- **Study descriptor**: `study.json` records model, composition, sut name, target SSD, the authored `Study` description, the experiment window (start, stop, step), and scenario paths. It carries no tolerance.
- **Scenario packaging**: `pyssp_workflow.execute.package_scenario` copies the study SSV/SSM into the SSP and adds one root `ParameterBinding`. A fixture that exercises another parameter form applies it with `pyssp_standard` in its build hook.
- **Tolerance**: read from the composed FMUs' model descriptions; not part of the experiment.
- **Runtime**: `run_simulations.py` runs the built SSP as-is. No scenario injection.
- **Canonicalization**: strip all runtime container names from result signals; `fmu.h` canonicalizes to `h`.
- **Comparison**: `pyssp_vv.measure` aligns trajectories and produces metrics; `pyssp_vv.judge` produces `pass`, `fail`, or `invalid`.
- **Model policy**: signal invariants live in `workflow/model_policy.py`; registry data carries tolerances and reference applicability.
- **Campaign**: build model, build study, simulate, and compare run as `sequence_extensions` nodes.
- **Registry**: a case names its `study` and `build`; the registry resolves `artifacts/models/<model>/<study>/<build>/`.
- **Capability ownership**: `pyssp_workflow` composes `pyssp_standard`, `pyssp_simulate`, `pyssp_vv`, and `pyssp_sysml2`.

## Owns
- Concrete build, study, and runtime mechanism.

## Excludes
- Product promise: `CP-001`.
- Stage boundary: `INFO-002`.
- Verification: `EVAL-001`.
