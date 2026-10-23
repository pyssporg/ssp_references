# signal_step_gain

## Origin

Assembled from shared Modelica FMUs. The model and study are authored in SysML
at `architecture/signal_step_gain.sysml`.

## Overview

`signal_step_gain` is a deterministic signal-propagation SSP fixture built from shared
Modelica FMUs. Parameter form: external SSV + external SSM.

## Architecture Source

- `architecture/signal_step_gain.sysml`
- Exportable composition: `System :> SspModel`
- Study composition: `test_baseline :> Study`
- No legacy SSD, SSV, or SSM is checked into the model directory.

## Studies

- `test_baseline :> Study`
- Scenario set: `ScenarioSet`
- Experiment: `startTime=0.0`, `stopTime=1.0`, `stepSize=0.001`
- Tolerance is not part of the experiment; it comes from the FMU model
  descriptions.
- Artifacts: `artifacts/studies/signal_step_gain/test_baseline/`
- Studies are never exported as SSPs.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- OMSimulator
- FMPy

## Structure

- `Step -> Gain`

## Strategy Role

- Deterministic signal-propagation fixture.
- Priority 1 propagation test.
- Minimal reproducer for direct algebraic feedthrough.

## Intent

- Validate direct propagation of a stepped signal through a simple algebraic transform while exercising SysML model export and scenario packaging.

## Expected Behavior

- Output equals input multiplied by a fixed gain.
- The output step occurs at the same communication step as the input step.

## Main Failures This Catches

- One-step propagation lag.
- Wrong gain parameter handling.
- Incorrect connector mapping.
- Missing packaged scenario.

## Simulation Notes

- The build packages the `ScenarioSet` scenario into the exported SSP in the
  fixture's parameter form.
- The runtime runs the built SSP as-is; it does not inject a scenario.
- Form: external SSV + external SSM.

## Packaging Notes

- Exported model: `artifacts/models/signal_step_gain/test_baseline/model/`
- Study artifacts: `artifacts/studies/signal_step_gain/test_baseline/`
- FMU sources:
- `models/fmu/Modelica.Blocks.Sources.Step/fmu`
- `models/fmu/Modelica.Blocks.Math.Gain/fmu`
- Build: `python3 scripts/build_models.py run signal_step_gain`

## Typical Use

- Tight-tolerance comparison tests.
- Debugging direct feedthrough or step-alignment issues.
- Regression test for the `SspModel`/`Study` boundary.
