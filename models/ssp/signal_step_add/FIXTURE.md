# signal_step_add

## Origin

Assembled from shared Modelica FMUs. The model and study are authored in SysML
at `architecture/signal_step_add.sysml`.

## Overview

`signal_step_add` is a deterministic signal-propagation SSP fixture built from shared
Modelica FMUs. Parameter form: external SSV + external SSM (disambiguated members).

## Architecture Source

- `architecture/signal_step_add.sysml`
- Exportable composition: `System :> SspModel`
- Study composition: `baseline :> Study`
- No legacy SSD, SSV, or SSM is checked into the model directory.

## Studies

- `baseline :> Study`
- Scenario set: `ScenarioSet`
- Experiment: `startTime=0.0`, `stopTime=1.0`, `stepSize=0.001`
- Tolerance is not part of the experiment; it comes from the FMU model
  descriptions.
- Artifacts: `artifacts/studies/signal_step_add/baseline/`
- Studies are never exported as SSPs.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- OMSimulator

## Structure

- `Step_a -> Add.u1`
- `Step_b -> Add.u2`

## Strategy Role

- Deterministic signal-propagation fixture.
- Priority 1 propagation test.
- Minimal reproducer for fan-in behavior.

## Intent

- Validate deterministic fan-in behavior and algebraic summation.

## Expected Behavior

- Output equals the exact sum of both source signals at every recorded step.

## Main Failures This Catches

- Incorrect handling of multiple incoming signals.
- Wrong input ordering or connector binding.
- Missed update on one input during a step.

## Simulation Notes

- The build packages the `ScenarioSet` scenario into the exported SSP in the
  fixture's parameter form.
- The runtime runs the built SSP as-is; it does not inject a scenario.
- Form: external SSV + external SSM (disambiguated members).

## Packaging Notes

- Exported model: `artifacts/models/signal_step_add/baseline/model/`
- Study artifacts: `artifacts/studies/signal_step_add/baseline/`
- FMU sources:
- `models/fmu/Modelica.Blocks.Sources.Step/fmu`
- `models/fmu/Modelica.Blocks.Math.Add/fmu`
- Build: `python3 scripts/build_models.py run signal_step_add`

## Typical Use

- Tight-tolerance comparison tests.
- Debugging connector binding and multi-input update behavior.
