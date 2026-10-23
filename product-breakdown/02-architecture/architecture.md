---
id: INFO-002
type: info
title: System Architecture
summary: Stable stages, fixture hierarchy, runtime contract, and stage boundaries.
date: 2026-10-22
status: current
pb_exempt: true
---

# System Architecture

This document describes the stable guarantees, component boundaries, and
interface contracts of the `ssp_references` repository. It sits at the
**System Architecture** layer in the documentation chain, between
[00-intent/intent.md](../00-intent/intent.md) (Intent and Product Commitments) and any future
Technical Decisions records.

The canonical artifact-level contract for the pipeline and external tools is
[Pipeline and Tool Boundaries](pipeline-boundaries.md). This document describes
the full architecture; that file is the single reference for what each
boundary reads and writes.

## Library Boundary Rule

Library borders follow one rule:

1. Carry a standardized artifact first: SSP, SSD, SSV, SSM, LS-REF, or result
   CSV.
2. When no standard covers the need, carry only a type that is explicitly part
   of the producer's public API.
3. Never carry internal modules, private objects, or adapter-only structures
   across a library border.
4. Treat a new public type as a deliberate API decision, not an accidental
   export.

This applies to Python imports as well as files. A consumer imports the
producer's public surface; it does not reach into an internal module because
that module happens to be importable today. See `ADR-011`.

---

## 1. Three-Stage Pipeline

The repository's core workflow is a three-stage pipeline. Each stage is
independently invocable — it consumes only its own inputs, produces only its
own outputs, and has no side effects on the data of any other stage. The three
stages are connected by file-based interface contracts, not by shared memory,
inter-process calls, or hidden state.

### Stage 1: Build

**Purpose:** Transform authored model and study definitions into a reproducible,
runtime-ready exported SSP and the study data that exercises it.

**Input:** A model directory under `models/ssp/<model_name>/` containing at
minimum a `build.py` script and a `FIXTURE.md` fixture note. Migrated fixtures
carry `architecture/*.sysml` with a `part def ... :> SspModel` and, where
studies are defined, `part def ... :> Study` compositions. Some legacy model
directories still carry an `experiments.xml` and checked-in or generated
resource files (FMUs, legacy SSV/SSM) until they are migrated. A fixture may
keep its legacy SSD and resources as the model body and author only the study
in SysML; the `SspModel` composition is then a boundary marker, selects the
body with `ssp_meta.source`, and is never exported.

**Output:** Two artifact classes:

- a runnable build SSP at
  `artifacts/models/<model_name>/<study_name>/<build_name>/` containing
  `SystemStructure.ssd`, `resources/`, and the study scenario already packaged
  in the fixture's parameter-application form;
- study artifacts at `artifacts/studies/<model_name>/<study_name>/` containing
  the study descriptor and, when the study applies one, the scenario SSV and
  SSM mapping. A study may author only an experiment. Studies are not SSPs;
  they are build inputs that supply the window and, optionally, the scenario.

**Entry point:** `scripts/build_models.py` discovers and dispatches to each
model's own `build.py`. The model-level build script is the source of truth for
how that particular fixture is exported and which studies it generates.
Migrated build scripts call `pyssp_workflow.authoring` for SysML derivation and
then apply the fixture's parameter-application form with `pyssp_standard`
(`ADR-013`, `DD-011`).

**Invariant:** The build stage does not execute simulations, does not write to
`artifacts/simulation/` or `artifacts/comparisons/`, and does not modify
`artifacts/simulation_registry.json`. Its build SSP is the complete engine
input.

### Stage 2: Simulate

**Purpose:** Run registered studies against one or more simulation backends and
record raw result trajectories.

**Input:** A runnable build SSP and its study descriptor (from Stage 1) plus the
simulation registry at `artifacts/simulation_registry.json`, which maps each
model build to named studies, backends, compare signals, references, and gate
policy. The study descriptor supplies the simulation window (start time, stop
time, step size). The scenario is already packaged in the SSP, so the simulate
stage does not inject one. Tolerance is read from the composed FMUs.

**Output:** Per-backend simulation result files (CSV, and optionally `.mat`
for some backends) under
`artifacts/simulation/<model_name>/<study_name>/<backend>/`. Each run also
produces a `simulation.json` run manifest at the same location.

**Entry point:** `scripts/run_simulations.py` reads the registry, expands the
model/study/backend matrix, prepares setup manifests, and dispatches through
`pyssp_workflow` execute nodes. Engine execution is a `pyssp_simulate`
responsibility; local compatibility shims exist only for documented upstream
gaps (see `ADR-005` and `ADR-008`).

**Invariant:** The simulate stage does not rebuild SSPs, does not inject a
scenario, does not mutate build artifacts or model source directories, and does
not run comparisons.

### Stage 3: Compare

**Purpose:** Compare simulation results across different backends and produce
pairwise metrics.

**Input:** Simulation run manifests (from Stage 2) referencing result CSV files,
plus the compare-signal list from the setup manifest. Comparison is always
engine-to-engine — at least two distinct backend runs are required.

**Output:** Per-pairwise-comparison metrics CSV files and comparison manifests
under
`artifacts/comparisons/<model_name>/<study_name>/<backend_a>_vs_<backend_b>/`.
Reference comparisons are written under
`artifacts/comparisons/<model_name>/<study_name>/references/<backend>_vs_<reference_label>/`.
A batch-level comparison manifest is also written at
`artifacts/comparisons/<model_name>/<study_name>/comparisons.json`. Every
comparison manifest records a `gate` verdict and its reasons. The gate records
`pass`, `fail`, or `invalid`; `invalid` means the comparison was not fit to
judge.

**Entry point:** `scripts/run_comparisons.py` reads the registry, loads the
setup and run manifests, and drives the comparison. `pyssp_vv.measure` produces
the metrics, `pyssp_vv.judge` produces the verdict, and model-specific signal
invariants live in `workflow/model_policy.py`.

**Invariant:** The compare stage does not re-run simulations, does not rebuild
SSPs, and does not modify model sources or simulation outputs.

---

## 2. Fixture Hierarchy

The repository organizes fixture models into four architectural classes. Each
class represents a different level of compositional complexity and serves a
distinct purpose in the pipeline.

```
  FMU Building Blocks
        |
        v
  Simple Reference SSPs     Deterministic Signal-Propagation Fixtures
        |                              |
        +--------------+---------------+
                       |
                       v
              Composite SSPs
```

### FMU Building Blocks
Reusable signal-processing FMUs (e.g., sources, gains, combiners). These are
the base units of the fixture hierarchy. They live as exported FMUs under
`models/fmu/` and are referenced by SSP fixtures during the build stage.

### Simple Reference SSPs
Single-FMU SSPs that wrap one building block or a self-contained physical model
into a runnable SSP. These are the fastest-running fixtures and serve as
basic behavioral checks.

### Deterministic Signal-Propagation Fixtures
SSPs composed from two or more FMU building blocks wired together to exercise a
specific signal-propagation scenario (fan-out, fan-in, algebraic combination,
delayed detection, etc.). The expected output of these fixtures is
algebraically predictable, making them suitable for tight-tolerance
cross-engine comparison.

### Composite SSPs
Multi-component SSPs that couple several subsystems into a single co-simulation
scenario. These exercise realistic coupling behavior, signal routing across
components, and multi-FMU scheduling.

**Architectural relationship:** FMU building blocks are the leaf dependencies.
Simple reference SSPs and signal-propagation fixtures compose building blocks
into runnable SSPs. Composite SSPs may contain any combination of the above
as internal components.

---

## 3. Key Architectural Boundaries

Each script entry point in `scripts/` has a single clear responsibility.
The following table states what each entry point owns and what it is explicitly
forbidden from doing.

| Entry Point | Owns | Forbidden From |
|---|---|---|
| `build_models.py` | Model discovery and dispatch to per-model `build.py`; exports `SspModel` SSPs and generates study artifacts | Running simulations, writing to `artifacts/simulation/` or `artifacts/comparisons/`, modifying the simulation registry |
| `run_simulations.py` | Registry expansion, study setup, runtime scenario injection, backend dispatch, result recording | Rebuilding SSPs, mutating exported model artifacts, running comparisons |
| `run_comparisons.py` | Pairwise engine-to-engine comparison, reference comparison, verdict recording | Re-running simulations, modifying model sources, rebuilding SSPs |
| `run_campaign.py` | Submitting build, study, simulate, and compare nodes through `sequence_extensions` | Implementing domain logic; bypassing the stage entry points |

These boundaries ensure that each stage can be invoked, debugged, and tested
independently. A build script failure does not corrupt simulation results; a
simulation failure does not block comparison of already-valid runs.

### Tool boundaries

Evaluation tools follow the same rule. The SysML authoring path invokes an
external `pyssp` executable through `pyssp_workflow.authoring` and exchanges
SysML, SSD, SSV, SSM, and SSP artifacts. The round-trip checker remains an
independent artifact-only adapter over SSD files. Neither path imports
`pyssp_sysml2`; this lets the SysML tool run in a separate environment with its
own versions, as long as the exchanged artifacts remain standard-conformant.

The exact boundary contract, artifact classes, and tool-environment rules are
maintained in [Pipeline and Tool Boundaries](pipeline-boundaries.md).

No tool may add compatibility behavior to a producer's Python model merely to
satisfy a consumer. Adapt the consumer or the artifact boundary instead. See
`ADR-006`.

---

## 4. Data Flow

The following text diagram shows the path from model source to comparison
artifact:

```
  models/ssp/<model>/architecture/*.sysml   (SspModel + Study definitions)
           |
           |  build_models.py -> build.py
           |  pyssp_workflow.authoring + pyssp_workflow.execute / pyssp_standard
           |  (SysML -> model SSP; study scenario packaged by the form hook)
           v
  artifacts/models/<model>/<study>/<build>/  (runnable SSP:
                                              SystemStructure.ssd, resources/,
                                              packaged scenario)
  artifacts/studies/<model>/<study>/         (SSV, SSM, study descriptor)
           |
           |  simulation_registry.json maps model -> study -> build -> backends
           v
  artifacts/simulation/<model>/<study>/setup.json   (study setup manifest)
           |
           |  run_simulations.py runs the built SSP as-is per backend
           v
  artifacts/simulation/<model>/<study>/<backend>/
      - config.json
      - result.csv (or result.mat + unpacked CSV)
      - simulation.json (run manifest)
      - simulation.log / stdout.log
           |
           |  run_comparisons.py loads run manifests,
           |  compares backend pairs pairwise
           v
  artifacts/comparisons/<model>/<study>/<backend_a>_vs_<backend_b>/
      - comparison.json (pairwise comparison manifest)
      - metrics.csv (per-signal metrics)
           |
           v
  artifacts/comparisons/<model>/<study>/comparisons.json (batch summary)
```

The flow is strictly left-to-right and top-to-bottom. No stage writes to a
location owned by a previous or subsequent stage.

---

## 5. Runtime Contract

The runtime contract is a chain of four connected artifacts. Each artifact is a
JSON file that records the state, configuration, and provenance of the pipeline
stage that produced it.

### `simulation_registry.json`
Located at `artifacts/simulation_registry.json`. This is the top-level study-
and-backend selection matrix. It lists every model with:
- The signals to compare during post-processing (`compare_signals`).
- One or more named cases, each naming its study, its `build` name, the
  backends to run, reference baselines, and gate policy.

The artifact path is `artifacts/models/<model>/<study>/<build>` and the study
artifacts are at `artifacts/studies/<model>/<study>`.

The registry is the exclusive source of truth for which model/study/backend
combinations are active. It is not derived from the SSP directory tree or from
any `experiments.xml`.

### `setup.json`
Written by `run_simulations.py` before dispatching any backend. Located at
`artifacts/simulation/<model>/<study>/setup.json`. It records:
- The runnable SSP path, study, and build name.
- The study artifact directory.
- The simulation window (start time, stop time, interval) from the study
  descriptor. Tolerance is read from the composed FMUs, not the descriptor.
- The explicit backend list and compare-signal list for this model/study.
- The gate policy (`atol`, `rtol`, invariant tolerance) frozen from the registry.
- The root system name and path to `SystemStructure.ssd`.

The setup manifest is the fixed record of *what was configured*. Later stages
read it without re-parsing `experiments.xml` or the study descriptor.

### Simulation artifacts
One directory per backend per study at
`artifacts/simulation/<model>/<study>/<backend>/`. Each directory contains:
- `simulation.json` — the run manifest recording backend name, result path,
  status, runtime, and error information.
- `result.csv` — the raw simulation trajectory.
- `config.json` — backend configuration payload when the backend produces one
  (currently ssp4sim).
- `simulation.log` / `stdout.log` — diagnostic output when the backend
  produces it.

### Comparison artifacts
Written by `run_comparisons.py`. Pairwise directories at
`artifacts/comparisons/<model>/<study>/<backend_a>_vs_<backend_b>/` containing:
- `comparison.json` — the pairwise comparison manifest.
- `metrics.csv` — per-signal comparison metrics.

A batch summary is written at
`artifacts/comparisons/<model>/<study>/comparisons.json`. Reference comparisons
live under `artifacts/comparisons/<model>/<study>/references/` and use the same
manifest and metrics shape.

### Connection chain

```
  simulation_registry.json
       |
       |  (expands into individual model/study/backend specs)
       v
  artifacts/simulation/<model>/<study>/setup.json
       |
       |  (consumed by backend adapters to produce runs)
       v
  artifacts/simulation/<model>/<study>/<backend>/simulation.json
       |
       |  (loaded by comparison entry point)
       v
  artifacts/comparisons/<model>/<study>/comparisons.json
```

---

## 6. Boundary Rules

The following architectural violations are not allowed:

1. **Build scripts must not run simulations.** The build stage produces
   exported model SSPs and study data only. Any simulation logic in a model's
   `build.py` breaks the pipeline's independent-invocability invariant.

2. **Simulation scripts must not modify model sources.** `run_simulations.py`
   and backend adapters read from built SSP roots but must never write to
   `models/` or `artifacts/models/`.

3. **Comparison scripts must not re-run simulations.** `run_comparisons.py`
   compares existing results only. It must not invoke backend simulation
   adapters directly or indirectly.

4. **`experiments.xml` is packaging metadata, not the runtime contract.**
   For migrated fixtures, the window and step come from the study descriptor and
   are frozen into `setup.json`; tolerance comes from the FMUs. Legacy fixtures
   may still carry `experiments.xml` until migrated. No pipeline stage depends
   on LS-REF conventions at runtime.

5. **Simulation artifacts must not be stored in model directories.** Results,
   configs, logs, and manifests live under `artifacts/simulation/` and
   `artifacts/comparisons/`, never under `models/` or `artifacts/models/`.

6. **Backend-specific logic must not leak into model build scripts.**
   A model's `build.py` builds an SSP. It does not configure, invoke, or
   reference any simulation backend. Backend selection and configuration belong
   to the simulation stage (`run_simulations.py` and the adapter modules).

7. **The simulation registry is the single source of truth for study/backend
   selection.** No pipeline stage derives the run matrix from directory
   scanning, `experiments.xml` content, or any other source.

8. **Library borders exchange standard artifacts first.** The SysML authoring
   path invokes the `pyssp` CLI through `pyssp_workflow.authoring` and exchanges
   SysML/SSP artifacts. Do not import `pyssp_sysml2` into the build. When a
   Python object must cross, it belongs to the producer's public API; internal
   model objects and compatibility shims do not. See `ADR-006`, `ADR-007`, and
   `ADR-011`.

9. **Studies must not be exported as SSPs.** Only `part def ... :> SspModel`
   definitions are exportable. A `part def ... :> Study` produces scenario
   SSV/SSM and experiment data, and is packaged into a build SSP. See
   `ADR-009` and `ADR-013`.

10. **Parameter form is applied where it is known.** Default packaging is a
    root external SSV/SSM binding. A fixture that exercises another form applies
    it with `pyssp_standard` in its build hook. The simulate stage does not
    inject or reshape parameters. See `PD-007` and `ADR-013`.

---

## Document Purpose

This architecture document satisfies the Build → Simulate → Compare pipeline
commitment stated in [00-intent/intent.md](../00-intent/intent.md) by defining the stable
boundaries, interface contracts, and forbidden shortcuts that preserve that
pipeline across changes. Future technical decisions (ADRs) and implementation
work should reference this document as the source of architectural constraints.