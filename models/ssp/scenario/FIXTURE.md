# scenario

## Origin

Authored SSP fixture in `models/ssp/scenario/ssp` built around local scenario
FMU resources.

## Overview

`scenario` is a small single-FMU SSP that can generate source data from a
parameter definition.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- OMSimulator
- FMPy

## Strategy Role

- Test SSV, SSM and parameter setting in an SSP context.
- Provides a minimal scenario for validating external-parameter handling.

## Main Failures This Catches

- Larger-system signal exchange issues.
- SSV and SSM parsing problems.

## Typical Use

- Validating engine behavior on SSV and SSM parameter parsing.