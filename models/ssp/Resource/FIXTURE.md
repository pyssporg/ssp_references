# Resource

## Origin

Packaged from the shared `models/fmu/Resource` reference FMU fixture. The model
and study are authored in SysML at `architecture/Resource.sysml`.

## Overview

`Resource` is a simple reference SSP fixture used to validate FMU resource
handling inside an SSP. The single component exposes a constant integer output
loaded from a bundled resource file.

## Architecture Source

- `architecture/Resource.sysml`
- Exportable composition: `System :> SspModel`
- Study composition: `baseline :> Study`
- No parameter interfaces or parameter sets; the FMU has no tunable variables.
- No legacy SSD, SSV, or SSM is checked into the model directory.

## Studies

- `baseline :> Study`
- Scenario set: none; the build packages no scenario.
- Experiment: `startTime=0.0`, `stopTime=1.0`, `stepSize=0.001`
- Tolerance is not part of the experiment; it comes from the FMU model
  descriptions.
- Artifacts: `artifacts/studies/Resource/baseline/`
- Studies are never exported as SSPs.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- OMSimulator

## Structure

- Single component `fmu : Resource` with output connector `y`.

## Strategy Role

- Simple reference model.
- Packaging and runtime integration check.

## Intent

- Validate that an engine resolves files bundled inside an FMU's `resources/`
  directory after the FMU is packaged in an SSP.

## Expected Behavior

- `y` stays constant at the value read from `resources/y.txt` (97) for the whole
  simulation window.

## Main Failures This Catches

- FMU resource loading.
- Packaged SSP resource resolution.
- Runtime failures caused by missing bundled files.

## Simulation Notes

- `y` is constant, so engine-to-engine comparison reports a degenerate signal
  and an `invalid` gate; this is expected for this fixture.
- The runtime runs the built SSP as-is; it does not inject a scenario.

## Packaging Notes

- Exported model: `artifacts/models/Resource/baseline/model/`
- Study artifacts: `artifacts/studies/Resource/baseline/`
- FMU source: `models/fmu/Resource/fmu`
- The build skips FMU validation: the shared FMU declares both
  `ModelExchange` and `CoSimulation`, while the FMI 2 reader keeps only the
  first interface and would reject the `CoSimulation` component.
- Build: `python3 scripts/build_models.py run Resource`

## Typical Use

- Verifying that engines can execute resource-dependent FMUs after SSP
  packaging.
