# signal_nested_pass_through

## Origin

Assembled from shared Modelica FMUs. The model and analysis are authored in SysML
at `architecture/signal_nested_pass_through.sysml`.

## Overview

`signal_nested_pass_through` is a deterministic signal-propagation SSP fixture built from shared
Modelica FMUs. Parameter form: inline component parameters inside a nested system.

## Architecture Source

- `architecture/signal_nested_pass_through.sysml`
- Exportable composition: `System :> SspModel`
- Analysis composition: `baseline :> Analysis`
- No legacy SSD, SSV, or SSM is checked into the model directory.

## Analyses

- `baseline :> Analysis`
- Scenario set: `ScenarioSet`
- Experiment: `startTime=0.0`, `stopTime=1.0`, `stepSize=0.001`
- Tolerance is not part of the experiment; it comes from the FMU model
  descriptions.
- Artifacts: `artifacts/analyses/signal_nested_pass_through/baseline/`
- Analyses are never exported as SSPs.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim

OMSimulator is not registered for this fixture: it fails to instantiate the
stack's emitted content (duplicate root-scope connector, DD-014/DD-015). ssp4sim
applies the inline component parameters correctly.

## Structure

- `Step -> Inner.u`
- `Inner`: `u -> gain.u`, `gain.y -> v`
- `Inner.v -> Add.u1`
- Root output: `Add.y -> y`
- All wiring, including the boundary connections, is authored in SysML.

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
- Analysis artifacts: `artifacts/analyses/signal_nested_pass_through/baseline/`
- FMU sources:
- `models/fmu/Modelica.Blocks.Sources.Step/fmu`
- `models/fmu/Modelica.Blocks.Math.Gain/fmu`
- `models/fmu/Modelica.Blocks.Math.Add/fmu`
- Build: `python3 scripts/build_models.py run signal_nested_pass_through`

## Typical Use

- Nested-system regression checks.
