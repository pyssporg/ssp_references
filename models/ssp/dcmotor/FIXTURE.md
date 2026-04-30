# dcmotor

## Origin

Authored SSP fixture in `models/ssp/dcmotor/ssp` built around local component
FMUs and nested resources.

## Overview

`dcmotor` is a composite SSP fixture with multiple interacting FMUs.

## Strategy Role

- Composite SSP model.
- Pre-merge comparison candidate.
- Regression anchor for coupled execution behavior.

## Main Risks Covered

- Multi-component signal exchange.
- Routing and coupling behavior.
- Orchestration issues not visible in single-FMU models.

## Typical Use

- Validating realistic coupled execution.
- Checking that engine changes do not break composite SSP handling.
