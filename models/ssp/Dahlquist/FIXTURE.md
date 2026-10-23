# Dahlquist

## Origin

Packaged from the shared `models/fmu/Dahlquist` reference FMU fixture and its
CSV baselines. The model and study are authored in SysML at
`architecture/Dahlquist.sysml`.

## Overview

`Dahlquist` is a simple reference SSP fixture for basic integration behavior. It
wraps the Dahlquist test equation as a single FMI reference FMU.

## Architecture Source

- `architecture/Dahlquist.sysml`
- Exportable composition: `System :> SspModel`
- Study composition: `baseline :> Study`
- Parameter interface: `DahlquistParameters` exposes `k`. The study applies no
  scenario, so the FMU default (`k = 1.0`) applies.
- No legacy SSD, SSV, or SSM is checked into the model directory.

## Studies

- `baseline :> Study`
- Scenario set: none; the build packages no scenario.
- Experiment: `startTime=0.0`, `stopTime=10.0`, `stepSize=0.001`
- Tolerance is not part of the experiment; it comes from the FMU model
  descriptions.
- Artifacts: `artifacts/studies/Dahlquist/baseline/`
- Studies are never exported as SSPs.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- OMSimulator
- FMPy

## Structure

- Single component `fmu : Dahlquist` with output `x` and parameter connector
  `k`.

## Strategy Role

- Simple reference model.
- Behavioral comparison baseline.
- Regression anchor for numerical stability checks.

## Intent

- Exercise a well-understood exponential decay so solver and integration
  differences show up clearly.

## Expected Behavior

- `x` decays exponentially from its initial value according to the Dahlquist
  test equation.

## Main Failures This Catches

- Basic integration behavior.
- Numerical stability.
- Sensitivity to solver or step-size changes.

## Simulation Notes

- The build packages no scenario; the FMU default applies.
- The runtime runs the built SSP as-is; it does not inject a scenario.

## Packaging Notes

- Exported model: `artifacts/models/Dahlquist/baseline/model/`
- Study artifacts: `artifacts/studies/Dahlquist/baseline/`
- FMU source: `models/fmu/Dahlquist/fmu`
- The build skips FMU validation: the shared FMU declares both `ModelExchange`
  and `CoSimulation`, while the FMI 2 reader keeps only the first interface and
  would reject the `CoSimulation` component.
- Build: `python3 scripts/build_models.py run Dahlquist`

## Typical Use

- Fast sanity checks for deterministic continuous behavior.
- Tracking unintended changes in simple exponential-like trajectories.
