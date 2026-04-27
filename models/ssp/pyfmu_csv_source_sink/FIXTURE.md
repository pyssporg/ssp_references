# pyfmu_csv_source_sink

## Overview

`pyfmu_csv_source_sink` is a minimal SSP assembled from a `pyfmu_csv` source
FMU and a shared Modelica block sink FMU.

## Structure

- `source.y -> sink.u`

## Inputs

- `input/signals.csv` defines the source signal exported by the generated
  source FMU.

## Intent

- Exercise packaging a CSV-backed source FMU into an SSP.
- Provide a small source-to-sink wiring fixture.
- Keep the source CSV in the model directory instead of generating it in code.

## Simulation Notes

The sink is `Modelica.Blocks.Math.Gain` configured with `sink.k = 1.0`. Its
output is intentionally not mapped to a system connector in this fixture.
