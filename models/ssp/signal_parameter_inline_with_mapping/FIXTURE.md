# signal_parameter_inline_with_mapping

## Origin

Assembled from shared Modelica FMUs. The model and study are authored in SysML
at `architecture/signal_parameter_inline_with_mapping.sysml`.

## Overview

`signal_parameter_inline_with_mapping` is a deterministic signal-propagation SSP fixture built from shared
Modelica FMUs. Parameter form: inline SSV + external SSM.

## Architecture Source

- `architecture/signal_parameter_inline_with_mapping.sysml`
- Exportable composition: `System :> SspModel`
- Study composition: `baseline :> Study`
- No legacy SSD, SSV, or SSM is checked into the model directory.

## Studies

- `baseline :> Study`
- Scenario set: `ScenarioSet`
- Experiment: `startTime=0.0`, `stopTime=1.0`, `stepSize=0.001`
- Tolerance is not part of the experiment; it comes from the FMU model
  descriptions.
- Artifacts: `artifacts/studies/signal_parameter_inline_with_mapping/baseline/`
- Studies are never exported as SSPs.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- OMSimulator

## Structure

- `Step` (inline values + external SSM)

## Strategy Role

- Deterministic signal-propagation fixture.
- Coverage for inline SSV with external SSM.

## Intent

- Validate that inline parameter values combined with an external mapping resolve to the component parameters.

## Expected Behavior

- Step output transitions at the configured time and height with no one-step lag.

## Main Failures This Catches

- Inline values ignored when a mapping is present.
- Unsupported inline+mapping combination.
- Mapping resolution failure.

## Simulation Notes

- The build packages the `ScenarioSet` scenario into the exported SSP in the
  fixture's parameter form.
- The runtime runs the built SSP as-is; it does not inject a scenario.
- Form: inline SSV + external SSM.

## Packaging Notes

- Exported model: `artifacts/models/signal_parameter_inline_with_mapping/baseline/model/`
- Study artifacts: `artifacts/studies/signal_parameter_inline_with_mapping/baseline/`
- FMU sources:
- `models/fmu/Modelica.Blocks.Sources.Step/fmu`
- Build: `python3 scripts/build_models.py run signal_parameter_inline_with_mapping`

## Typical Use

- Parameter-form regression checks.
