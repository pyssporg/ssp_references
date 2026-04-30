# BouncingBall

## Origin

Packaged from the shared `models/fmu/BouncingBall` reference FMU fixture and
its CSV baselines.

## Overview

`BouncingBall` is a simple reference SSP fixture used for fast behavioral
checks.

## Strategy Role

- Simple reference model.
- Smoke-test candidate.
- Cross-engine behavioral comparison baseline.

## Main Risks Covered

- Event handling and discontinuities.
- Result export correctness.
- Basic FMI/SSP runtime integration.

## Typical Use

- Fast regression checks.
- Comparing event timing and overall trajectory shape across engines.
