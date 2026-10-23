# signal_algebraic_loop

## Origin

Assembled from shared Modelica FMUs. The model and study are authored in SysML
at `architecture/signal_algebraic_loop.sysml`.

## Overview

`signal_algebraic_loop` is a deterministic signal-propagation SSP fixture built from shared
Modelica FMUs. Parameter form: external target-named SSV, no mapping.

## Architecture Source

- `architecture/signal_algebraic_loop.sysml`
- Exportable composition: `System :> SspModel`
- Study composition: `baseline :> Study`
- No legacy SSD, SSV, or SSM is checked into the model directory.

## Studies

- `baseline :> Study`
- Scenario set: `ScenarioSet`
- Experiment: `startTime=0.0`, `stopTime=1.0`, `stepSize=0.001`
- Tolerance is not part of the experiment; it comes from the FMU model
  descriptions.
- Artifacts: `artifacts/studies/signal_algebraic_loop/baseline/`
- Studies are never exported as SSPs.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- OMSimulator

## Structure

- `Sine -> Add.u1`
- `Add.y -> Gain.u`
- `Gain.y -> Add.u2`

## Strategy Role

- Deterministic signal-propagation fixture.
- Behavioral comparison target.
- Regression anchor for a single closed algebraic loop.

## Intent

- Validate solver and scheduler handling when the system has one closed algebraic loop.
- Distinguish loop-resolution errors from acyclic feedthrough errors.

## Expected Behavior

- `add.y = 2 * sine.y`, `gain.y = sine.y`.

## Main Failures This Catches

- Failure to solve a closed algebraic loop.
- Wrong fixed-point iteration or evaluation order.
- One-step lag in feedback propagation.

## Simulation Notes

- The build packages the `ScenarioSet` scenario into the exported SSP in the
  fixture's parameter form.
- The runtime runs the built SSP as-is; it does not inject a scenario.
- Form: external target-named SSV, no mapping.

## Packaging Notes

- Exported model: `artifacts/models/signal_algebraic_loop/baseline/model/`
- Study artifacts: `artifacts/studies/signal_algebraic_loop/baseline/`
- FMU sources:
- `models/fmu/Modelica.Blocks.Sources.Sine/fmu`
- `models/fmu/Modelica.Blocks.Math.Gain/fmu`
- `models/fmu/Modelica.Blocks.Math.Add/fmu`
- Build: `python3 scripts/build_models.py run signal_algebraic_loop`

## Typical Use

- Tight-tolerance cross-engine comparison.
- Regression testing for algebraic loop handling.
