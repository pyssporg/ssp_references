# embrace

## Origin

Authored SSP fixture in `models/ssp/embrace/ssp` built around local component
FMUs, SSP parameters, and `CONOPS.csv`.

## Overview

`embrace` is a larger composite SSP fixture representing a more realistic,
resource-heavy orchestration case.

## Architecture Source

- Legacy model body: `ssp/SystemStructure.ssd` and `ssp/resources/`.
- Authored study: `architecture/embrace.sysml`.
- `EmbraceModel.ssp_meta.source = "models/ssp/embrace/ssp"` selects the body.
- The SysML `EmbraceModel :> SspModel` composition is a boundary marker only;
  it declares no parts, connectors, or FMU metadata. The hierarchy and the
  external SSV/SSM scenario stay in the checked-in SSD and resources, and are
  not exported from SysML.
- No legacy `experiments.xml` is checked in; the study supplies the experiment.

## Studies

- `baseline :> Study`
- Experiment: `startTime=0.0`, `stopTime=10.0`, `stepSize=0.01`.
- The study applies no scenario parameter set, so it produces only
  `study.json`; the model's packaged SSV/SSM scenario is unchanged.
- Tolerance is not part of the experiment; the FMUs declare it in their
  `DefaultExperiment`.
- Artifacts: `artifacts/studies/embrace/baseline/`
- Studies are never exported as SSPs.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- OMSimulator
- FMPy

## Strategy Role

- Composite SSP model.
- Pre-merge comparison candidate.
- Regression anchor for larger-system orchestration behavior.

## Main Failures This Catches

- Larger-system signal exchange.
- Resource-heavy packaging and loading.
- Orchestration and scheduling behavior in realistic composite models.

## Typical Use

- Validating engine behavior on larger coupled systems where signal routing and
  setup complexity are both important.

## Engine-Specific Notes

The OMSimulator backend for this fixture is run with a reduced logging and
eventing setup to keep the result file manageable and to tolerate the model's
initial unknowns:

- `--ignoreInitialUnknowns=true`
- `--wallTime=true`
- `--emitEvents=false`
- `--inputExtrapolation=true`
