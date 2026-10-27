---
id: EVAL-001
type: eval
title: Co-Simulation Engine Test Strategy
summary: Prepare an exported model and study, simulate every registered backend, compare results.
date: 2026-10-22
status: current
pb_exempt: true
---

# Co-Simulation Engine Test Strategy

## Purpose

This repository should validate a co-simulation engine by running prepared SSP
models, collecting simulation results, and comparing those results against
trusted baselines.

The strategy is intentionally high level. It focuses on confidence in simulation
behavior, not on implementation details inside the engine.

## Core Principle

The main test question is:

"When the engine simulates a known SSP model, does it produce the expected
result trajectory?"

Every test level should therefore be organized around three steps:

1. Prepare a stable exported `SspModel` and, where needed, a `Study` scenario.
2. Simulate the runnable SSP with one or more engines under that study.
3. Compare the produced result signals against a trusted reference.

## Primary Oracles

Result comparison should use a small set of trusted oracles:

- Reference trajectories stored alongside the shared FMU fixtures under
  `models/fmu/<model>/references/`.
- A trusted external engine such as OMSimulator.
- Previously accepted engine results for regression detection.

These oracles serve different purposes:

- Reference trajectories validate model behavior against known expected output.
- Cross-engine comparison validates compatibility with established tooling.
- Regression baselines detect unintended changes between engine versions.

## Model and Study Preparation

Migrated fixtures separate the model from the study that exercises it, and the
build joins them:

- A `part def ... :> SspModel` is exported per study as an SSP. It contains the
  component wiring and parameter interfaces.
- A `part def ... :> Study` supplies a scenario SSV/SSM and one experiment
  descriptor (start, stop, step). It is never exported as an SSP.
- The build packages the study scenario into the SSP in the fixture's parameter
  form. Simulation runs the built SSP as-is.
- Build, study generation, simulation, and comparison are submitted as
  `sequence_extensions` nodes so models and studies can run in parallel.

Pilot status: the `signal_*` family is migrated to SysML authoring. Each fixture
exports `System :> SspModel` to `artifacts/models/<model>/<study>/model/`,
generates its study under `artifacts/studies/<model>/<study>/`, and passes the
registered engine gate. Parameter forms are preserved per fixture (`PD-007`).

A migrated fixture is verified in four steps:

1. The `SspModel` builds and its SSD round-trips through
   `check_sysml_roundtrip.py --strict`.
2. The `Study` generates scenario values and mappings with targets relative to
   the exported SSP root.
3. All registered backends simulate the same exported SSP with the study
   scenario and agree within the gate.
4. The `pyssp_vv` verdict distinguishes `pass`, `fail`, and `invalid`.

## Test Levels

### 1. Smoke Tests

Smoke tests answer: "Can the engine simulate the model at all?"

They should:

- Run a small representative subset of SSP models.
- Confirm the simulation completes without crashes or invalid outputs.
- Check that a result file is produced with the expected time column and signal
  set.

This level is meant for fast feedback in normal development.

### 2. Behavioral Comparison Tests

Behavioral comparison tests answer: "Does the engine produce the right system
response?"

They should:

- Simulate each selected model with the engine under test.
- Simulate the same model with a trusted comparison engine where possible.
- Resample onto a common time grid.
- Compare the explicitly selected signal set for that model using metrics such
  as max absolute error, mean absolute error, and RMSE.

This should be the main quality gate for the engine.

### 3. Regression Tests

Regression tests answer: "Did engine behavior change unexpectedly?"

They should:

- Preserve accepted comparison outputs for important models.
- Re-run the same simulations after engine changes.
- Flag unexpected metric deltas or newly missing signals.

This level protects against silent degradation after solver, scheduler, or FMI
integration changes.

## Model Portfolio

The test portfolio should cover different kinds of co-simulation risk.

### Simple Reference Models

Examples: `BouncingBall`, `VanDerPol`, `Dahlquist`, `Stair`, `Resource`.

These models are useful for:

- Fast execution.
- Isolated validation of time integration and event handling.
- Detecting obvious numerical or FMI interface regressions.

### Deterministic Signal-Propagation Building Blocks

Examples: `Modelica.Blocks.Math.Add`, `Modelica.Blocks.Math.Gain`,
`Modelica.Blocks.Math.Product`, `Modelica.Blocks.Sources.Step`,
`Modelica.Blocks.Sources.Sine`.

These FMUs should be used as small composable building blocks for targeted
signal-propagation tests.

They are especially valuable because many of them are algebraic or otherwise
highly deterministic from one communication step to the next. That makes them
well suited for checking whether the engine propagates values correctly across
connections and across step boundaries.

These building blocks are useful for:

- Verifying that connected outputs appear at downstream inputs when expected.
- Detecting ordering and feedthrough errors in coupled execution.
- Checking that algebraic transformations preserve the expected numerical
  relationship between signals.
- Validating that communication-step handling does not introduce unexpected lag,
  drift, or oscillation.
- Building minimal SSPs that isolate one propagation behavior at a time.

### Composite SSP Models

Examples: `dcmotor`, `embrace`.

These models are useful for:

- Validating multi-component coupling behavior.
- Checking signal routing across components.
- Exercising realistic SSP packaging and resource handling.
- Exposing scheduling and data-exchange issues not visible in single-FMU cases.

## Signal-Propagation Focus

The strategy should explicitly include a class of tests whose main purpose is
not complex physical behavior, but signal propagation through a coupled system.

These tests should be assembled from deterministic FMU building blocks so that
the expected result is simple to reason about and easy to compare.

Typical propagation scenarios include:

- Pure pass-through or identity-like behavior.
- Algebraic combinations such as addition, multiplication, and gain scaling.
- Source-to-transform-to-output chains across multiple components.
- Step changes and sinusoidal inputs propagated through deterministic blocks.
- Small networks where a one-step delay, wrong evaluation order, or incorrect
  connector mapping becomes immediately visible in the result traces.
- Closed algebraic loops, both as a single loop and as a nested loop inside a
  larger loop, to expose simultaneous-equation solving and feedback ordering.

This class of tests is important because it isolates engine orchestration
behavior. When such a test fails, the likely problem is in scheduling, data
exchange, or connector handling rather than in the physical model itself.

### Closed Algebraic-Loop Coverage

The repository should keep at least two dedicated fixtures for closed feedback
systems:

- A sole algebraic loop around a single gain/add pair.
- A nested loop where one closed loop feeds another closed loop.

These are needed because acyclic signal chains do not exercise the part of the
runtime that must resolve simultaneous equations across backends. A backend can
appear correct on fan-in, fan-out, and delay-style fixtures while still
failing on loop closure, so these cases provide a separate regression target.

## Comparison Policy

Signal comparison should be pragmatic rather than binary.

The strategy should compare:

- Signal presence.
- Time coverage.
- Magnitude agreement.
- Trend agreement across the simulation window.

Acceptance should be based on per-signal tolerances, not bitwise equality.
Different model classes will need different tolerance levels. The
`pyssp_vv` judgment records `pass`, `fail`, or `invalid`; `invalid` means the
comparison was not fit to judge and must not be reported as a numerical
failure.

Recommended rule set:

- Use tighter tolerances for simple reference models.
- Use very tight tolerances for deterministic signal-propagation models built
  from algebraic Modelica FMUs.
- Treat closed-loop deterministic fixtures with the same tight threshold, but
  require them specifically to prove the engine converges on the loop solution
  rather than merely matching an acyclic feedthrough trace.
- Use broader tolerances for larger composite models.
- Treat missing signals, NaNs, unstable spikes, or early termination as test
  failures even when aggregate metrics look acceptable.

For deterministic propagation tests, comparison should emphasize exact signal
relationships in addition to aggregate error metrics. For example, the engine
should preserve expected scaling, summation, and timing behavior across each
communication step, not merely produce a roughly similar overall trajectory.

## Execution Cadence

The suite should run at different depths depending on purpose.

- Per change: smoke tests plus a small comparison subset.
- Before merge: broader comparison across representative simple and composite
  models.
- Periodically or before release: full regression sweep across all maintained
  models and supported configurations.

## Expected Outputs

Each test run should leave behind artifacts that are easy to inspect:

- Raw simulation result files per engine under `artifacts/simulation/`.
- Pairwise comparison CSV files under `artifacts/comparisons/`.
- Summary JSON files with error metrics and test window metadata.

This makes failures diagnosable and keeps the strategy useful for both automated
gates and manual investigation.

## Out Of Scope

This strategy does not try to prove absolute physical correctness of every
model. It is meant to validate engine behavior relative to stable fixtures and
trusted baselines.

## Repository Fit

This repository already supports the core workflow needed for the strategy:

- SSP fixtures live under `models/ssp/`.
- Reusable FMU building blocks live under `models/fmu/`.
- Migrated fixtures author `SspModel` and `Study` definitions under
  `models/ssp/<model>/architecture/`.
- Runnable SSPs live under `artifacts/models/<model>/<study>/<build>/`.
- Study scenario and experiment artifacts live under
  `artifacts/studies/<model>/<study>/`. Studies are not SSPs.
- Runtime setup, simulation, and comparison outputs live under
  `artifacts/simulation/<model>/<study>/` and
  `artifacts/comparisons/<model>/<study>/`.
- `artifacts/simulation_registry.json` maps model builds to one or more studies,
  records the backends for each study explicitly, and stores the selected
  compare signals for each model. The current backend set is `ssp4sim`,
  `OMSimulator`, and `FMPy`.
- Each generated `artifacts/simulation/<model>/<study>/setup.json` also stores
  the explicit backend list, selected compare signals, scenario paths, and
  experiment window for that setup.
- Simulation is driven by `scripts/run_simulations.py` and the target
  `pyssp_workflow` nodes.
- Comparison is driven by `scripts/run_comparisons.py`; measurement and
  judgment come from `pyssp_vv`.

That means the immediate next step is selecting a small required model set,
including deterministic signal-propagation fixtures, defining tolerances per
model or signal group, and turning comparison outcomes into clear
pass/fail/invalid criteria.

## Coverage Taxonomy Reference

The System Simulation Use-Case Coverage Analysis `EVAL-008`
defines the canonical coverage taxonomy (UC-1 through UC-16) for this fixture
suite. Every test level defined in this strategy should be traceable to one or
more use-cases in that taxonomy.

New fixture and test work should be prioritized against the gap map in the
coverage analysis document rather than ad-hoc.

The taxonomy also identifies two engine-level verification tests
(`test_reference_csvs_are_not_inverted`,
`test_modelica_block_fmus_expose_dependency_metadata`) that should be
transferred to the respective simulation engine repositories. These tests
verify implementation details that belong in the engine projects, not in
this fixture suite's test suite.
