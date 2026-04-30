# signal_step_product

## Origin

Assembled from the shared `models/fmu/Modelica.Blocks.Sources.Step`,
`models/fmu/Modelica.Blocks.Sources.Sine`, and
`models/fmu/Modelica.Blocks.Math.Product` fixtures.

## Overview

`signal_step_product` is a planned deterministic signal-propagation SSP
fixture built from shared Modelica FMUs.

## Structure

- `Step * Sine -> Product`

## Strategy Role

- Deterministic signal-propagation fixture.
- Priority 2 propagation test.

## Intent

- Validate deterministic gating behavior through a multiplicative block.

## Expected Behavior

- Output is zero before the step activates.
- Output follows the sine signal scaled by the step level after activation.

## Main Failures This Catches

- Wrong time alignment between inputs.
- Incorrect product input wiring.
- Step-boundary ordering issues.
