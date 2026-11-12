# signal_init_loop

## Origin

Assembled from a newly authored loop building-block FMU
(`models/fmu/LoopGain/`), instantiated twice with different scenario
parameters. The model and analysis are authored in SysML under
`architecture/`.

## Overview

`signal_init_loop` is the cyclic companion to `signal_init_chain`: two
pass-through gain blocks wired in a loop, so the connection graph has a
cycle and no topological initialization order exists. The consistent
start values are the loop's fixed point and can only be reached by
iterating during initialization — ordering alone cannot resolve the
start-time frontier, no matter how the components are sequenced.

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
- Artifacts: `artifacts/analyses/signal_init_loop/baseline/`
- Analyses are never exported as SSPs.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- omsimulator

## Structure

- `gain_a (LoopGain) -> gain_b (LoopGain) -> gain_a` (cycle)

Both components are instances of the same FMU; the SSP references it
twice. Each hop is `y = k*u + c`:

- `gain_a`: k = 0.5, c = 10.0 (loop excitation)
- `gain_b`: k = 0.5, c = 0.0

## Why Initialization Requires Iteration

`signal_init_chain` (acyclic) has a source-first topological order that
lets every component observe committed upstream outputs before it exits
initialization. A cycle has no such order: with
`u_a = y_b`, `u_b = y_a`, `y_a = 0.5*u_a + 10`, `y_b = 0.5*u_b`, no
component can be initialized first — the consistent start values are
the loop's unique fixed point:

- `u_a = y_b = 20/3 ≈ 6.666667`
- `u_b = y_a = 40/3 ≈ 13.333333`

An engine must iterate during initialization (set inputs, read outputs,
repeat) to find these values. The loop contracts by 0.25 per turn, so
fixed-point iteration converges quickly.

An engine that initializes each component independently instead commits
whatever its inputs hold — the FMU defaults (0.0) — so `gain_a` commits
`y_a = 10.0` and `gain_b` commits `y_b = 0.0` at the frontier.

## Parameters

- gain_a: k = 0.5, c = 10.0
- gain_b: k = 0.5, c = 0.0

The parameters are bound per component through the analysis scenario
(`bind sut.gain_a.parameters.*`, `bind sut.gain_b.parameters.*`); one
FMU, two parameterizations.

## Intent

- Complete the initialization series: chain (a topological order
  exists), guard (loud failure when propagation is missing), loop (no
  order exists — iteration is required), loop_guard (a division inside
  the cycle — no engine passes today).
- Isolate initialization semantics: pass-through blocks leave nothing
  but the initialization-time data flow to observe.
- Distinguish engines that solve cross-FMU algebraic loops during
  initialization from engines that initialize components independently.
- Set today's bar for cyclic initialization: an engine clears this
  fixture by iterating the linear loop to its fixed point.
  `signal_init_loop_guard` raises the bar further with a division that
  no engine clears yet — this fixture is the division-free rung that
  omsimulator demonstrates is reachable.
- An init-time frontier cycle, distinct from the runtime scheduler
  loops (`signal_algebraic_loop`, `signal_nested_algebraic_loop`): this
  fixture is judged on initialization-time committed values at the
  start-time frontier, not on steady-state step-time convergence.

## Expected Behavior

With iterative initialization, at the start-time frontier (t=0) both
outputs already equal the fixed point: `gain_a.y = 13.333333`,
`gain_b.y = 6.666667`, constant over the whole window.

With independent initialization, the frontier commits the defaults and
runtime routing heals the loop geometrically (the committed values are
one full loop-turn stale, contracting by 0.25 per two hops), as the
measured baseline run under
`artifacts/simulation/signal_init_loop/baseline/` shows:

| t | gain_a.y | gain_b.y |
|-------|-----------|-----------|
| 0.001 | 10.0 | 0.0 |
| 0.002 | 10.0 | 5.0 |
| 0.003 | 12.5 | 5.0 |
| 0.004 | 12.5 | 6.25 |
| 0.005 | 13.125 | 6.25 |

Converged to (13.333333, 6.666667) by t ≈ 0.012. After the frontier the
outputs agree across engines — the difference is confined to
initialization-time committed values, so only the frontier rows and the
healing transient reveal the initialization behavior (the same
silent-convergence masking as `signal_init_chain`, but caused by a
cycle instead of an ordering choice).

## Engine-Specific Notes

Verified across the two registered backends on the same built SSP:

- **omsimulator** detects the algebraic loop and iterates during
  initialization. The log reports `Alg. loop (size 2/4)
  model.root.gain_b, model.root.gain_a`; at the frontier (t=0.0):
  `gain_a.u = 6.66666666667`, `gain_a.y = 13.3333333333`,
  `gain_b.u = 13.3333333333`, `gain_b.y = 6.66666666667`. No errors.
- **ssp4sim** initializes each component independently: both inputs hold
  their defaults (0.0) at the frontier, the outputs commit 10.0 and 0.0,
  and the loop heals geometrically over the first ~12 steps (table
  above). No crash — the wrong committed values are silent.

The cross-engine comparison
(`artifacts/comparisons/signal_init_loop/baseline/ssp4sim_vs_omsimulator/`)
is valid and fails on both compare signals — the gate failure is the
fixture's finding, expected under engines that do not iterate during
initialization.

## Strategy Role

- Deterministic signal-propagation fixture targeting initialization
  semantics under a cyclic connection graph.
- Behavioral/regression level: distinguishes engines that iterate during
  initialization from those that initialize independently.
- Exposes start-time-frontier errors that runtime comparisons miss: a
  contracting loop heals within a few steps, so only the frontier values
  reveal the initialization behavior.

## Main Failures This Catches

- Engines that do not iterate during initialization commit default start
  values in every loop component (silent, heals within ~12 steps).
- Initialization-order regressions: an engine that previously iterated
  and now initializes independently changes the frontier values.
- Silent convergence masking: the loop contracts geometrically, so only
  the start-time frontier exposes the difference.
- Gate expectation: the cross-engine comparison fails on both signals as
  long as one registered engine initializes independently.

## Simulation Notes

- The build packages the `ScenarioSet` scenario into the exported SSP in
  the fixture's parameter form (inline root parameter set).
- The runtime runs the built SSP as-is; it does not inject a scenario.
- The omsimulator backend needs the `OMSimulator` 3.x Python module (with
  the `SSP` API); system OMSimulator 2.1.x lacks it.

## Packaging Notes

- Exported model: `artifacts/models/signal_init_loop/baseline/model/`
- Analysis artifacts: `artifacts/analyses/signal_init_loop/baseline/`
- FMU sources:
  - `models/fmu/LoopGain/fmu` (one FMU, referenced by both components)
- The LoopGain FMU is built manually with
  `python3 models/fmu/LoopGain/build.py` (it is not part of the
  discovered workflow set, mirroring InitGuard and the shared
  Modelica.Blocks FMU sources).
- Build: `python3 scripts/build_models.py run signal_init_loop`

## Typical Use

- Verifying that an engine iterates during initialization when the
  connection graph has a cycle: pass if both outputs equal the fixed
  point (13.333333, 6.666667) from the first row.
- Regression fixture for initialization iteration across engines and
  engine modes, alongside `signal_init_chain` (ordering) and
  `signal_init_chain_guard` (propagation assert).
