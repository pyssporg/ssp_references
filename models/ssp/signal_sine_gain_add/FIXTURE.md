# signal_sine_gain_add

## Overview

`signal_sine_gain_add` is a planned deterministic signal-propagation SSP
fixture built from shared Modelica FMUs.

## Structure

- `Sine -> Gain`
- `Step -> Add`
- `Gain output + Step output -> Add output`

## Strategy Role

- Deterministic signal-propagation fixture.
- Priority 2 propagation test.

## Intent

- Validate a short transformation chain with mixed source types.

## Expected Behavior

- Output equals `gain * sine + step`.

## Main Failures This Catches

- Drift in chained propagation.
- Wrong evaluation order in multi-stage networks.
- Loss of amplitude or offset across multiple components.
