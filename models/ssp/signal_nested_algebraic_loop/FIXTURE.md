# signal_nested_algebraic_loop

## Origin

Assembled from shared Modelica FMUs. The model and analysis are authored in SysML
under `architecture/`.

## Overview

`signal_nested_algebraic_loop` is a deterministic signal-propagation SSP fixture built from shared
Modelica FMUs. Parameter form: external target-named SSV, no mapping.

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
- Artifacts: `artifacts/analyses/signal_nested_algebraic_loop/baseline/`
- Analyses are never exported as SSPs.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- OMSimulator

## Structure

- `Sine -> Add_outer.u1`
- `Add_outer.y -> Gain_outer.u`
- `Gain_outer.y -> Add_inner.u1`
- `Gain_inner.y -> Add_inner.u2`
- `Add_inner.y -> Add_outer.u2` and `Add_inner.y -> Gain_inner.u`

## Strategy Role

- Deterministic signal-propagation fixture.
- Behavioral comparison target.
- Regression anchor for nested loop resolution.

## Intent

- Validate solver handling when one closed loop depends on another closed loop.

## Expected Behavior

- `add_outer.y = 2 * sine.y`, `add_inner.y = sine.y`, `gain_outer.y = 0.5 * sine.y`, `gain_inner.y = 0.5 * sine.y`.

## Main Failures This Catches

- Failure to converge when loop resolution is nested.
- Incorrect propagation between inner and outer paths.
- Evaluation-order bugs invisible in a single loop.

## Simulation Notes

- The build packages the `ScenarioSet` scenario into the exported SSP in the
  fixture's parameter form.
- The runtime runs the built SSP as-is; it does not inject a scenario.
- Form: external target-named SSV, no mapping.

## Packaging Notes

- Exported model: `artifacts/models/signal_nested_algebraic_loop/baseline/model/`
- Analysis artifacts: `artifacts/analyses/signal_nested_algebraic_loop/baseline/`
- FMU sources:
- `models/fmu/Modelica.Blocks.Sources.Sine/fmu`
- `models/fmu/Modelica.Blocks.Math.Gain/fmu`
- `models/fmu/Modelica.Blocks.Math.Add/fmu`
- Build: `python3 scripts/build_models.py run signal_nested_algebraic_loop`

## Typical Use

- Tight-tolerance cross-engine comparison.
- Regression testing for nested loop handling.
