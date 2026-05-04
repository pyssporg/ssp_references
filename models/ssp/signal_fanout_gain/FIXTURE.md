# signal_fanout_gain

## Origin

Assembled from the shared `models/fmu/Modelica.Blocks.Sources.Step` and
`models/fmu/Modelica.Blocks.Math.Gain` fixtures.

The parameter values are stored in
`models/ssp/signal_fanout_gain/ssp/resources/signal_fanout_gain_parameters.ssv`
and linked during the SSP build.

## Overview

`signal_fanout_gain` is a deterministic signal-propagation SSP fixture built
from shared Modelica FMUs with an external system-level parameter set.

## Structure

- `Step -> Gain A`
- `Step -> Gain B`

## Strategy Role

- Deterministic signal-propagation fixture.
- Priority 1 propagation test.
- Minimal reproducer for fan-out behavior.

## Intent

- Validate fan-out from one source to multiple downstream consumers.

## Expected Behavior

- Both outputs track the same source timing, but with their own gain factors.

## Main Failures This Catches

- Inconsistent propagation to multiple receivers.
- Partial update behavior within the same communication step.
- Incorrect duplication of source signals across connectors.

## Typical Use

- Tight-tolerance comparison tests.
- Debugging branch consistency and repeated propagation within one step.
