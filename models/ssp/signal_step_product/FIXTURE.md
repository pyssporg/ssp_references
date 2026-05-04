# signal_step_product

## Origin

Assembled from the shared `models/fmu/Modelica.Blocks.Sources.Step`,
`models/fmu/Modelica.Blocks.Sources.Sine`, and
`models/fmu/Modelica.Blocks.Math.Product` fixtures.

The external parameter set and mapping are created during the build step and
then linked into the SSP archive.

## Overview

`signal_step_product` is a deterministic signal-propagation SSP fixture built
from shared Modelica FMUs with build-generated external parameter packaging.

## Structure

- `Step * Sine -> Product`

## Strategy Role

- Deterministic signal-propagation fixture.
- Priority 2 propagation test.
- Implemented regression fixture.

## Intent

- Validate deterministic gating behavior through a multiplicative block.

## Expected Behavior

- Output is zero before the step activates.
- Output follows the sine signal scaled by the step level after activation.

## Main Failures This Catches

- Wrong time alignment between inputs.
- Incorrect product input wiring.
- Step-boundary ordering issues.
