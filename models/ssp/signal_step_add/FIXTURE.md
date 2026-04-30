# signal_step_add

## Origin

Assembled from the shared `models/fmu/Modelica.Blocks.Sources.Step` and
`models/fmu/Modelica.Blocks.Math.Add` fixtures.

## Overview

`signal_step_add` is a deterministic signal-propagation SSP fixture built from
shared Modelica FMUs.

## Structure

- `Step + Step -> Add`

## Strategy Role

- Deterministic signal-propagation fixture.
- Priority 1 propagation test.
- Minimal reproducer for fan-in behavior.

## Intent

- Validate deterministic fan-in behavior and algebraic summation.

## Expected Behavior

- Output equals the exact sum of both source signals at every recorded step.

## Main Failures This Catches

- Incorrect handling of multiple incoming signals.
- Wrong input ordering or connector binding.
- Missed update on one input during a communication step.

## Typical Use

- Tight-tolerance comparison tests.
- Debugging connector binding and multi-input update behavior.
