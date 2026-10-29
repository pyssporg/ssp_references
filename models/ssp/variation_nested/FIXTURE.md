# variation_nested

## Origin

Authored in this repository at `architecture/variation_nested.sysml`, adapted from `docs/breakdown/06-evolution/selected/examples/variation-points/10_nested_variation.sysml`; the FMU metadata follows `models/ssp/signal_step_product/` and `models/ssp/signal_step_gain/`. First added 2026-10-29 with the variation-point batch.

## Overview

Two levels of part variation around one fixed outer composition. The outer point `PathChoice` offers `directPath` (one Gain) and `nestedPath` (an inner `StageChoice` feeding `output_gain`). The inner point `StageChoice` offers `gainStage` and `secondStage`; only `gainStage` is exercised by a study. The source is `Sine`. Each study declares its own `ScenarioSet` and binds it through the variation-resolved usages, so the build packages an external SSV plus an external SSM. Parameter form: external SSV + external SSM.

## Architecture Source

- `architecture/variation_nested.sysml`
- Exportable composition: `System :> SspModel`
- Outer point: `variation part def PathChoice` with `variant part directPath : DirectPath` and `variant part nestedPath : NestedPath`
- Inner point: `variation part def StageChoice` with `variant part gainStage : GainStage` and `variant part secondStage : SecondStage`
- `GainStage` and `SecondStage` each wrap one Gain (`gain`, `gain2`) between `stage_in` and `stage_out`.
- `NestedPath` declares `variation part inner_stage : StageChoice` and `part output_gain : Gain`.
- `ScenarioSet` (offset, startTime, gainK, stageK) is declared on each study; `bind` connects it to the source parameters and to the resolved gain target.
- Study compositions: `direct :> Study`, `nested_gain :> Study`
- No legacy SSD, SSV, or SSM is checked into the model directory.

## Studies

- `direct :> Study` selects `sut.path=directPath` (model `path=directPath`) and binds `sut.source.parameters.offset/startTime` plus `sut.path.gain.parameters.k`; its packaged SSM targets `path.gain.k`.
- `nested_gain :> Study` selects `sut.path=nestedPath` and `sut.path.inner_stage=gainStage` (model `path=nestedPath`, `path.inner_stage=gainStage`) and binds `sut.source.parameters.offset/startTime`, `sut.path.output_gain.parameters.k`, and `sut.path.inner_stage.gain.parameters.k`; its packaged SSM targets `path.inner_stage.gain.k`.
- Selection is applied at build time through `build_fixture(selections={study: {"study": {...}, "model": {...}}})`; study keys are rooted at the Study, model keys at `System`.
- Experiment: `startTime=0.0`, `stopTime=1.0`, `stepSize=0.001`.
- Each study directory carries `ScenarioSet.ssv` and `<study>.ssm`; the build binds them into the exported SSP after `build_fixture`.
- Artifacts: `artifacts/studies/variation_nested/<study>/`; studies are never exported as SSPs.
- Registry: not registered. OMSimulator cannot instantiate the inner subsystem, so there is no comparison evidence.
- `secondStage` is defined but no study selects it.

## Strategy Role

- Proves the dotted key resolves the inner point only after the outer body is selected; selecting only `path=nestedPath` fails naming `path.inner_stage`.
- Build-level contract test: `tests/test_variation_cases.py` asserts `direct` materialises `path.gain`, and `nested_gain` materialises `path.output_gain` plus `path.inner_stage.gain`, with the packaged external SSV+SSM and the `path.inner_stage.gain.k` mapping target.
- Catches an inner point resolved too early, a flattened outer body, a component tree that drifts between selections, and a scenario packaged as an inline mapping.

## Structure

- `System` = `source : Sine` + `path : PathChoice`; `source.y -> path.u`. There is no root output port.
- `directPath`: `path` contains `gain : Gain`.
- `nestedPath`: `path` contains `inner_stage : StageChoice` and `output_gain : Gain`; with `gainStage`, `inner_stage` contains `gain : Gain`. With `secondStage`, it would contain `gain2 : Gain`.
- Signals: `source.y`, `path.y`/`output_gain.y`, and the stage output.

## Intent

- One selection names both levels: `path=nestedPath` plus `path.inner_stage=gainStage`, with the inner point existing only inside the selected outer body, and the scenario resolved to the nested gain.

## Expected Behavior

- Packaged set: `offset=0`, `startTime=0.5`, `gainK=3`, `stageK=5`; `source.y = sin(2*pi*(t-0.5))` for `t >= 0.5`.
- `direct` gives `path.y = 3*source.y`; `nested_gain` gives `output_gain.y = 15*source.y` (inner gain `k=5`, output gain `k=3`).
- The two studies now differ in signal amplitude as well as structure.
- No registry gate confirms either trajectory.

## Simulation Notes

- Not registered: there is no simulation or comparison evidence for either study. OMSimulator cannot instantiate a synthesized subsystem that itself contains a synthesized subsystem (`KeyError: 'System.path.inner_stage'`), so the registered engine cannot run the nested case; the missing gate must not be read as a pass.

## Limitations

- Inline outer variant bodies that contain a variation usage are rejected when resolution starts at a Study (`sut.path` counts as depth two). The outer variants are therefore typed definitions (`DirectPath`, `NestedPath`), with the inner point inside `NestedPath`.
- Only two levels of variation are supported; a third level is rejected.
- `secondStage` is defined but remains unexercised.

## Packaging Notes

- Exported model: `artifacts/models/variation_nested/<study>/model/`
- Study artifacts: `artifacts/studies/variation_nested/<study>/`
- Packaged scenario: `resources/ScenarioSet.ssv` with `resources/<study>.ssm` (external SSV + external SSM)
- Packaged FMUs: `resources/Sine`, `resources/Gain`. The architecture still defines `Product`/`ProductFmu`, but no current variant uses it, so it is not packaged.
- Build: `python3 scripts/build_models.py run variation_nested`
