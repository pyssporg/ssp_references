# signal_nested_algebraic_loop

## Origin

Assembled from the shared `models/fmu/Modelica.Blocks.Sources.Sine`,
`models/fmu/Modelica.Blocks.Math.Gain`, and
`models/fmu/Modelica.Blocks.Math.Add` fixtures.

The parameter values are stored in
`models/ssp/signal_nested_algebraic_loop/ssp/resources/signal_nested_algebraic_loop_parameters.ssv`
and linked during the SSP build.

## Overview

`signal_nested_algebraic_loop` is a deterministic signal-propagation SSP
fixture that nests one algebraic loop inside another.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- OMSimulator

## Strategy Role

- Deterministic signal-propagation fixture.
- Behavioral comparison target.
- Regression anchor for nested loop resolution.

## Structure

- `Sine -> Add_outer -> Gain_outer -> Add_outer`
- `Add_inner` feeds `Add_outer` so the inner loop sits inside the outer loop
- Inner loop: `Gain_outer -> Add_inner -> Gain_inner -> Add_inner`

## Intent

- Validate solver and scheduler handling when one closed loop depends on the
  solution of another closed loop.
- Catch regressions that only appear when a loop is resolved after an inner
  loop has already been fixed.

## Expected Behavior

- `sine.y` oscillates around a positive bias during the simulation window
- The 2 Hz excitation makes the curvature visible within the 1 second
  experiment window while keeping the loop outputs away from zero
- `add_outer.y = 2 * sine.y`
- `add_inner.y = sine.y`
- `gain_outer.y = 0.5 * sine.y`
- `gain_inner.y = 0.5 * sine.y`
- The fixed point is simple to state, and the comparison artifacts show how
  each backend resolves the nested feedback paths.

## Main Failures This Catches

- Failure to converge when loop resolution is nested.
- Incorrect propagation between inner and outer feedback paths.
- Evaluation-order bugs that are invisible in a single closed loop.

## Packaging Notes

- Uses a checked-in external SSV with the sine and gain parameters.
- The source FMUs are Modelica-generated and expose `ModelStructure`
  dependency metadata in `modelDescription.xml`.
- `FMPy` is intentionally excluded here because it does not resolve the
  nested loop into a bounded trace on this fixture.

## Typical Use

- Tight-tolerance cross-engine comparison.
- Regression testing for nested algebraic-loop handling.
