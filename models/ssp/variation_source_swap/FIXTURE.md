# variation_source_swap

## Origin

Authored in this repository at `architecture/variation_source_swap.sysml`, adapted from the definition-level part-variation shape in `docs/breakdown/06-evolution/selected/examples/variation-points/01_structural_part_variation.sysml`. The Step and Sine FMUs are shared fixtures under `models/fmu/`; first added 2026-10-29 with the variation-point batch.

## Overview

One definition-level variation point, `SourceChoice`, offers two source FMUs as variant parts. `System.source : SourceChoice` is the only part; `System` has no root output port and no parameter bindings. Each study selects one variant at build time, so the same composition produces one SSP per selection: the component name `source` and the connector layout stay fixed, while the packaged FMU and `extra/org.pyssp/selection.json` change. No scenario set is applied, so both studies use the FMU defaults.

## Architecture Source

- `architecture/variation_source_swap.sysml`
- Exportable composition: `System :> SspModel`
- Variation point: `variation part def SourceChoice` with `variant part step : Step` and `variant part sine : Sine`
- `Step` and `Sine` expose `y` plus their FMU parameter connectors; `System` exposes no `y` port.
- Study compositions: `step :> Study`, `sine :> Study`
- No legacy SSD, SSV, or SSM is checked into the model directory.

## Studies

- `step :> Study` selects `sut.source=step`; the model build selects `source=step`.
- `sine :> Study` selects `sut.source=sine`; the model build selects `source=sine`.
- Selection is applied at build time through `build_fixture(selections={study: {"study": {...}, "model": {...}}})`; study keys are rooted at the Study, model keys at `System`.
- Experiment: `startTime=0.0`, `stopTime=1.0`, `stepSize=0.001`.
- No SSV or SSM is generated; each study directory holds only `study.json`.
- Artifacts: `artifacts/studies/variation_source_swap/<study>/`; studies are never exported as SSPs.
- Registry: only `sine` is registered (compare `source.y` on ssp4sim and OMSimulator). `step` is built but not registered because Step's defaults (`height=1`, `offset=0`, `startTime=0`) make its output constant, so its comparison gate would be degenerate.

## Strategy Role

- Structural variation fixture: the selection retypes one part usage and swaps the packaged FMU.
- Build-level contract test: `tests/test_variation_cases.py` asserts the element tree and packaged FMU per selection.
- Catches a dropped selection, an unselected point that silently builds, a stale SSD, and a missing selection record.
- The registered `sine` case is the variation-point entry in the cross-engine comparison gate; that comparison currently passes.

## Structure

- `System` contains `source : SourceChoice`; there is no root output port.
- `step` selection: `source` is `Step.fmu`; signal `source.y`.
- `sine` selection: `source` is `Sine.fmu`; signal `source.y`.

## Intent

- Prove that a definition-level part variation changes the packaged FMU, the SSD component type, and `extra/org.pyssp/selection.json` while the component name and connector layout stay fixed.

## Expected Behavior

- `step`: `source.y = 1` for `t > 0` (Step defaults are constant).
- `sine`: `source.y = sin(2*pi*t)` with Sine defaults (`amplitude=1`, `f=1`, `offset=0`, `phase=0`).
- There is no root output; the compared signal is `source.y`.

## Simulation Notes

- Both studies run the built SSP as-is; no scenario is injected.
- Only `sine` has registry evidence. The `step` build is not a passing behavioral case.

## Packaging Notes

- Exported model: `artifacts/models/variation_source_swap/<study>/model/`
- Study artifacts: `artifacts/studies/variation_source_swap/<study>/`
- FMU sources: `models/fmu/Modelica.Blocks.Sources.Step/fmu`, `models/fmu/Modelica.Blocks.Sources.Sine/fmu`
- Build: `python3 scripts/build_models.py run variation_source_swap`
