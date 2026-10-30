# signal_nested_parameter_bindings

## Origin

Assembled from shared Modelica FMUs. The model and analysis are authored in SysML
under `architecture/`.

## Overview

`signal_nested_parameter_bindings` is a deterministic signal-propagation SSP fixture built from shared
Modelica FMUs. Parameter form: nested inline sets plus a root external SSV+SSM override into a nested target.

## Architecture Source

- `architecture/` split by section: `01-interfaces.sysml`,
  `02-parameters.sysml`, `03-components.sysml`, `04-structure.sysml`,
  `05-analyses.sysml`
- Exportable composition: `System :> SspModel`
- Analysis composition: `baseline :> Analysis`
- No legacy SSD, SSV, or SSM is checked into the model directory.

## Analyses

- `baseline :> Analysis`
- Scenario set: `ScenarioSet`
- Experiment: `startTime=0.0`, `stopTime=1.0`, `stepSize=0.001`
- Tolerance is not part of the experiment; it comes from the FMU model
  descriptions.
- Artifacts: `artifacts/analyses/signal_nested_parameter_bindings/baseline/`
- Analyses are never exported as SSPs.

## Backends

This fixture is registered for simulation with the following backends:

- Not registered in the simulation registry.

## Structure

- `Step -> Add.u1`
- `Inner`: `sine.y -> gain.u`, `gain.y -> y`
- `Inner.y -> Add.u2`
- Root output: `Add.y -> y`
- All wiring, including the boundary connections, is authored in SysML.

## Strategy Role

- Composite SSP fixture.
- Mixed nested/root parameter-binding coverage.

## Intent

- Validate a root external mapping that targets a parameter already carrying a nested inline value.

## Expected Behavior

- The root external binding determines the effective nested `inner.sine.amplitude`.

## Main Failures This Catches

- Nested target override ignored.
- Wrong precedence between inline and external values.

## Simulation Notes

- The build packages the `ScenarioSet` scenario into the exported SSP in the
  fixture's parameter form.
- The runtime runs the built SSP as-is; it does not inject a scenario.
- Form: nested inline sets plus a root external SSV+SSM override into a nested target.

## Packaging Notes

- Exported model: `artifacts/models/signal_nested_parameter_bindings/baseline/model/`
- Analysis artifacts: `artifacts/analyses/signal_nested_parameter_bindings/baseline/`
- FMU sources:
- `models/fmu/Modelica.Blocks.Sources.Step/fmu`
- `models/fmu/Modelica.Blocks.Math.Add/fmu`
- `models/fmu/Modelica.Blocks.Sources.Sine/fmu`
- `models/fmu/Modelica.Blocks.Math.Gain/fmu`
- Build: `python3 scripts/build_models.py run signal_nested_parameter_bindings`

## Typical Use

- Parameter-form regression checks.
