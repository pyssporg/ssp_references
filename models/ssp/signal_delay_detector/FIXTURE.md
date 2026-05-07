# signal_delay_detector

## Origin

Assembled from the shared `models/fmu/Modelica.Blocks.Sources.Step`,
`models/fmu/Modelica.Blocks.Math.Gain`, and `models/fmu/Modelica.Blocks.Math.Add`
fixtures.

The parameter values are stored in
`models/ssp/signal_delay_detector/ssp/resources/signal_delay_detector_parameters.ssv`
and linked during the SSP build.

## Overview

`signal_delay_detector` is a deterministic signal-propagation SSP fixture
designed to expose subtle ordering and delay issues.

## Structure

- `Step -> Gain -> Gain -> Add`
- Parallel direct path from `Step -> Add`

## Strategy Role

- Deterministic signal-propagation fixture.
- Priority 3 propagation test.
- Implemented regression fixture.

## Intent

- Make one-step delay and ordering errors easy to detect by comparing a direct
  path with a transformed path.

## Expected Behavior

- Both paths remain aligned in time according to the declared algebraic
  relationship.

## Main Failures This Catches

- Hidden one-step delay.
- Wrong topological ordering.
- Incorrect handling of algebraic feedthrough across a chain.

## Current Runtime Note

The current co-simulation runtime still aborts on this fixture at the first
`Step` discontinuity (`t = 0.25`). The FMU logs
`fmi2GetContinuousStates: Invalid argument states[] = NULL` from its internal
continuous-state helper during `doStep`.

That failure comes from the FMU/runtime interaction, not from the SSP package
layout. The fixture remains useful as a regression detector because it makes
the ordering and event-boundary problem visible immediately.
