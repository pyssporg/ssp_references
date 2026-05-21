# signal_sine_gain_add

## Origin

Assembled from the shared `models/fmu/Modelica.Blocks.Sources.Sine`,
`models/fmu/Modelica.Blocks.Sources.Step`,
`models/fmu/Modelica.Blocks.Math.Gain`, and
`models/fmu/Modelica.Blocks.Math.Add` fixtures.

## Overview

`signal_sine_gain_add` is a deterministic signal-propagation SSP fixture built
from shared Modelica FMUs with an inline system-level regression parameter set.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- OMSimulator
- FMPy

## Structure

- `Sine -> Gain`
- `Step -> Add`
- `Gain output + Step output -> Add output`

## Strategy Role

- Deterministic signal-propagation fixture.
- Priority 2 propagation test.
- Internal regression anchor for inline parameter packaging.

## Intent

- Validate a short transformation chain with mixed source types.

## Expected Behavior

- Output equals `gain * sine + step`.

## Main Failures This Catches

- Drift in chained propagation.
- Wrong evaluation order in multi-stage networks.
- Loss of amplitude or offset across multiple components.
