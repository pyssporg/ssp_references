# pyfmu_csv_source_sink

## Origin

Assembled locally from `input/signals.csv`, a generated `CsvSource` FMU, and
the shared `models/fmu/Modelica.Blocks.Math.Gain` fixture. The `CsvSource` FMU
is built by `pyfmu_csv` during the fixture build and is not checked in under
`models/`.

## Overview

`pyfmu_csv_source_sink` is a minimal SSP assembled from a `pyfmu_csv` source
FMU and a shared Modelica block sink FMU. Parameter form: external SSV with an
inline mapping.

## Architecture Source

- `architecture/pyfmu_csv_source_sink.sysml`
- Exportable composition: `System :> SspModel`
- Study composition: `baseline :> Study`
- No legacy SSD, SSV, SSM, or `experiments.xml` is checked into the model
  directory.
- `CsvSourceFmu` deliberately has no `fmu_meta.source`: the composition is
  exported with an empty `source` on the `source` component, and the build
  attaches the generated FMU to the built artifact afterwards.

## Studies

- `baseline :> Study`
- Experiment: `startTime=0.0`, `stopTime=1.0`, `stepSize=0.001`
- `System` owns `ScenarioSet`; `ScenarioSet.k = 1.0` maps to `sink.k`.
- The study is experiment-only; it applies no scenario set.
- Tolerance is not part of the experiment; it comes from the composed FMUs.
- Artifacts: `artifacts/studies/pyfmu_csv_source_sink/baseline/`
- Studies are never exported as SSPs.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim

## Strategy Role

- Exercise packaging a CSV-backed source FMU into an SSP.
- Provide a small source-to-sink wiring fixture for regression coverage.

## Structure

- `source.y -> sink.u`

## Intent

- Exercise packaging a CSV-backed source FMU into an SSP.
- Provide a small source-to-sink wiring fixture.
- Keep the source CSV in the model directory instead of generating it in code.

## Simulation Notes

The sink is `Modelica.Blocks.Math.Gain` configured with `sink.k = 1.0`. Its
output is intentionally not mapped to a system connector in this fixture.

The source signal is defined by `input/signals.csv` in the model directory.
The study descriptor supplies the simulation window; the runtime runs the built
SSP as-is.

## Packaging Notes

- `build.py` exports the structure (the `source` component has an empty SSD
  `source`), generates `CsvSource.fmu` from `input/signals.csv`, and attaches
  it to the built artifact with `SSP.attach_fmu`.
- `generate ssp` packages `ScenarioSet` as
  `resources/parameter_sets/ScenarioSet.ssv` with an inline parameter mapping.
  The build adds no parameter set.
- `SSP.attach_fmu` checks the SSD connectors and implementation against the FMU.
- The attached FMU stays a `resources/CsvSource.fmu` archive rather than being
  unpacked into `resources/CsvSource/` like the prebuilt FMUs. Engines accept
  it, but the artifact shape is inconsistent; revisit if attached FMUs need the
  same extraction and model-exchange stripping as exported ones.
- No LS-REF `experiments.xml` is packaged; the study descriptor is the window
  source.
- Exported model: `artifacts/models/pyfmu_csv_source_sink/baseline/model/`
- Study artifacts: `artifacts/studies/pyfmu_csv_source_sink/baseline/`
- Build: `python3 scripts/build_models.py run pyfmu_csv_source_sink`
