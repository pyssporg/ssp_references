# signal_init_loop_guard

## Origin

Assembled from the loop building-block FMU shared with `signal_init_loop`
(`models/fmu/LoopGain/`) and a newly authored validating divider FMU
(`models/fmu/DivideGuard/`). The model and analysis are authored in SysML
under `architecture/`.

## Overview

`signal_init_loop_guard` is the hard-failure companion to
`signal_init_loop`: the same cyclic loop, but the second component divides
a constant by its connected input, so a zero input during initialization
is not merely wrong — it is a division by zero. The failure mode that is
silent (default-committed values) in `signal_init_loop` becomes a loud
abort at startup.

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
- Artifacts: `artifacts/analyses/signal_init_loop_guard/baseline/`
- Analyses are never exported as SSPs.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- omsimulator

## Structure

- `gain (LoopGain) -> div (DivideGuard) -> gain` (cycle)

Each hop:

- `gain`: y = k*u + c with k = 0.5, c = 10.0 (loop excitation)
- `div`: y = c/u with c = 100.0 (divides by its connected input)

## Why It Crashes

The cycle has no topological initialization order. The consistent start
values are the loop's unique positive fixed point:

- `div.u = gain.y = 5*(sqrt(3)+1) ≈ 13.660254`
- `gain.u = div.y = 10*(sqrt(3)-1) ≈ 7.320508`

Reaching them requires iterating the loop — but every evaluation of
`div` with its input still at the default start value (0.0) divides by
zero. Both engines evaluate exactly that way during initialization:

- An engine that initializes components independently (no iteration)
  evaluates `div` at `fmi2ExitInitializationMode` with `u = 0.0`.
- An engine that iterates the loop Jacobi-style (evaluate all outputs
  at current inputs, then set all inputs) evaluates `div`'s output
  first, before any input has been set — with `u = 0.0`.

The OpenModelica runtime inside the FMU guards the division natively
(`division by zero at time 0, (a=100) / (b=0)`), and the block asserts
`u > 1e-6` in its `initial equation` as a defensive guard with an
explicit message. Either check rejects initialization with `fmi2Error`,
and the engine must abort.

## Parameters

- gain: k = 0.5, c = 10.0
- div: c = 100.0 (dividend)

## Intent

- Give the cyclic-loop initialization pattern a realistic hard failure:
  a division by the connected input, the classic initialization crash.
- Demonstrate the FMI 2.0 initialization contract under a cycle: an FMU
  may reject initialization, and the engine must propagate the failure.
- Verify that engines reject the un-initializable loop loudly instead of
  silently emitting inf/NaN trajectories.
- Raise the bar beyond `signal_init_loop`: that fixture is the
  division-free cyclic loop omsimulator handles by iterating; this
  fixture adds the division and is deliberately beyond every
  registered engine today — the documented development target for
  loop-capable initialization (loop-breaking propagation or
  reload-and-retry).

## Expected Behavior

No registered engine can simulate this fixture as authored: every
initialization strategy that evaluates `div` with its input at the
default 0.0 divides by zero. Two implementable engine capabilities
would pass it, and the fixture accepts either — it tests the
requirement (reach consistent loop initialization despite an FMU
rejecting init), not the mechanism:

- **Loop-breaking initialization**: propagate the freshly committed
  upstream output into `div` before it exits initialization
  (Gauss-Seidel-at-initialization with `gain` first).
- **Reload-and-retry initialization**: when the FMU rejects init with
  `fmi2Error`, free it, reload a fresh instance, set a nonzero input
  guess (any nonzero value survives the division), and re-enter
  initialization; the loop contracts by ~0.268 per turn, so the retry
  iteration converges to the fixed point. The reload is not optional
  bookkeeping: after `fmi2Error` the FMI 2.0 contract forbids reusing
  the instance, so reload is the only legal way to retry.

No registered engine has either capability today; the fixture pins
the requirement and its strict xfail in the parent sweep goes loud
the day an engine passes it.

## Engine-Specific Notes

Verified against the built SSP (`artifacts/simulation/signal_init_loop_guard/baseline/`):

- **ssp4sim**: initializes each FMU independently. At
  `fmi2ExitInitializationMode` `div.u` holds its default 0.0, the FMU
  rejects initialization, and the engine aborts: the log reports
  `[exit_init] exit_initialization_mode failed for div`; the process
  terminates (exit code 1) and produces an empty result (0 data rows).
  The execution kernel is `JacobiParallelTBB` (Jacobi-style).
- **omsimulator**: detects the loop (`Alg. loop (size 2/4)
  model.root.gain, model.root.div`) and iterates during initialization,
  but evaluates outputs at start values first (Jacobi-style): the FMU's
  runtime fires `LOG_ASSERT | division by zero at time 0, (a=100) /
  (b=0), where divisor b expression is: u`, `fmi2GetReal` is terminated
  by an assertion, and initialization fails with `Status.error`. No
  result is produced.

Neither backend produces a result, so the case has no cross-engine
comparison — the recorded evidence is the two abort modes. The crash
points differ and are diagnostic: ssp4sim fails at
`exitInitializationMode` (independent per-FMU initialization);
omsimulator fails during its initialization-loop output evaluation
(before any input was set).

Every ssp4sim executor mode aborts identically (verified on the built
SSP with a hand-edited `simulation.executor.method`):

- `jacobi` (default, all parallel variants), `seidel`, and `la2` all
  fail with `[exit_init] exit_initialization_mode failed for div`.
  ssp4sim's initialization is per-FMU independent regardless of the
  step executor: `la2` resolves the loop with Jacobi substeps at step
  time, and `seidel` orders evaluation within a step, but neither
  propagates committed outputs into a component's
  `fmi2ExitInitializationMode` inside a cycle.

## Strategy Role

- Deterministic hard-failure fixture targeting initialization semantics
  under a cyclic connection graph with a division.
- Behavioral/regression level: verifies loud rejection (abort) of an
  un-initializable loop, and distinguishes crash modes across engines.
- Complements `signal_init_loop` (silent wrong frontier values in the
  same topology) and `signal_init_chain_guard` (crash in an acyclic chain).

## Main Failures This Catches

- Engines that silently propagate inf/NaN instead of aborting when the
  initialization divides by zero.
- Behavior changes in crash mode or crash point (for example an engine
  that starts rejecting during a different lifecycle step, or an engine
  that switches from Jacobi-style to Gauss-Seidel-style initialization
  and starts passing the fixture).
- Regression in the DivideGuard FMU itself (assert never fires, or the
  division is no longer guarded).

## Simulation Notes

- The build packages the `ScenarioSet` scenario into the exported SSP in
  the fixture's parameter form (inline root parameter set).
- The runtime runs the built SSP as-is; it does not inject a scenario.
- The omsimulator backend needs the `OMSimulator` 3.x Python module (with
  the `SSP` API); system OMSimulator 2.1.x lacks it.

## Packaging Notes

- Exported model: `artifacts/models/signal_init_loop_guard/baseline/model/`
- Analysis artifacts: `artifacts/analyses/signal_init_loop_guard/baseline/`
- FMU sources:
  - `models/fmu/LoopGain/fmu` (shared with `signal_init_loop`)
  - `models/fmu/DivideGuard/fmu`
- The DivideGuard FMU is built manually with
  `python3 models/fmu/DivideGuard/build.py` (it is not part of the
  discovered workflow set, mirroring InitGuard and LoopGain).
- Build: `python3 scripts/build_models.py run signal_init_loop_guard`

## Typical Use

- Verifying that an engine aborts loudly on a divide-by-zero inside a
  cross-FMU initialization loop instead of producing non-finite output.
- Crash-mode regression fixture alongside `signal_init_chain_guard` (acyclic
  crash) and `signal_init_loop` (silent cyclic failure).
