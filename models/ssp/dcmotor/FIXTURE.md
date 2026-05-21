# dcmotor

## Origin

Authored SSP fixture in `models/ssp/dcmotor/ssp` built around local component
FMUs and nested resources.

## Overview

`dcmotor` is a composite SSP fixture with multiple interacting FMUs. The
checked-in build output is flattened for `ssp4sim`, and the bundled FMUs are
written without `ModelExchange` sections so engines must use co-simulation.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- OMSimulator
- FMPy

## Strategy Role

- Composite SSP model.
- Pre-merge comparison candidate.
- Regression anchor for coupled execution behavior.

## Main Failures This Catches

- Multi-component signal exchange.
- Routing and coupling behavior.
- Orchestration issues not visible in single-FMU models.

## Typical Use

- Validating realistic coupled execution.
- Checking that engine changes do not break composite SSP handling.
