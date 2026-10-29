# signal_sine_gain_add

## Origin

Assembled from shared Modelica FMUs. The model and analysis are authored in SysML
at `architecture/signal_sine_gain_add.sysml`.

## Overview

`signal_sine_gain_add` is a deterministic signal-propagation SSP fixture built from shared
Modelica FMUs. Parameter form: inline root parameter set.

## Architecture Source

- `architecture/signal_sine_gain_add.sysml`
- Exportable composition: `System :> SspModel`
- Analysis composition: `baseline :> Analysis`
- No legacy SSD, SSV, or SSM is checked into the model directory.

## Analyses

- `baseline :> Analysis`
- Scenario set: `ScenarioSet`
- Experiment: `startTime=0.0`, `stopTime=1.0`, `stepSize=0.001`
- Tolerance is not part of the experiment; it comes from the FMU model
  descriptions.
- Artifacts: `artifacts/analyses/signal_sine_gain_add/baseline/`
- Analyses are never exported as SSPs.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- OMSimulator

## Structure

- `Sine -> Gain -> Add.u1`
- `Step -> Add.u2`

## Strategy Role

- Deterministic signal-propagation fixture.
- Priority 2 propagation test.
- Inline parameter packaging anchor.

## Intent

- Validate a short transformation chain with mixed source types and inline parameter values.

## Expected Behavior

- Output equals `gain * sine + step`.

## Main Failures This Catches

- Drift in chained propagation.
- Wrong evaluation order in multi-stage networks.
- Loss of amplitude or offset across components.

## Simulation Notes

- The build packages the `ScenarioSet` scenario into the exported SSP in the
  fixture's parameter form.
- The runtime runs the built SSP as-is; it does not inject a scenario.
- Form: inline root parameter set.

## Packaging Notes

- Exported model: `artifacts/models/signal_sine_gain_add/baseline/model/`
- Analysis artifacts: `artifacts/analyses/signal_sine_gain_add/baseline/`
- FMU sources:
- `models/fmu/Modelica.Blocks.Sources.Sine/fmu`
- `models/fmu/Modelica.Blocks.Sources.Step/fmu`
- `models/fmu/Modelica.Blocks.Math.Gain/fmu`
- `models/fmu/Modelica.Blocks.Math.Add/fmu`
- Build: `python3 scripts/build_models.py run signal_sine_gain_add`

## Typical Use

- Tight-tolerance cross-engine comparison.
- Regression testing for inline parameter packaging.
