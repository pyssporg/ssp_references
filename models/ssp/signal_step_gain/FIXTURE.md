# signal_step_gain

## Origin

Assembled from the shared `models/fmu/Modelica.Blocks.Sources.Step` and
`models/fmu/Modelica.Blocks.Math.Gain` fixtures. The model and study are
authored in SysML at `architecture/signal_step_gain.sysml`.

## Overview

Deterministic signal-propagation fixture built from two shared Modelica FMUs
with external parameter interfaces and one study scenario.

## Architecture Source

- `architecture/signal_step_gain.sysml`
- Exportable composition: `System :> SspModel`
- Parameter interfaces: `StepParameters` (`height`, `offset`, `startTime`) and
  `GainParameters` (`k`)
- No legacy SSD, SSV, or SSM is checked into the model directory.

## Studies

- `test_baseline :> Study`
- Applies `ScenarioSet` (`height=2.0`, `offset=1.0`, `startTime=0.25`, `k=3.0`)
- Experiment: `startTime=0.0`, `stopTime=1.0`, `stepSize=0.001`,
  `tolerance=0.0001`
- Artifacts: `artifacts/studies/signal_step_gain/test_baseline/`
- Studies are never exported as SSPs.

## Strategy Role

- Deterministic signal-propagation fixture.
- Priority 1 propagation test.
- Minimal reproducer for direct algebraic feedthrough.

## Structure

```text
Step -> Gain
```

## Intent

Validate direct propagation of a stepped signal through a simple algebraic
transform while exercising SysML model export and runtime study injection.

## Expected Behavior

- Output equals input multiplied by a fixed gain.
- The output step occurs at the same communication step as the input step.

## Main Failures This Catches

- One-step propagation lag.
- Wrong gain parameter handling.
- Incorrect connector mapping.
- Missing runtime scenario injection.

## Simulation Notes

- Registered backends: `ssp4sim`, `omsimulator`, `fmpy`.
- The exported SSP carries parameter connectors and no scenario binding.
- Runtime copies the exported SSP, adds the study scenario, and leaves the
  exported artifact unchanged.

## Packaging Notes

- Exported model: `artifacts/models/signal_step_gain/model/`
- Study: `artifacts/studies/signal_step_gain/test_baseline/`
- FMU sources: `models/fmu/Modelica.Blocks.Sources.Step/fmu` and
  `models/fmu/Modelica.Blocks.Math.Gain/fmu`
- Build: `python3 models/ssp/signal_step_gain/build.py`

## Typical Use

- Tight-tolerance comparison tests.
- Debugging direct feedthrough or step-alignment issues.
- Regression test for the `SspModel`/`Study` boundary.
