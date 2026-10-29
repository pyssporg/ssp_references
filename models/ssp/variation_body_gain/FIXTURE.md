# variation_body_gain

## Origin

Authored in this repository at `architecture/variation_body_gain.sysml`, adapted from the variant-body shape in `docs/breakdown/06-evolution/selected/examples/variation-points/10_nested_variation.sysml`. The Sine, Gain, and Product FMUs are shared fixtures under `models/fmu/`; first added 2026-10-29 with the variation-point batch.

## Overview

One definition-level variation point, `PathChoice`, whose variants are bodies rather than types. `PathChoice` declares boundary ports `u` and `y`; the `oneStage` body holds one Gain, and the `twoStages` body holds a Product feeding a Gain. `System` is `source : Sine` plus `path : PathChoice`, with `source.y -> path.u`. Each study selects one body at build time, so the synthesized `PathChoice__<variant>` subsystem differs between selections. No parameter set or bind is authored; both FMUs run with their defaults.

## Architecture Source

- `architecture/variation_body_gain.sysml`
- Exportable composition: `System :> SspModel`
- Variation point: `variation part def PathChoice` with `variant part oneStage { part gain : Gain; ... }` and `variant part twoStages { part product : Product; part gain : Gain; ... }`
- Study compositions: `one_stage :> Study`, `two_stages :> Study`
- No legacy SSD, SSV, or SSM is checked into the model directory.

## Studies

- `one_stage :> Study` selects `sut.path=oneStage`; the model build selects `path=oneStage`.
- `two_stages :> Study` selects `sut.path=twoStages`; the model build selects `path=twoStages`.
- Selection is applied at build time through `build_fixture(selections={study: {"study": {...}, "model": {...}}})`; study keys are rooted at the Study, model keys at `System`.
- Experiment: `startTime=0.0`, `stopTime=1.0`, `stepSize=0.001`.
- No SSV or SSM is generated; each study directory holds only `study.json`.
- Artifacts: `artifacts/studies/variation_body_gain/<study>/`; studies are never exported as SSPs.
- Registry: not registered. The engines' `gain.y` trajectories do not agree yet, so there is no comparison gate or simulation evidence.

## Strategy Role

- Structural variation fixture: the selection replaces the usage type with a synthesized definition built from the selected body.
- Build-level contract test: `tests/test_variation_cases.py` asserts that `one_stage` materialises `gain` and `two_stages` materialises `product` and `gain`, with the varied FMU packaged.
- Catches a body whose inner parts leak into another selection, lost boundary wiring, and a stale packaged FMU.

## Structure

- `source : Sine -> path : PathChoice`; there is no root output port.
- `oneStage`: `path` contains `gain : Gain`; `u -> gain.u`, `gain.y -> y`.
- `twoStages`: `path` contains `product : Product` and `gain : Gain`; `u -> product.u1` and `u -> product.u2`, `product.y -> gain.u`, `gain.y -> y`.

## Intent

- Prove that selecting a variant body changes the SSD element tree and the packaged FMU set while the `System` boundary wiring stays fixed.

## Expected Behavior

- With FMU defaults (`Sine` amplitude 1, `f=1`; `Gain` `k=1`; Product multiplies its inputs): `one_stage` gives `path.y = sin(2*pi*t)`, `two_stages` gives `path.y = sin(2*pi*t)^2`.
- There is no root output; the signals are `path.y` and the nested `gain.y`.
- These are algebraic expectations only; no registry gate confirms them.

## Simulation Notes

- Not registered: there is no simulation or comparison evidence for either study, and the unresolved `gain.y` disagreement must not be read as a pass.
- No parameter set or bind is applied through the variation-resolved body, so parameter packaging is not exercised; both selections run with FMU defaults.

## Packaging Notes

- Exported model: `artifacts/models/variation_body_gain/<study>/model/`
- Study artifacts: `artifacts/studies/variation_body_gain/<study>/`
- FMU sources: `models/fmu/Modelica.Blocks.Sources.Sine/fmu`, `models/fmu/Modelica.Blocks.Math.Gain/fmu`, and `models/fmu/Modelica.Blocks.Math.Product/fmu` (only in `two_stages`)
- Build: `python3 scripts/build_models.py run variation_body_gain`
