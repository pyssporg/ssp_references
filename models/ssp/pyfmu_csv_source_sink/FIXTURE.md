# pyfmu_csv_source_sink

## Origin

Assembled locally from `input/signals.csv`, a generated `CsvSource` FMU, and
the shared `models/fmu/Modelica.Blocks.Math.Gain` fixture. The `CsvSource` FMU
is built by `pyfmu_csv` during the fixture build and is not checked in under
`models/`.

## Overview

`pyfmu_csv_source_sink` is a minimal SSP assembled from a `pyfmu_csv` source
FMU and a shared Modelica block sink FMU.

## Architecture Source

- `architecture/pyfmu_csv_source_sink.sysml`
- Exportable composition: `System :> SspModel`
- No legacy SSD, SSV, or SSM is checked into the model directory.
- `CsvSourceFmu` deliberately has no `fmu_meta.source`: the composition is
  exported as a design structure and populated with the generated FMU.

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

## Packaging Notes

- `build.py` exports the structure with `--allow-missing-fmus`, generates
  `CsvSource.fmu` from `input/signals.csv`, and attaches it with
  `SSP.attach_fmu`, which checks the SSD connectors and implementation against
  the FMU.
- `experiments.xml` supplies the baseline window and tolerance and is packaged
  as LS-REF metadata.
