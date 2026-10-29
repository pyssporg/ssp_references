# signal_nested_external_bindings

## Origin

Assembled from shared Modelica FMUs. The model and analysis are authored in SysML
at `architecture/signal_nested_external_bindings.sysml`.

## Overview

`signal_nested_external_bindings` is a deterministic signal-propagation SSP fixture built from shared
Modelica FMUs. Parameter form: external SSV+SSM binding on the nested system; step inline.

## Architecture Source

- `architecture/signal_nested_external_bindings.sysml`
- Exportable composition: `System :> SspModel`
- Analysis composition: `baseline :> Analysis`
- No legacy SSD, SSV, or SSM is checked into the model directory.

## Analyses

- `baseline :> Analysis`
- Scenario set: `ScenarioSet`
- Experiment: `startTime=0.0`, `stopTime=1.0`, `stepSize=0.001`
- Tolerance is not part of the experiment; it comes from the FMU model
  descriptions.
- Artifacts: `artifacts/analyses/signal_nested_external_bindings/baseline/`
- Analyses are never exported as SSPs.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim

OMSimulator is not registered for this fixture: it fails to instantiate the
stack's emitted content with the same duplicate root-scope connector it hits on
`signal_nested_pass_through` (DD-014/DD-016). ssp4sim applies the inline
component parameters correctly.

## Structure

- `Step` (inline)
- `Inner`: `sine.y -> y`
- Root output: `step.y -> y`
- All wiring, including the boundary connections, is authored in SysML.

## Strategy Role

- Composite SSP fixture.
- Nested external-binding coverage.

## Intent

- Validate an external parameter binding placed on a nested system.

## Expected Behavior

- `sine.y = offset + amplitude * sin(2*pi*f*t)`.

## Main Failures This Catches

- Nested external binding ignored.
- Mapping applied at the wrong level.

## Simulation Notes

- The build packages the `ScenarioSet` scenario into the exported SSP in the
  fixture's parameter form.
- The runtime runs the built SSP as-is; it does not inject a scenario.
- Form: external SSV+SSM binding on the nested system; step inline.

## Packaging Notes

- Exported model: `artifacts/models/signal_nested_external_bindings/baseline/model/`
- Analysis artifacts: `artifacts/analyses/signal_nested_external_bindings/baseline/`
- FMU sources:
- `models/fmu/Modelica.Blocks.Sources.Step/fmu`
- `models/fmu/Modelica.Blocks.Sources.Sine/fmu`
- Build: `python3 scripts/build_models.py run signal_nested_external_bindings`

## Typical Use

- Nested parameter-form regression checks.
