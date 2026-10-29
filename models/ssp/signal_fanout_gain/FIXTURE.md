# signal_fanout_gain

## Origin

Assembled from shared Modelica FMUs. The model and analysis are authored in SysML
at `architecture/signal_fanout_gain.sysml`.

## Overview

`signal_fanout_gain` is a deterministic signal-propagation SSP fixture built from shared
Modelica FMUs. Parameter form: external target-named SSV, no mapping.

## Architecture Source

- `architecture/signal_fanout_gain.sysml`
- Exportable composition: `System :> SspModel`
- Analysis composition: `baseline :> Analysis`
- No legacy SSD, SSV, or SSM is checked into the model directory.

## Analyses

- `baseline :> Analysis`
- Scenario set: `ScenarioSet`
- Experiment: `startTime=0.0`, `stopTime=1.0`, `stepSize=0.001`
- Tolerance is not part of the experiment; it comes from the FMU model
  descriptions.
- Artifacts: `artifacts/analyses/signal_fanout_gain/baseline/`
- Analyses are never exported as SSPs.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- OMSimulator
- FMPy

## Structure

- `Step -> Gain A`
- `Step -> Gain B`

## Strategy Role

- Deterministic signal-propagation fixture.
- Priority 1 propagation test.
- Minimal reproducer for fan-out behavior.

## Intent

- Validate fan-out from one source to multiple downstream consumers.

## Expected Behavior

- Both outputs track the same source timing with their own gain factors.

## Main Failures This Catches

- Inconsistent propagation to multiple receivers.
- Partial update within one communication step.
- Incorrect duplication of source signals across connectors.

## Simulation Notes

- The build packages the `ScenarioSet` scenario into the exported SSP in the
  fixture's parameter form.
- The runtime runs the built SSP as-is; it does not inject a scenario.
- Form: external target-named SSV, no mapping.

## Packaging Notes

- Exported model: `artifacts/models/signal_fanout_gain/baseline/model/`
- Analysis artifacts: `artifacts/analyses/signal_fanout_gain/baseline/`
- FMU sources:
- `models/fmu/Modelica.Blocks.Sources.Step/fmu`
- `models/fmu/Modelica.Blocks.Math.Gain/fmu`
- Build: `python3 scripts/build_models.py run signal_fanout_gain`

## Typical Use

- Tight-tolerance comparison tests.
- Debugging branch consistency and repeated propagation within one step.
