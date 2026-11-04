# Stair

## Origin

Packaged from the shared `models/fmu/Stair` reference FMU fixture and its CSV
baselines. The model and analysis are authored in SysML at
`architecture/Stair.sysml`.

## Overview

`Stair` is a simple reference SSP fixture focused on stepped or event-driven
behavior. It wraps the single FMI reference FMU with an integer counter output.

## Architecture Source

- `architecture/Stair.sysml`
- Exportable composition: `System :> SspModel`
- Analysis composition: `baseline :> Analysis`
- No parameter interfaces or parameter sets; the FMU has no tunable variables.
- No legacy SSD, SSV, or SSM is checked into the model directory.

## Analyses

- `baseline :> Analysis`
- Scenario set: none; the build packages no scenario.
- Experiment: `startTime=0.0`, `stopTime=9.0`, `stepSize=0.2`
- Tolerance is not part of the experiment; it comes from the FMU model
  descriptions.
- Artifacts: `artifacts/analyses/Stair/baseline/`
- Analyses are never exported as SSPs.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- OMSimulator

## Structure

- Single component `fmu : Stair` with integer output `counter`.

## Strategy Role

- Simple reference model.
- Smoke-test candidate.
- Behavioral comparison baseline for time events.

## Intent

- Exercise time-event handling and integer output export.

## Expected Behavior

- `counter` changes on the FMU's time-event schedule and stays constant between
  events.

## Main Failures This Catches

- Time-event handling.
- Step transition timing.
- Discrete or event-driven response consistency.

## Simulation Notes

- The build packages no scenario; the FMU has no tunable variables.
- The runtime runs the built SSP as-is; it does not inject a scenario.

## Packaging Notes

- Exported model: `artifacts/models/Stair/baseline/model/`
- Analysis artifacts: `artifacts/analyses/Stair/baseline/`
- FMU source: `models/fmu/Stair/fmu`
- The build skips FMU validation: the shared FMU declares both `ModelExchange`
  and `CoSimulation`, while the FMI 2 reader keeps only the first interface and
  would reject the `CoSimulation` component.
- Build: `python3 scripts/build_models.py run Stair`

## Typical Use

- Checking whether engines align on event timing and output transitions.
