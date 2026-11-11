# signal_init_chain

## Origin

Assembled from shared Modelica FMUs. The model and analysis are authored in SysML
under `architecture/`.

## Overview

`signal_init_chain` is a minimal 3-FMU strict chain that demonstrates how
initialization interacts with SSP connections: every FMU except the first has a
connected input, so the start-time frontier exposes exactly what each component
committed when it left initialization mode.

## Architecture Source

- `architecture/` split by section: `01-interfaces.sysml`,
  `02-parameters.sysml`, `03-components.sysml`, `04-structure.sysml`,
  `05-analyses.sysml`
- Exportable composition: `System :> SspModel`
- Analysis composition: `baseline :> Analysis`
- No legacy SSD, SSV, or SSM is checked into the model directory.

## Analyses

- `baseline :> Analysis`
- Scenario set: `ScenarioSet`
- Experiment: `startTime=0.0`, `stopTime=1.0`, `stepSize=0.001`
- Artifacts: `artifacts/analyses/signal_init_chain/baseline/`
- Analyses are never exported as SSPs.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- omsimulator

## Structure

- `source (Sine) -> gain (Gain) -> add (Add.u1)`

A strict chain: every FMU except the first has a connected input.

## How Initialization Works

### FMI 2.0 co-simulation lifecycle (per component)

1. `fmi2Instantiate` — the FMU shared library is loaded, an instance created.
2. `fmi2SetupExperiment` — start/stop time and tolerance are communicated.
3. `fmi2EnterInitializationMode` — the component enters initialization mode.
4. Inside initialization mode the engine may set start values (parameters,
   input start values), and the component computes its `initial=calculated`
   outputs (the model description's `InitialUnknowns`).
5. `fmi2ExitInitializationMode` — the component derives its initial continuous
   state from the values its inputs hold *at this moment*; its outputs become
   valid at the start-time frontier.
6. Communication loop — `fmi2DoStep` per timestep, with the engine routing
   outputs to inputs between steps.

### What an SSP connection is

A connection (`ssd:Connection`) is a runtime routing rule: during the
communication loop the engine copies the upstream output into the downstream
input every step. It is not an initialization-time data transfer.

### Consequence for a chain

Components enter and exit initialization independently. When `gain` exits
initialization, its connected input `u` holds its start value (the FMU
default), not `source`'s committed output — so its initial state is derived
from defaults. The upstream value only arrives at the first communication
step, one hop late at the start-time frontier.

### Initialization order

A component-ordering that lets every component observe committed upstream
outputs before it exits initialization exists if and only if the connection
graph is acyclic (a DAG): source-first (topological) order. A cycle has no
such order — cross-FMU algebraic loops require iteration during
initialization and cannot be resolved by ordering alone.

This fixture is the minimal DAG that forces a non-trivial order: a strict
chain of three components.

## Parameters

- sine.offset = 10.0, sine.amplitude = 0.5, sine.f = 1.0 (the frontier
  value at t=0 is the offset, since sin(0)=0, and the signal varies over the
  window so gate comparisons are judgeable)
- gain.k = 1.0 (pass-through)
- add.k1 = 1.0, add.k2 = 0.0 (only u1 matters)

## Intent

- Isolate initialization semantics: a sine source, a pass-through gain and
  a pass-through sum leave nothing but the initialization-time data flow to
  observe.
- Provide the reference case for start-time-frontier correctness in chained
  FMU systems.

## Expected Behavior

With source-first (topological) initialization, at the start-time frontier
(t=0) all three outputs equal 10.0, the offset.

When components initialize independently, each downstream component commits
its default start value (0.0) and lags exactly one timestep per chain hop, as
the measured baseline run under
`artifacts/simulation/signal_init_chain/baseline/` shows:

| t | source.y | gain.y | add.y |
|-------|-----------|-----------|-----------|
| 0.001 | 10.003142 | 0.0 | 0.0 |
| 0.002 | 10.006283 | 10.006283 | 0.0 |
| 0.003 | 10.009424 | 10.009424 | 10.006283 |

After the frontier the runtime routing has taken over and the chain is correct —
the difference is confined to initialization-time committed values.

## Engine-Specific Notes

Verified across the two registered backends on the same built SSP:

- **omsimulator** propagates committed upstream outputs through initialization:
  at the frontier (t=0.0) the downstream inputs already hold the upstream
  values — `gain.u = 10.0`, `add.u1 = 10.0` — and all outputs are correct
  from the first row.
- **ssp4sim** initializes each component independently: downstream components
  commit their FMU defaults (0.0) at the frontier and catch up one timestep
  per chain hop (table above).

The cross-engine comparison
(`artifacts/comparisons/signal_init_chain/baseline/ssp4sim_vs_omsimulator/`)
is valid and fails on `add.y: criterion-exceeded (10.0 > 0.106)` — the gate
failure is the fixture's finding, expected under engines that do not propagate
initialization-time data through connections.

## Strategy Role

- Deterministic signal-propagation fixture targeting initialization semantics.
- Behavioral/regression level: distinguishes engines and engine modes that
  propagate committed outputs through initialization from those that do not.
- Exposes start-time-frontier errors that runtime comparisons miss.

## Main Failures This Catches

- Wrong committed values at the start-time frontier in chained FMUs.
- Initialization-order regressions in engines that order initialization.
- Silent convergence masking: a chain of pass-throughs heals after one step,
  so only the frontier values reveal the initialization behavior.
- Gate expectation: the cross-engine comparison fails on the downstream
  signals as long as one registered engine initializes independently.

## Simulation Notes

- The build packages the `ScenarioSet` scenario into the exported SSP in the
  fixture's parameter form (inline root parameter set).
- The runtime runs the built SSP as-is; it does not inject a scenario.
- The omsimulator backend needs the `OMSimulator` 3.x Python module (with the
  `SSP` API); system OMSimulator 2.1.x lacks it.

## Packaging Notes

- Exported model: `artifacts/models/signal_init_chain/baseline/model/`
- Analysis artifacts: `artifacts/analyses/signal_init_chain/baseline/`
- FMU sources:
  - `models/fmu/Modelica.Blocks.Sources.Sine/fmu`
  - `models/fmu/Modelica.Blocks.Math.Gain/fmu`
  - `models/fmu/Modelica.Blocks.Math.Add/fmu`
- Build: `python3 scripts/build_models.py run signal_init_chain`

## Typical Use

- Understanding and demonstrating FMU/SSP initialization semantics for
  chained components.
- Regression fixture for initialization ordering across engines and engine
  modes: pass if all three outputs equal 10.0 at the start-time frontier.
