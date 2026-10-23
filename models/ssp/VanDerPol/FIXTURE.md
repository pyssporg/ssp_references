# VanDerPol

## Origin

Packaged from the shared `models/fmu/VanDerPol` reference FMU fixture and its
CSV baselines. The model and studies are authored in SysML at
`architecture/VanDerPol.sysml`.

## Overview

`VanDerPol` is a simple reference SSP fixture used to validate continuous
nonlinear dynamics. It wraps the Van der Pol oscillator as a single FMI
reference FMU and exposes two studies over the `mu` parameter.

## Architecture Source

- `architecture/VanDerPol.sysml`
- Exportable composition: `System :> SspModel`
- Study compositions: `baseline :> Study`, `fast :> Study`
- Parameter interface: `VanDerPolParameters` exposes `mu`.
- No legacy SSD, SSV, or SSM is checked into the model directory.

## Studies

- `baseline :> Study`
  - Scenario set: none; the FMU default `mu = 1.0` applies.
  - Experiment: `startTime=0.0`, `stopTime=20.0`, `stepSize=0.001`
  - Artifacts: `artifacts/studies/VanDerPol/baseline/`
- `fast :> Study`
  - Scenario set: `FastScenario` with `mu = 2.0`.
  - Experiment: `startTime=0.0`, `stopTime=1.0`, `stepSize=0.001`
  - Artifacts: `artifacts/studies/VanDerPol/fast/`
- Tolerance is not part of the experiment; it comes from the FMU model
  descriptions.
- Studies are never exported as SSPs.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- OMSimulator
- FMPy

## Structure

- Single component `fmu : VanDerPol` with outputs `x0` and `x1` and parameter
  connector `mu`.

## Strategy Role

- Simple reference model.
- Behavioral comparison baseline.
- Regression anchor for continuous-time behavior.

## Intent

- Exercise smooth nonlinear dynamics and a parameter-dependent study variant.

## Expected Behavior

- `x0` and `x1` follow the limit-cycle trajectory for the selected `mu`; the
  fast study converges to the same cycle over a shorter window.

## Main Failures This Catches

- Continuous dynamics handling.
- Solver consistency across engines.
- Numerical drift or integration regressions.
- Parameter packaging for a study variant.

## Simulation Notes

- The baseline packages no scenario; the fast study packages `FastScenario` as
  a root external SSV+SSM binding.
- The runtime runs the built SSP as-is; it does not inject a scenario.
- All registered backends agree within the gate tolerance on both studies.

## Packaging Notes

- Exported models: `artifacts/models/VanDerPol/baseline/model/` and
  `artifacts/models/VanDerPol/fast/model/`
- Study artifacts: `artifacts/studies/VanDerPol/baseline/` and
  `artifacts/studies/VanDerPol/fast/`
- FMU source: `models/fmu/VanDerPol/fmu`
- The build skips FMU validation: the shared FMU declares both `ModelExchange`
  and `CoSimulation`, while the FMI 2 reader keeps only the first interface and
  would reject the `CoSimulation` component.
- Build: `python3 scripts/build_models.py run VanDerPol`

## Typical Use

- Fast cross-engine comparison for continuous models.
- Detecting changes in smooth nonlinear trajectories.
