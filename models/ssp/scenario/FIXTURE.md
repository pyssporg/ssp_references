# scenario

## Origin

Migrated from the checked-in SSP fixture that wrapped the prebuilt `scenario`
FMU (`modelDescription.xml` author/generation tool `scenario_fmu`, version
`0.1.0`). The FMU ships a linux64 binary and is now the source fixture at
`models/fmu/scenario/fmu`. The model body, parameter set, and experiment are
authored in SysML.

## Overview

`scenario` is a small single-FMU SSP that generates source data from a
structured scenario definition. The FMU exposes five real outputs and one
string parameter, `scenario_input`, whose value contains newline-separated
records.

## Architecture Source

- `architecture/scenario.sysml`
- Exportable composition: `System :> SspModel`
- Analysis composition: `baseline :> Analysis`
- Parameter interface: `ScenarioParameters :> ParameterInterface` with
  `scenario_input : String`.
- Model-owned parameter set: `ScenarioSet :> ParameterSet` is applied inside
  `System`. The analysis is experiment-only.
- No checked-in SSD, SSV, or SSM remains; the build generates them.
- `ScenarioSet` keeps the legacy SSV members `Alt_start`, `Mach_start`,
  `heat_load_start`, `Wgt_On_Whl_start`, and `Aircraft_state_start` so the
  generated parameter set matches the previous artifact. Only
  `scenario_input` is bound; the other members have no target in this SSP and
  are ignored.

## Analyses

- `baseline :> Analysis`
- Scenario set: none; the model-owned `ScenarioSet` is already applied.
- Experiment: `startTime=0.0`, `stopTime=10.0`, `stepSize=0.001`
- Tolerance is not part of the experiment; it comes from the FMU model
  description.
- Artifacts: `artifacts/analyses/scenario/baseline/`
- Analyses are never exported as SSPs.

## Structure

- Single component `scenario : Scenario` with outputs `Alt`, `Mach`,
  `heat_load`, `Wgt_On_Whl`, and `Aircraft_state`.
- No connections; the component is the whole SSP.

## Strategy Role

- Test SSV, SSM, and parameter setting in an SSP context.
- Provides a minimal scenario for validating external-parameter handling.
- Exercises a String parameter whose value contains embedded newlines.

## Intent

- Validate that an engine applies an external SSV/SSM root binding to a string
  parameter containing structured, multi-line data.

## Expected Behavior

- `scenario_input` is applied from the analysis SSV.
- `Alt` and `Mach` ramp from their start values; `heat_load`,
  `Wgt_On_Whl`, and `Aircraft_state` follow the scenario definition.
- The previous build produced 10 001 samples over `0.0..10.0`; the migrated
  build reproduces that result exactly.

## Main Failures This Catches

- SSV and SSM parsing problems.
- Missing or malformed string parameter values.
- Engines that do not apply an external root parameter binding.
- Loss of the scenario definition's newline structure.

## Simulation Notes

- Registered for `ssp4sim` only.
- The runtime runs the built SSP as-is; it does not inject a scenario.

## Packaging Notes

- Exported model: `artifacts/models/scenario/baseline/model/`
- Analysis artifacts: `artifacts/analyses/scenario/baseline/`
- FMU source: `models/fmu/scenario/fmu`
- Parameter form: one model-owned SSV
  (`resources/parameter_sets/ScenarioSet.ssv`) with an inline
  `ssd:ParameterMapping`, applied as a single root `ParameterBinding`.
- The inline mapping keeps only
  `scenario_input -> scenario.scenario_input`. The previous SSM also mapped
  `Mach_start` and `Alt_start` to `ECS_HW.fd.*` and `Consumer.fd.*`; those
  components do not exist in this SSP, so the entries were inert and are not
  reproduced. Multi-target mapping coverage lives in
  `signal_nested_external_bindings`.
- The build packages no analysis scenario; the model SSP already carries it.
- The build fixes a duplicate root binding that the old `build.py` produced.
- Build: `python3 scripts/build_models.py run scenario`

## Typical Use

- Validating engine behavior on SSV and SSM parameter parsing.
- Regression-checking string parameter handling across builds.
