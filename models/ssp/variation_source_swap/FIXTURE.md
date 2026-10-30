# variation_source_swap

## Origin

Authored in this repository at `architecture/variation_source_swap.sysml`, adapted from the definition-level part-variation shape in `docs/breakdown/06-evolution/selected/examples/variation-points/01_structural_part_variation.sysml`. The Step and Sine FMUs are shared fixtures under `models/fmu/`; first added 2026-10-29 with the variation-point batch.

## Overview

One definition-level variation point, `SourceChoice`, offers two source FMUs as variant parts. `System.source : SourceChoice` is the only part, and `System` has no root output port. Each analysis declares its own `ScenarioSet` and binds it through the variation-resolved usage `sut.source.parameters.*`, so the build packages an external SSV plus an external SSM. The same composition therefore produces one SSP per selection: the component name `source` and the connector layout stay fixed, while the packaged FMU, the packaged scenario, and `extra/org.pyssp/selection.json` change. Each analysis declares its selection in `pyssp_selection`, and `build.py` builds the adapter's legal plans. Parameter form: external SSV + external SSM.

## Architecture Source

- `architecture/variation_source_swap.sysml`
- Exportable composition: `System :> SspModel`
- Variation point: `variation part def SourceChoice` with `variant part step : Step` and `variant part sine : Sine`
- `Step` and `Sine` expose `y` plus their FMU parameter connectors; `System` exposes no `y` port.
- `ScenarioSet` (height, offset, startTime, amplitude, f) is declared on each analysis; `bind` connects it to the selected source's parameter port.
- Analysis compositions: `step :> Analysis`, `sine :> Analysis`
- No legacy SSD, SSV, or SSM is checked into the model directory.

## Analyses

- `step :> Analysis` declares `pyssp_selection = "source=step"` and binds `sut.source.parameters.height/offset/startTime`; its packaged SSM targets `source.height`.
- `sine :> Analysis` declares `pyssp_selection = "source=sine"` and binds `sut.source.parameters.amplitude/f/offset/startTime`; its packaged SSM targets `source.amplitude`.
- The adapter resolves each declared selection and returns a plan; `build.py` builds the `legal` plans.
- Experiment: `startTime=0.0`, `stopTime=1.0`, `stepSize=0.001`.
- Each analysis directory carries `ScenarioSet.ssv` and `<analysis>.ssm`; the build binds them into the exported SSP after `build_fixture`.
- Artifacts: `artifacts/analyses/variation_source_swap/<analysis>/`; analyses are never exported as SSPs.
- Registry: both `step` and `sine` are registered on ssp4sim and OMSimulator, comparing `source.y`; both comparisons pass their gate.

## Strategy Role

- Structural variation fixture: the selection retypes one part usage, swaps the packaged FMU, and resolves which scenario member the SSM targets.
- Build-level contract test: `tests/test_variation_cases.py` asserts the element tree, the packaged FMU, the external SSV+SSM, and the variation-resolved mapping target per selection.
- Catches a dropped selection, an unselected point that silently builds, a stale SSD, a missing selection record, and a scenario packaged as an inline mapping.
- Both cases are registered in the cross-engine comparison gate; both comparisons currently pass.

## Structure

- `System` contains `source : SourceChoice`; there is no root output port.
- `step` selection: `source` is `Step.fmu`; signal `source.y`.
- `sine` selection: `source` is `Sine.fmu`; signal `source.y`.

## Intent

- Prove that a definition-level part variation changes the packaged FMU, the SSD component type, and `extra/org.pyssp/selection.json` while the component name, the connector layout, and the variation-resolved scenario mapping stay fixed.

## Expected Behavior

- `step`: `source.y = offset + height*[t >= startTime]` with the packaged set (`height=2`, `offset=0`, `startTime=0.5`).
- `sine`: `source.y = offset + amplitude*sin(2*pi*f*(t-startTime))` for `t >= startTime`, with `amplitude=2`, `f=1`, `offset=0`.
- There is no root output; the compared signal is `source.y`.

## Simulation Notes

- Both analyses run the built SSP as-is; the scenario is packaged, not injected.
- The registered gate passes for both cases: `source.y` has a shift-tolerant max error of 0 for `step` and ~5e-7 for `sine`.

## Limitations

- The selection is authored per analysis and the adapter returns `legal`, `violated`, or `invalid`; a `violated` analysis is expected only where the fixture documents a pruned branch.

## Packaging Notes

- Exported model: `artifacts/models/variation_source_swap/<analysis>/model/`
- Analysis artifacts: `artifacts/analyses/variation_source_swap/<analysis>/`
- Packaged scenario: `resources/ScenarioSet.ssv` with `resources/<analysis>.ssm` (external SSV + external SSM)
- FMU sources: `models/fmu/Modelica.Blocks.Sources.Step/fmu`, `models/fmu/Modelica.Blocks.Sources.Sine/fmu`
- Selection record: `extra/org.pyssp/selection.json` records the analysis's authored `pyssp_selection`.
- Build: `python3 scripts/build_models.py run variation_source_swap`
