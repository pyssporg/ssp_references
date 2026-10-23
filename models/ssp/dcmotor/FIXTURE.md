# dcmotor

## Origin

Authored SSP fixture in `models/ssp/dcmotor/ssp` built around local component
FMUs and nested resources.

## Overview

`dcmotor` is a composite SSP fixture with multiple interacting FMUs. The
checked-in build output is flattened for `ssp4sim`, and the bundled FMUs are
written without `ModelExchange` sections so engines must use co-simulation.

## Architecture Source

- Legacy model body: `ssp/SystemStructure.ssd` and `ssp/resources/`.
- Authored study: `architecture/dcmotor.sysml`.
- `DcMotorModel.ssp_meta.source = "models/ssp/dcmotor/ssp"` selects the body.
- The SysML `DcMotorModel :> SspModel` composition is a boundary marker only;
  it declares no parts, connectors, or FMU metadata. The hierarchy stays in the
  checked-in SSD and is not exported from SysML.
- No legacy `experiments.xml` is checked in; the study supplies the experiment.

## Studies

- `baseline :> Study`
- Experiment: `startTime=0.0`, `stopTime=1.0`, `stepSize=0.001`.
- The study applies no scenario parameter set, so it produces only
  `study.json`; the model's own inline parameter sets stay in the SSD.
- Tolerance is not part of the experiment; the FMUs declare it in their
  `DefaultExperiment`.
- Artifacts: `artifacts/studies/dcmotor/baseline/`
- Studies are never exported as SSPs.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- OMSimulator

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
