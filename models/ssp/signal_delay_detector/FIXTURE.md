# signal_delay_detector

## Origin

Assembled from shared Modelica FMUs. The model and analysis are authored in SysML
under `architecture/`.

## Overview

`signal_delay_detector` is a deterministic signal-propagation SSP fixture built from shared
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
- Artifacts: `artifacts/analyses/signal_delay_detector/baseline/`
- Analyses are never exported as SSPs.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- OMSimulator

## Structure

- `Step -> Gain_a -> Gain_b -> Add.u1`
- `Step -> Add.u2`

## Strategy Role

- Deterministic signal-propagation fixture.
- Priority 3 propagation test.
- Ordering and delay reproducer.

## Intent

- Make one-step delay and ordering errors easy to detect by comparing a direct path with a transformed path.

## Expected Behavior

- Both paths stay aligned in time according to the declared algebraic relationship.

## Main Failures This Catches

- Hidden one-step delay.
- Wrong topological ordering.
- Incorrect feedthrough across a chain.

## Simulation Notes

- The build packages the `ScenarioSet` scenario into the exported SSP in the
  fixture's parameter form.
- The runtime runs the built SSP as-is; it does not inject a scenario.
- Form: external target-named SSV, no mapping.

## Packaging Notes

- Exported model: `artifacts/models/signal_delay_detector/baseline/model/`
- Analysis artifacts: `artifacts/analyses/signal_delay_detector/baseline/`
- FMU sources:
- `models/fmu/Modelica.Blocks.Sources.Step/fmu`
- `models/fmu/Modelica.Blocks.Math.Gain/fmu`
- `models/fmu/Modelica.Blocks.Math.Add/fmu`
- Build: `python3 scripts/build_models.py run signal_delay_detector`

## Typical Use

- Tight-tolerance cross-engine comparison.
- Regression testing for ordering and delay.
