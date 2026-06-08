# signal_algebraic_loop

## Origin

Assembled from the shared `models/fmu/Modelica.Blocks.Sources.Sine`,
`models/fmu/Modelica.Blocks.Math.Gain`, and
`models/fmu/Modelica.Blocks.Math.Add` fixtures.

The parameter values are stored in
`models/ssp/signal_algebraic_loop/ssp/resources/signal_algebraic_loop_parameters.ssv`
and linked during the SSP build.

## Overview

`signal_algebraic_loop` is a deterministic signal-propagation SSP fixture that
closes one algebraic loop around a single gain/add pair.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- OMSimulator
- FMPy

## Strategy Role

- Deterministic signal-propagation fixture.
- Behavioral comparison target.
- Regression anchor for a single closed algebraic loop.

## Structure

- `Sine -> Add -> Gain -> Add`
- Feedback path: `Add.y -> Gain.u -> Add.u2`

## Intent

- Validate solver and scheduler handling when the system has one closed
  algebraic loop.
- Distinguish loop-resolution errors from acyclic feedthrough errors.

## Expected Behavior

- `sine.y` oscillates around zero during the simulation window
- The 2 Hz excitation makes the curvature visible within the 1 second
  experiment window
- `add.y = 2 * sine.y`
- `gain.y = sine.y`
- The fixed point is simple to state, and the comparison artifacts show how
  each backend resolves it.

## Main Failures This Catches

- Failure to solve a closed algebraic loop.
- Wrong fixed-point iteration or evaluation order.
- One-step lag in feedback propagation.

## Packaging Notes

- Uses a checked-in external SSV with the sine and gain parameters.
- The source FMUs are Modelica-generated and expose `ModelStructure`
  dependency metadata in `modelDescription.xml`.

## Typical Use

- Tight-tolerance cross-engine comparison.
- Regression testing for algebraic loop handling.
