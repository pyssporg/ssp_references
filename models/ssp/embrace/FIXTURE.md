# embrace

## Origin

Authored SSP fixture in `models/ssp/embrace/ssp` built around local component
FMUs, SSP parameters, and `CONOPS.csv`.

## Overview

`embrace` is a larger composite SSP fixture representing a more realistic,
resource-heavy orchestration case.

## Strategy Role

- Composite SSP model.
- Pre-merge comparison candidate.
- Regression anchor for larger-system orchestration behavior.

## Main Risks Covered

- Larger-system signal exchange.
- Resource-heavy packaging and loading.
- Orchestration and scheduling behavior in realistic composite models.

## Typical Use

- Validating engine behavior on larger coupled systems where signal routing and
  setup complexity are both important.
