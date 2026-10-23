# BouncingBall

## Origin

Packaged from the shared `models/fmu/BouncingBall` reference FMU fixture and its
CSV baselines. The model and study are authored in SysML at
`architecture/BouncingBall.sysml`.

## Overview

`BouncingBall` is a simple reference SSP fixture used for fast behavioral
checks. It wraps the single FMI reference FMU with event-driven continuous
dynamics.

## Architecture Source

- `architecture/BouncingBall.sysml`
- Exportable composition: `System :> SspModel`
- Study composition: `baseline :> Study`
- Parameter interface: `BouncingBallParameters` exposes `g` and `e`. The study
  applies no scenario, so the FMU defaults (`g = -9.81`, `e = 0.7`) apply.
- No legacy SSD, SSV, or SSM is checked into the model directory.

## Studies

- `baseline :> Study`
- Scenario set: none; the build packages no scenario.
- Experiment: `startTime=0.0`, `stopTime=3.0`, `stepSize=0.001`
- Tolerance is not part of the experiment; it comes from the FMU model
  descriptions.
- Artifacts: `artifacts/studies/BouncingBall/baseline/`
- Studies are never exported as SSPs.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- OMSimulator

## Structure

- Single component `fmu : BouncingBall` with outputs `h` and `v` and parameter
  connectors `g` and `e`.

## Strategy Role

- Simple reference model.
- Smoke-test candidate.
- Cross-engine behavioral comparison baseline.

## Intent

- Exercise event handling and discontinuities inside a single packaged FMU.

## Expected Behavior

- `h` falls under gravity and rebounds with coefficient `e` until it settles;
  `v` follows the corresponding velocity trajectory.

## Main Failures This Catches

- Event handling and discontinuities.
- Result export correctness.
- Basic FMI/SSP runtime integration.

## Simulation Notes

- The build packages no scenario; the FMU defaults apply.
- The runtime runs the built SSP as-is; it does not inject a scenario.
- OMSimulator is known to miss bounce events for this fixture, so the
  engine-to-engine gate reports `fail`; that is expected and documented.

## Packaging Notes

- Exported model: `artifacts/models/BouncingBall/baseline/model/`
- Study artifacts: `artifacts/studies/BouncingBall/baseline/`
- FMU source: `models/fmu/BouncingBall/fmu`
- The build skips FMU validation: the shared FMU declares both `ModelExchange`
  and `CoSimulation`, while the FMI 2 reader keeps only the first interface and
  would reject the `CoSimulation` component.
- Build: `python3 scripts/build_models.py run BouncingBall`

## Typical Use

- Fast regression checks.
- Comparing event timing and overall trajectory shape across engines.
