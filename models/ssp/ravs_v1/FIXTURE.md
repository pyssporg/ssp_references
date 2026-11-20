# ravs_v1

Reference Aircraft Vehicle Systems (RAVS), version 1.

## Version

- v1 is the legacy EMBRACE-derived composite (formerly `models/ssp/embrace`).
- v2 is the D16 aerospace demo sibling fixture, `ravs_v2`.
- Both are separate models in the registry, and both are exercised by tests.
- Historical run artifacts produced before the rename remain under
  `artifacts/{simulation,comparisons,plots}/embrace/`.

## Origin

Authored SSP fixture built around local component FMUs and a boundary-conditions
CSV source. The FMUs live under `models/ssp/ravs_v1/resources/`; they were
previously packaged through a checked-in `ssp/` body, which the SysML
architecture now replaces.

## Overview

`ravs_v1` is a larger composite SSP fixture representing a realistic,
resource-heavy orchestration case. Six co-simulation FMUs exchange scalar and
fluid-state signals; one FMU reads its boundary conditions from a packaged
`data/CONOPS.csv`.

## Architecture Source

- `architecture/01-interfaces.sysml` — model/analysis markers, the flat scalar
  signal ports, the `FluidState` fluid port (plain and conjugated), the
  `SwSignals` grouped proxy port, and the ECS_HW parameter interface.
- `architecture/02-parameters.sysml` — scenario set and experiment window.
- `architecture/03-components.sysml` — FMU metadata and the six component
  definitions.
- `architecture/04-structure.sysml` — `System :> SspModel` composition and
  wiring.
- `architecture/05-analyses.sysml` — `baseline :> Analysis`.
- No legacy SSD, SSV, or SSM is checked in.

`System` is exported from SysML; the
[port dialect](../../../docs/reference/port-dialect.md) explains how ports are
shaped around FMU variable names. In this fixture the mirrored fluid side is
`ECS_HW.consumerFeed : FluidStateConjugate` (`consumerFeed.p` input,
`consumerFeed.m` output).

The parameter interface declares the two effective structured targets,
`'pipeA.L'` and `'pipeB.L'`. The legacy external SSV/SSM pair was almost
entirely inert: only these two targets were mapped, and the remaining SSV
members named no FMU variable. The SysML scenario set carries the legacy mapped
values at full precision; both registered backends reproduce the previous
physical-signal trajectories exactly (the `$wallTime` columns are run-dependent).

## Analyses

- `baseline :> Analysis`
- Scenario set: `ScenarioSet`
- Experiment window and step: see `architecture/02-parameters.sysml`; the
  0.0–10.0 bounds are the exported `DefaultExperiment`.
- Tolerance is not part of the experiment; the FMUs declare it in their
  `DefaultExperiment`.
- Artifacts: `artifacts/analyses/ravs_v1/baseline/`
- Analyses are never exported as SSPs.

## Structure

Wiring and composition live in `architecture/04-structure.sysml`.

## Deviations from the legacy SSD

- **Connector orientation.** The regenerated SSD orients four connections the
  other way (`Consumer` start vs `ECS_HW` start for `consumerFeed.{m,hn}` and
  `consumerRet.{m,hn}`); the endpoint pairs are identical and SSP connections
  are undirected.

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

- Exported model: `artifacts/models/ravs_v1/baseline/model/`
- Analysis artifacts: `artifacts/analyses/ravs_v1/baseline/`
- FMU sources: `models/ssp/ravs_v1/resources/{0001_ECS_HW,0002_ECS_SW,0003_Consumer,0004_Atmos,0005_AdaptionUnit,BC}`
- Build: `python3 scripts/build_models.py run ravs_v1`
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
