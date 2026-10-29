# variation_body_gain

## Origin

Authored in this repository at `architecture/variation_body_gain.sysml`, adapted from the variant-body shape in `docs/breakdown/06-evolution/selected/examples/variation-points/10_nested_variation.sysml`. The Sine, Gain, and Product FMUs are shared fixtures under `models/fmu/`; first added 2026-10-29 with the variation-point batch.

## Overview

One definition-level variation point, `PathChoice`, whose variants are bodies rather than types. `PathChoice` declares boundary ports `u` and `y`; the `oneStage` body holds one Gain, and the `twoStages` body holds a Product feeding a Gain. `System` is `source : Sine` plus `path : PathChoice`, with `source.y -> path.u`. Each analysis selects one body and declares its own `ScenarioSet`, binding it through the variation-resolved usages `sut.source.parameters.*` and `sut.path.gain.parameters.k`, so the build packages an external SSV plus an external SSM that targets `path.gain.k`. Parameter form: external SSV + external SSM.

## Architecture Source

- `architecture/variation_body_gain.sysml`
- Exportable composition: `System :> SspModel`
- Variation point: `variation part def PathChoice` with `variant part oneStage { part gain : Gain; ... }` and `variant part twoStages { part product : Product; part gain : Gain; ... }`
- `ScenarioSet` (amplitude, f, offset, startTime, k) is declared on each analysis; `bind` connects it to the source parameters and to `path.gain`.
- Analysis compositions: `one_stage :> Analysis`, `two_stages :> Analysis`
- No legacy SSD, SSV, or SSM is checked into the model directory.

## Analyses

- `one_stage :> Analysis` selects `sut.path=oneStage` (model `path=oneStage`); the body's `gain` resolves to the `path.gain` binding.
- `two_stages :> Analysis` selects `sut.path=twoStages` (model `path=twoStages`); its `gain` is also the `path.gain` binding target.
- Both analyses bind `sut.source.parameters.amplitude/f/offset/startTime` and `sut.path.gain.parameters.k`; the packaged SSM targets `source.amplitude`, `source.f`, `source.offset`, `source.startTime`, and `path.gain.k`.
- Selection is applied at build time through `build_fixture(selections={analysis: {"analysis": {...}, "model": {...}}})`; analysis keys are rooted at the `Analysis`, model keys at `System`.
- Experiment: `startTime=0.0`, `stopTime=1.0`, `stepSize=0.001`.
- Each analysis directory carries `ScenarioSet.ssv` and `<analysis>.ssm`; the build binds them into the exported SSP after `build_fixture`.
- Artifacts: `artifacts/analyses/variation_body_gain/<analysis>/`; analyses are never exported as SSPs.
- Registry: not registered. The engines disagree on this fixture, so there is no comparison gate or simulation evidence.

## Strategy Role

- Structural variation fixture: the selection replaces the usage type with a synthesized definition built from the selected body.
- Build-level contract test: `tests/test_variation_cases.py` asserts per-analysis element trees, the packaged external SSV+SSM, and the `path.gain.k` mapping target.
- Catches a body whose inner parts leak into another selection, lost boundary wiring, a stale packaged FMU, and a scenario packaged as an inline mapping.
- Not registered; the packaging is asserted, the behavior is not.

## Structure

- `source : Sine -> path : PathChoice`; there is no root output port.
- `oneStage`: `path` contains `gain : Gain`; `u -> gain.u`, `gain.y -> y`.
- `twoStages`: `path` contains `product : Product` and `gain : Gain`; `u -> product.u1` and `u -> product.u2`, `product.y -> gain.u`, `gain.y -> y`.

## Intent

- Prove that selecting a variant body changes the SSD element tree and the packaged FMU set while the `System` boundary wiring stays fixed, and that a scenario applied through the body is packaged as an external SSV+SSM.

## Expected Behavior

- Packaged set: `amplitude=1`, `f=1`, `offset=0`, `startTime=0.5`, `k=3`; `source.y = sin(2*pi*(t-0.5))` for `t >= 0.5`.
- `one_stage` gives `path.y = 3*source.y`; `two_stages` gives `path.y = 3*source.y^2`.
- There is no root output; the signals are `path.y` and the nested `gain.y`.
- These are algebraic expectations only; no registry gate confirms them.

## Simulation Notes

- Not registered: there is no simulation or comparison evidence for either analysis, and the engines disagree. ssp4sim does not apply the nested `path.gain.k` target, while OMSimulator applies `k` but loses the connection into the synthesized `path` subsystem.
- The packaged `path.gain.k` mapping is not readable as intended by either engine, so neither selection's trajectories may be read as a pass; the fixtures document the engine behavior, not a working scenario.

## Packaging Notes

- Exported model: `artifacts/models/variation_body_gain/<analysis>/model/`
- Analysis artifacts: `artifacts/analyses/variation_body_gain/<analysis>/`
- Packaged scenario: `resources/ScenarioSet.ssv` with `resources/<analysis>.ssm` (external SSV + external SSM)
- FMU sources: `models/fmu/Modelica.Blocks.Sources.Sine/fmu`, `models/fmu/Modelica.Blocks.Math.Gain/fmu`, and `models/fmu/Modelica.Blocks.Math.Product/fmu` (only in `two_stages`)
- Build: `python3 scripts/build_models.py run variation_body_gain`
