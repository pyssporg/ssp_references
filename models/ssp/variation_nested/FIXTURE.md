# variation_nested

## Origin

Authored in this repository at `architecture/variation_nested.sysml`, adapted from `docs/breakdown/06-evolution/selected/examples/variation-points/10_nested_variation.sysml`; the FMU metadata follows `models/ssp/signal_step_product/` and `models/ssp/signal_step_gain/`. First added 2026-10-29 with the variation-point batch.

## Overview

Two levels of part variation around one fixed outer composition. The outer point `PathChoice` offers `directPath` (one Gain) and `nestedPath` (an inner `StageChoice` feeding `output_gain`). The inner point `StageChoice` offers `gainStage` and `secondStage`; only `gainStage` is exercised by a study. The source is `Sine`. Each study selects the outer variant, and `nested_gain` also selects the inner one. No parameter set or bind is authored; both FMUs run with their defaults.

## Architecture Source

- `architecture/variation_nested.sysml`
- Exportable composition: `System :> SspModel`
- Outer point: `variation part def PathChoice` with `variant part directPath : DirectPath` and `variant part nestedPath : NestedPath`
- Inner point: `variation part def StageChoice` with `variant part gainStage : GainStage` and `variant part secondStage : SecondStage`
- `GainStage` and `SecondStage` each wrap one Gain (`gain`, `gain2`) between `stage_in` and `stage_out`.
- `NestedPath` declares `variation part inner_stage : StageChoice` and `part output_gain : Gain`.
- Study compositions: `direct :> Study`, `nested_gain :> Study`
- No legacy SSD, SSV, or SSM is checked into the model directory.

## Studies

- `direct :> Study` selects `sut.path=directPath`; the model build selects `path=directPath`.
- `nested_gain :> Study` selects `sut.path=nestedPath` and `sut.path.inner_stage=gainStage`; the model build selects `path=nestedPath` and `path.inner_stage=gainStage`.
- Selection is applied at build time through `build_fixture(selections={study: {"study": {...}, "model": {...}}})`; study keys are rooted at the Study, model keys at `System`.
- Experiment: `startTime=0.0`, `stopTime=1.0`, `stepSize=0.001`.
- No SSV or SSM is generated; each study directory holds only `study.json`.
- Artifacts: `artifacts/studies/variation_nested/<study>/`; studies are never exported as SSPs.
- Registry: not registered. OMSimulator fails to import the inner subsystem (`System.path.inner_stage`), so there is no comparison evidence.
- `secondStage` is defined but no study selects it.

## Strategy Role

- Proves the dotted key resolves the inner point only after the outer body is selected; selecting only `path=nestedPath` fails naming `path.inner_stage`.
- Build-level contract test: `tests/test_variation_cases.py` asserts `direct` materialises `path.gain`, and `nested_gain` materialises `path.output_gain` plus `path.inner_stage.gain`.
- Catches an inner point resolved too early, a flattened outer body, and a component tree that drifts between selections.

## Structure

- `System` = `source : Sine` + `path : PathChoice`; `source.y -> path.u`. There is no root output port.
- `directPath`: `path` contains `gain : Gain`.
- `nestedPath`: `path` contains `inner_stage : StageChoice` and `output_gain : Gain`; with `gainStage`, `inner_stage` contains `gain : Gain`. With `secondStage`, it would contain `gain2 : Gain`.
- Signals: `source.y`, `path.y`/`output_gain.y`, and the stage output.

## Intent

- One selection names both levels: `path=nestedPath` plus `path.inner_stage=gainStage`, with the inner point existing only inside the selected outer body.

## Expected Behavior

- With FMU defaults (`Sine` amplitude 1, `f=1`; `Gain` `k=1`): `direct` gives `path.y = sin(2*pi*t)`, and `nested_gain` gives `output_gain.y = sin(2*pi*t)` (two unity gains).
- The two studies are algebraically identical under the FMU defaults; this fixture currently distinguishes structure, not signal shape.
- No registry gate confirms either trajectory.

## Simulation Notes

- Not registered: there is no simulation or comparison evidence for either study. OMSimulator cannot import the inner subsystem, and the missing gate must not be read as a pass.
- No parameter set or bind is applied through either variation-resolved body, so parameter packaging is not exercised; both selections run with FMU defaults.

## Limitations

- Inline outer variant bodies that contain a variation usage are rejected when resolution starts at a Study (`sut.path` counts as depth two). The outer variants are therefore typed definitions (`DirectPath`, `NestedPath`), with the inner point inside `NestedPath`.
- Only two levels of variation are supported; a third level is rejected.
- `secondStage` is defined but remains unexercised.

## Packaging Notes

- Exported model: `artifacts/models/variation_nested/<study>/model/`
- Study artifacts: `artifacts/studies/variation_nested/<study>/`
- Packaged FMUs: `resources/Sine`, `resources/Gain`. The architecture still defines `Product`/`ProductFmu`, but no current variant uses it, so it is not packaged.
- Build: `python3 scripts/build_models.py run variation_nested`
