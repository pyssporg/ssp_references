---
id: INFO-008
type: info
title: Build, study, and runtime workflow
summary: Build exports SspModel SSPs and study artifacts; simulate injects study data into a runtime SSP copy.
date: 2026-10-22
status: current
---

# Build, study, and runtime workflow

- **Authoring**: `pyssp_workflow.authoring.derive_ssp_from_sysml` and `derive_study_from_sysml` invoke the `pyssp` CLI; no `pyssp_sysml2` import.
- **Model build**: `build.py` exports `artifacts/models/<model>/<build>/`; `signal_step_gain` uses build `model`.
- **Study build**: `pyssp generate study` writes SSV, SSM, and `study.json` under `artifacts/studies/<model>/<study>/`.
- **Study descriptor**: `study.json` records model, composition, sut name, target SSD, experiment window, step size, tolerance, and scenario paths.
- **Runtime descriptor**: `pyssp_workflow.params.read_study_descriptor` reads `study.json` and points at the standardized scenario SSV and SSM.
- **Runtime inject**: `pyssp_workflow.execute.inject_scenario` copies the exported SSP and uses `pyssp_standard.SSP.add_external_parameterset` to merge the same SSV/SSM and one root-level `ParameterBinding`.
- **Immutability**: exported SSP is never mutated; the runtime copy is the only engine input.
- **Canonicalization**: strip all runtime container names from result signals; `fmu.h` canonicalizes to `h`.
- **Comparison**: `pyssp_vv.measure` aligns trajectories and produces metrics; `pyssp_vv.judge` produces `pass`, `fail`, or `invalid`.
- **Model policy**: signal invariants live in `workflow/model_policy.py`; registry data carries tolerances and reference applicability.
- **Campaign**: build model, build study, simulate, and compare run as `sequence_extensions` nodes.
- **Registry**: `build` selects the exported SSP; `study` selects study artifacts; case name selects simulation artifacts.
- **Capability ownership**: `pyssp_workflow` composes `pyssp_standard`, `pyssp_simulate`, `pyssp_vv`, and `pyssp_sysml2`.

## Owns
- Concrete build, study, and runtime mechanism.

## Excludes
- Product promise: `CP-001`.
- Stage boundary: `INFO-002`.
- Verification: `EVAL-001`.
