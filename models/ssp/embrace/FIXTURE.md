# embrace

## Origin

Authored SSP fixture built around local component FMUs and a boundary-conditions
CSV source. The FMUs live under `models/ssp/embrace/resources/`; they were
previously packaged through a checked-in `ssp/` body, which the SysML
architecture now replaces.

## Overview

`embrace` is a larger composite SSP fixture representing a realistic,
resource-heavy orchestration case. Six co-simulation FMUs exchange scalar and
fluid-state signals; one FMU reads its boundary conditions from a packaged
`data/CONOPS.csv`.

## Architecture Source

- `architecture/01-interfaces.sysml` — model/analysis markers, flat signal
  ports, and the ECS_HW parameter interface.
- `architecture/02-parameters.sysml` — scenario set and experiment window.
- `architecture/03-components.sysml` — FMU metadata and the six component
  definitions.
- `architecture/04-structure.sysml` — `System :> SspModel` composition and
  wiring.
- `architecture/05-analyses.sysml` — `baseline :> Analysis`.
- No legacy SSD, SSV, or SSM is checked in.

`System` is exported from SysML. The FMU variable namespace uses characters a
SysML identifier cannot (dots and array brackets), so every signal is a flat
port whose quoted name is the FMU variable name, for example
`in port 'consumerFeed.X[1]' : RealSignal;`. A flat port carries one connector
named exactly as the port usage, which keeps each variable's input/output
direction independent.

The parameter interface declares the two effective structured targets,
`'pipeA.L'` and `'pipeB.L'`. The legacy external SSV/SSM pair was almost
entirely inert: only these two targets were mapped, and the remaining SSV
members named no FMU variable. The SysML scenario set carries the legacy mapped
values at full precision; both registered backends reproduce the previous
physical-signal trajectories exactly (the `$wallTime` columns are run-dependent).

## Analyses

- `baseline :> Analysis`
- Scenario set: `ScenarioSet`
- Experiment: `startTime=0.0`, `stopTime=10.0`, `stepSize=0.01`.
- Tolerance is not part of the experiment; the FMUs declare it in their
  `DefaultExperiment`.
- Artifacts: `artifacts/analyses/embrace/baseline/`
- Analyses are never exported as SSPs.

## Structure

- `BC -> Atmos, Consumer, ECS_HW, AdaptionUnit`
- `Consumer <-> ECS_HW` over `consumerFeed` and `consumerRet`
- `ECS_HW -> AdaptionUnit -> ECS_SW -> ECS_HW`

## Strategy Role

- Composite SSP model.
- Pre-merge comparison candidate.
- Regression anchor for larger-system orchestration behavior.

## Intent

- Exercise a large architecture whose FMU variables use structured names that
  need SysML quoted identifiers.
- Keep the boundary-condition source and the parameter application inside the
  standard SSP artifacts.

## Expected Behavior

- The six FMUs exchange the legacy signal set over the legacy wiring.
- `pipeA.L` and `pipeB.L` receive the legacy mapped length value.
- Engine-to-engine comparison stays within the registry gate.

## Main Failures This Catches

- Larger-system signal exchange.
- Resource-heavy packaging and loading.
- Orchestration and scheduling behavior in realistic composite models.
- Name transport: a quoted SysML name must reach the SSD without its quotes and
  without losing dots or brackets.

## Simulation Notes

- The build applies the scenario as an external SSV plus SSM.
- The runtime runs the built SSP as-is; it does not inject a scenario.

## Packaging Notes

- Exported model: `artifacts/models/embrace/baseline/model/`
- Analysis artifacts: `artifacts/analyses/embrace/baseline/`
- FMU sources: `models/ssp/embrace/resources/{0001_ECS_HW,0002_ECS_SW,0003_Consumer,0004_Atmos,0005_AdaptionUnit,BC}`
- Build: `python3 scripts/build_models.py run embrace`
- The legacy `signalFilter.xml` and the OMSimulator `SimulationInformation`
  annotation are not carried into the SysML export. OMSimulator runs with the
  repository-wide options in `scripts/workflow/simulate.py`; the result
  trajectories are unchanged.

## Engine-Specific Notes

The OMSimulator backend for this fixture is run with a reduced logging and
eventing setup to keep the result file manageable and to tolerate the model's
initial unknowns:

- `--ignoreInitialUnknowns=true`
- `--wallTime=true`
- `--emitEvents=false`
- `--inputExtrapolation=true`

## Typical Use

- Validating engine behavior on larger coupled systems where signal routing and
  setup complexity are both important.
