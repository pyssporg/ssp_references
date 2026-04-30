# signal_step_gain

## Origin

Assembled from the shared `models/fmu/Modelica.Blocks.Sources.Step` and
`models/fmu/Modelica.Blocks.Math.Gain` fixtures.

## Overview

`signal_step_gain` is a deterministic signal-propagation SSP fixture built from
shared Modelica FMUs.

## Structure

- `Step -> Gain`

## Strategy Role

- Deterministic signal-propagation fixture.
- Priority 1 propagation test.
- Minimal reproducer for direct algebraic feedthrough.

## Intent

- Validate direct propagation of a stepped signal through a simple algebraic
  transform.

## Expected Behavior

- Output equals input multiplied by a fixed gain.
- The output step occurs at the same communication step as the input step.

## Main Failures This Catches

- One-step propagation lag.
- Wrong gain parameter handling.
- Incorrect connector mapping.

## Typical Use

- Tight-tolerance comparison tests.
- Debugging direct feedthrough or step-alignment issues.
