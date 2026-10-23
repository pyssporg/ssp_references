# signal_nested_pass_through

## Origin

Assembled from shared Modelica FMUs. The model and study are authored in SysML
at `architecture/signal_nested_pass_through.sysml`.

## Overview

`signal_nested_pass_through` is a deterministic signal-propagation SSP fixture built from shared
Modelica FMUs. Parameter form: inline component parameters inside a nested system.

## Architecture Source

- `architecture/signal_nested_pass_through.sysml`
- Exportable composition: `System :> SspModel`
- Study composition: `baseline :> Study`
- No legacy SSD, SSV, or SSM is checked into the model directory.

## Studies

- `baseline :> Study`
- Scenario set: `ScenarioSet`
- Experiment: `startTime=0.0`, `stopTime=1.0`, `stepSize=0.001`
- Tolerance is not part of the experiment; it comes from the FMU model
  descriptions.
- Artifacts: `artifacts/studies/signal_nested_pass_through/baseline/`
- Studies are never exported as SSPs.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- OMSimulator

## Structure

- `Step -> Inner(gain) -> Add.u1`
- Inner boundary wired by the build hook

## Strategy Role

- Composite SSP fixture.
- Nested-system pass-through coverage.

## Intent

- Validate parameter application and signal routing through a nested system boundary.

## Expected Behavior

- `add.y` follows the gained step through the nested system.

## Main Failures This Catches

- Nested boundary routing errors.
- Inline parameter loss inside a nested system.

## Simulation Notes

- The build packages the `ScenarioSet` scenario into the exported SSP in the
  fixture's parameter form.
- The runtime runs the built SSP as-is; it does not inject a scenario.
- Form: inline component parameters inside a nested system.

## Packaging Notes

- Exported model: `artifacts/models/signal_nested_pass_through/baseline/model/`
- Study artifacts: `artifacts/studies/signal_nested_pass_through/baseline/`
- FMU sources:
- `models/fmu/Modelica.Blocks.Sources.Step/fmu`
- `models/fmu/Modelica.Blocks.Math.Gain/fmu`
- `models/fmu/Modelica.Blocks.Math.Add/fmu`
- Build: `python3 scripts/build_models.py run signal_nested_pass_through`

## Typical Use

- Nested-system regression checks.
