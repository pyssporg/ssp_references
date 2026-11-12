# signal_init_chain_guard

## Origin

Assembled from a shared Modelica sine FMU, a newly authored validating guard
FMU (`models/fmu/InitGuard/`), and a shared Modelica add FMU. The model and
analysis are authored in SysML under `architecture/`.

## Overview

`signal_init_chain_guard` is the hard-failure companion to `signal_init_chain`: the
same strict chain, but the middle component is a guard that refuses to finish
initialization while its connected input holds the default zero. The failure
mode that is silent in `signal_init_chain` becomes a hard crash at startup.

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
- Artifacts: `artifacts/analyses/signal_init_chain_guard/baseline/`
- Analyses are never exported as SSPs.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- omsimulator

## Structure

- `source (Sine) -> guard (InitGuard) -> add (Add.u1)`

## How the Guard Fails

The guard FMU is authored in Modelica with a hard assertion in its
`initial equation`:

```
initial equation
  assert(u > 1e-6, "InitGuard: connected input u is zero during initialization; "
    + "the upstream value was not propagated into this component "
    + "before exitInitializationMode.");
```

Under the FMI 2.0 lifecycle the engine calls `fmi2ExitInitializationMode`
after setting start values. A guard whose connected input still holds the
default (0.0) at that point evaluates the assert false and returns
`fmi2Error` — the engine is then obligated to abort initialization.

This converts the silent start-time-frontier failure (documented in
`signal_init_chain`) into an explicit, loud failure: an engine that does not
propagate committed upstream outputs through initialization crashes at
startup instead of producing a subtly wrong first steps.

## Parameters

- sine.offset = 10.0, sine.amplitude = 0.5, sine.f = 1.0
- add.k1 = 1.0, add.k2 = 0.0 (only u1 matters)

## Expected Behavior

- **omsimulator** propagates committed upstream outputs into the guard's input
  before the guard exits initialization: `guard.u = 10.0` at the frontier, the
  assert passes, and the full window simulates with all three outputs equal to
  the sine value.
- **ssp4sim** initializes the guard independently; the guard's input holds its
  default zero at `exitInitializationMode`, the assert fails, and the process
  aborts before producing a result.

### Verified Behavior

Measured against the built SSP (`artifacts/simulation/signal_init_chain_guard/baseline/`):

- **omsimulator**: runs the full window. At the frontier (t=0.0):
  `guard.u = 10.0`, `guard.y = 10.0`, `add.u1 = 10.0`, `add.y = 10.0`.
  No errors in the log.
- **ssp4sim**: aborts during initialization. The log reports
  `[exit_init] exit_initialization_mode failed for guard`; the process
  terminates with SIGABRT (exit code 134, core dumped) and produces an
  empty result (0 data rows).

## Intent

- Demonstrate the FMI 2.0 initialization contract: an FMU may reject
  initialization, and the engine must propagate that failure.
- Make the independent-initialization failure loud and testable as a crash
  rather than a silent one-step lag.

## Main Failures This Catches

- Engines that do not propagate initialization-time data through connections
  crash the guard fixture at startup.
- Regression in the guard FMU itself (assert never fires, or fires on valid
  values).
- Engine behavior changes: if an engine starts passing the guard when it
  previously crashed (or vice versa), the fixture reports the change.

## Simulation Notes

- The build packages the `ScenarioSet` scenario into the exported SSP in the
  fixture's parameter form (inline root parameter set).
- The runtime runs the built SSP as-is; it does not inject a scenario.
- The omsimulator backend needs the `OMSimulator` 3.x Python module (with the
  `SSP` API); system OMSimulator 2.1.x lacks it.

## Packaging Notes

- Exported model: `artifacts/models/signal_init_chain_guard/baseline/model/`
- Analysis artifacts: `artifacts/analyses/signal_init_chain_guard/baseline/`
- FMU sources:
  - `models/fmu/Modelica.Blocks.Sources.Sine/fmu`
  - `models/fmu/InitGuard/fmu`
  - `models/fmu/Modelica.Blocks.Math.Add/fmu`
- The guard FMU is built manually with `python3 models/fmu/InitGuard/build.py`
  (it is not part of the discovered workflow set, mirroring the shared
  Modelica.Blocks FMU sources).
- Build: `python3 scripts/build_models.py run signal_init_chain_guard`

## Typical Use

- Verifying that an engine propagates initialization-time data through
  connections: an engine that crashes on this fixture has the 
  independent-initialization behavior.
