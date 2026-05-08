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
