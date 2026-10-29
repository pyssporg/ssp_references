# VanDerPol

## Origin

Packaged from the shared `models/fmu/VanDerPol` reference FMU fixture and its
CSV baselines. The model and analyses are authored in SysML at
`architecture/VanDerPol.sysml`.

## Overview

`VanDerPol` is a simple reference SSP fixture used to validate continuous
nonlinear dynamics. It wraps the Van der Pol oscillator as a single FMI
reference FMU and exposes three analyses over the `mu` parameter.

## Architecture Source

- `architecture/VanDerPol.sysml`
- Exportable composition: `System :> SspModel`
- Analysis compositions: `baseline :> Analysis`, `fast :> Analysis`, `slow :> Analysis`
- Parameter interface: `VanDerPolParameters` exposes `mu`.
- No legacy SSD, SSV, or SSM is checked into the model directory.

## Analyses

- `baseline :> Analysis`
  - Scenario set: none; the FMU default `mu = 1.0` applies.
  - Experiment: `startTime=0.0`, `stopTime=20.0`, `stepSize=0.001`
  - Artifacts: `artifacts/analyses/VanDerPol/baseline/`
- `fast :> Analysis`
  - Scenario set: `FastScenario` with `mu = 2.0`.
  - Experiment: `startTime=0.0`, `stopTime=1.0`, `stepSize=0.001`
  - Artifacts: `artifacts/analyses/VanDerPol/fast/`
- `slow :> Analysis`
  - Scenario set: `SlowScenario` with `mu = 0.5`.
  - Experiment: `startTime=0.0`, `stopTime=20.0`, `stepSize=0.001`
  - Artifacts: `artifacts/analyses/VanDerPol/slow/`
- Tolerance is not part of the experiment; it comes from the FMU model
  descriptions.
- Analyses are never exported as SSPs.

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

- Exercise smooth nonlinear dynamics and multiple parameter-dependent analysis
  variants over one exported model.

## Expected Behavior

- `x0` and `x1` follow the limit-cycle trajectory for the selected `mu`; the
  fast analysis converges to the same cycle over a shorter window and the slow
  analysis uses a weaker nonlinearity over the baseline window.

## Main Failures This Catches

- Continuous dynamics handling.
- Solver consistency across engines.
- Numerical drift or integration regressions.
- Parameter packaging for an analysis variant.

## Simulation Notes

- The baseline packages no scenario; the fast and slow analyses package
  `FastScenario` and `SlowScenario` as root external SSV+SSM bindings.
- The runtime runs the built SSP as-is; it does not inject a scenario.
- All registered backends agree within the gate tolerance on all three analyses.

## Packaging Notes

- Exported models: `artifacts/models/VanDerPol/baseline/model/`,
  `artifacts/models/VanDerPol/fast/model/`, and
  `artifacts/models/VanDerPol/slow/model/`
- Analysis artifacts: `artifacts/analyses/VanDerPol/baseline/`,
  `artifacts/analyses/VanDerPol/fast/`, and `artifacts/analyses/VanDerPol/slow/`
- FMU source: `models/fmu/VanDerPol/fmu`
- The build skips FMU validation: the shared FMU declares both `ModelExchange`
  and `CoSimulation`, while the FMI 2 reader keeps only the first interface and
  would reject the `CoSimulation` component.
- Build: `python3 scripts/build_models.py run VanDerPol`

## Typical Use

- Fast cross-engine comparison for continuous models.
- Detecting changes in smooth nonlinear trajectories.
