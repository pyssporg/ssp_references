# VanDerPol

## Origin

Packaged from the shared `models/fmu/VanDerPol` reference FMU fixture and its
CSV baselines.

## Overview

`VanDerPol` is a simple reference SSP fixture used to validate continuous
nonlinear dynamics.

## Strategy Role

- Simple reference model.
- Behavioral comparison baseline.
- Regression anchor for continuous-time behavior.

## Main Risks Covered

- Continuous dynamics handling.
- Solver consistency across engines.
- Numerical drift or integration regressions.

## Typical Use

- Fast cross-engine comparison for continuous models.
- Detecting changes in smooth nonlinear trajectories.

## Packaging Note

This fixture carries a small `experiments.xml` bundle so the builder can
materialize the baseline SSP variants.

- `resources/` holds the parameter SSV and SSM files.
- `references/` holds the reference CSV baselines.
- `baseline` runs with `mu = 1.0`.
- `fast` runs with `mu = 2.0`.

The build step packages the parameter resources into the SSP `resources/`
directory and stores the experiment XML plus reference CSVs under
`extra/org.fmi-standard.fmi-ls-ref/`.
