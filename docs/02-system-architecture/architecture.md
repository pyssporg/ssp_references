# System Architecture

This document describes the stable guarantees, component boundaries, and
interface contracts of the `ssp_references` repository. It sits at the
**System Architecture** layer in the documentation chain, between
[docs/00-intent/intent.md](../00-intent/intent.md) (Intent and Product Commitments) and any future
Technical Decisions records.

---

## 1. Three-Stage Pipeline

The repository's core workflow is a three-stage pipeline. Each stage is
independently invocable — it consumes only its own inputs, produces only its
own outputs, and has no side effects on the data of any other stage. The three
stages are connected by file-based interface contracts, not by shared memory,
inter-process calls, or hidden state.

### Stage 1: Build

**Purpose:** Transform an authored model definition into a reproducible,
runtime-ready SSP artifact.

**Input:** A model directory under `models/ssp/<model_name>/` containing at
minimum a `build.py` script and a `FIXTURE.md` fixture note. Some model
directories also carry an `experiments.xml` for variant SSP assembly and
checked-in or generated resource files (`.ssv`, `.ssm`, FMUs).

**Output:** A built SSP root directory at
`artifacts/models/<model_name>/<experiment_name>/` containing the unpacked SSP
structure — `SystemStructure.ssd`, `resources/`, and an
`extra/org.fmi-standard.fmi-ls-ref/experiments.xml`.

**Entry point:** `scripts/build_models.py` discovers and dispatches to each
model's own `build.py`. The model-level build script is the source of truth for
how that particular SSP gets assembled.

**Invariant:** The build stage does not execute simulations, does not write to
`artifacts/simulation/` or `artifacts/comparisons/`, and does not modify
`artifacts/simulation_registry.json`.

### Stage 2: Simulate

**Purpose:** Run registered simulation cases against one or more simulation
backends and record raw result trajectories.

**Input:** A built SSP root (from Stage 1) plus the simulation registry
at `artifacts/simulation_registry.json` that maps each model to its named
cases, backends, and compare-signal lists. The simulation entry point reads
`experiments.xml` inside the built SSP to determine the simulation window
(start time, stop time, step size).

**Output:** Per-backend simulation result files (CSV, and optionally `.mat`
for some backends) under
`artifacts/simulation/<model_name>/<case_name>/<backend>/`. Each run also
produces a `simulation.json` run manifest at the same location.

**Entry point:** `scripts/run_simulations.py` reads the registry, expands the
model/case/backend matrix, prepares setup manifests, and dispatches to the
appropriate backend adapter.

**Invariant:** The simulate stage does not rebuild SSPs, does not modify model
source directories, and does not run comparisons.

### Stage 3: Compare

**Purpose:** Compare simulation results across different backends and produce
pairwise metrics.

**Input:** Simulation run manifests (from Stage 2) referencing result CSV files,
plus the compare-signal list from the setup manifest. Comparison is always
engine-to-engine — at least two distinct backend runs are required.

**Output:** Per-pairwise-comparison metrics CSV files and comparison manifests
under
`artifacts/comparisons/<model_name>/<case_name>/<backend_a>_vs_<backend_b>/`.
A batch-level comparison manifest is also written at
`artifacts/comparisons/<model_name>/<case_name>/comparisons.json`.

**Entry point:** `scripts/run_comparisons.py` reads the registry, loads the
setup and run manifests, and drives the comparison.

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
| `build_models.py` | Model discovery and dispatch to per-model `build.py` | Running simulations, writing to `artifacts/simulation/` or `artifacts/comparisons/`, modifying the simulation registry |
| `run_simulations.py` | Registry expansion, simulation setup, backend dispatch, result recording | Rebuilding SSPs, modifying model source directories, running comparisons |
| `run_comparisons.py` | Pairwise engine-to-engine comparison, metrics computation, comparison manifest writing | Re-running simulations, modifying model sources, rebuilding SSPs |

These boundaries ensure that each stage can be invoked, debugged, and tested
independently. A build script failure does not corrupt simulation results; a
simulation failure does not block comparison of already-valid runs.

---

## 4. Data Flow

The following text diagram shows the path from model source to comparison
artifact:

```
  models/ssp/<model>/build.py     (authored model definition)
           |
           |  build_models.py dispatches to per-model build.py
           v
  artifacts/models/<model>/<case>/ (built SSP root: SystemStructure.ssd,
                                    resources/, experiments.xml)
           |
           |  simulation_registry.json maps model -> cases -> backends
           v
  artifacts/simulation/<model>/<case>/setup.json   (per-case setup manifest)
           |
           |  run_simulations.py dispatches per backend
           v
  artifacts/simulation/<model>/<case>/<backend>/
      - config.json
      - result.csv (or result.mat + unpacked CSV)
      - simulation.json (run manifest)
      - simulation.log / stdout.log
           |
           |  run_comparisons.py loads run manifests,
           |  compares backend pairs pairwise
           v
  artifacts/comparisons/<model>/<case>/<backend_a>_vs_<backend_b>/
      - comparison.json (pairwise comparison manifest)
      - metrics.csv (per-signal metrics)
           |
           v
  artifacts/comparisons/<model>/<case>/comparisons.json (batch summary)
```

The flow is strictly left-to-right and top-to-bottom. No stage writes to a
location owned by a previous or subsequent stage.

---

## 5. Runtime Contract

The runtime contract is a chain of four connected artifacts. Each artifact is a
JSON file that records the state, configuration, and provenance of the pipeline
stage that produced it.

### `simulation_registry.json`
Located at `artifacts/simulation_registry.json`. This is the top-level case-and-
backend selection matrix. It lists every model with:
- The signals to compare during post-processing (`compare_signals`).
- One or more named cases, each listing the backends to run.

The registry is the exclusive source of truth for which model/case/backend
combinations are active. It is not derived from the SSP directory tree or from
any `experiments.xml`.

### `setup.json`
Written by `run_simulations.py` before dispatching any backend. Located at
`artifacts/simulation/<model>/<case>/setup.json`. It records:
- The SSP root path.
- The simulation window (start time, stop time, interval).
- The tolerance and description from `experiments.xml`.
- The explicit backend list and compare-signal list for this model/case.
- The root system name and paths to `SystemStructure.ssd` and `experiments.xml`.

The setup manifest is the fixed record of *what was configured*. Later stages
read it without re-parsing `experiments.xml`.

### Simulation artifacts
One directory per backend per case at
`artifacts/simulation/<model>/<case>/<backend>/`. Each directory contains:
- `simulation.json` — the run manifest recording backend name, result path,
  status, runtime, and error information.
- `result.csv` — the raw simulation trajectory.
- `config.json` — backend-specific configuration payload.
- `simulation.log` / `stdout.log` — diagnostic output.

### Comparison artifacts
Written by `run_comparisons.py`. Pairwise directories at
`artifacts/comparisons/<model>/<case>/<backend_a>_vs_<backend_b>/` containing:
- `comparison.json` — the pairwise comparison manifest.
- `metrics.csv` — per-signal comparison metrics.

A batch summary is written at
`artifacts/comparisons/<model>/<case>/comparisons.json`.

### Connection chain

```
  simulation_registry.json
       |
       |  (expands into individual SimulationCaseSpec entries)
       v
  artifacts/simulation/<model>/<case>/setup.json
       |
       |  (consumed by backend adapters to produce runs)
       v
  artifacts/simulation/<model>/<case>/<backend>/simulation.json
       |
       |  (loaded by comparison entry point)
       v
  artifacts/comparisons/<model>/<case>/comparisons.json
```

---

## 6. Forbidden Shortcuts

The following architectural violations are not allowed:

1. **Build scripts must not run simulations.** The build stage produces SSP
   artifacts only. Any simulation logic in a model's `build.py` breaks the
   pipeline's independent-invocability invariant.

2. **Simulation scripts must not modify model sources.** `run_simulations.py`
   and backend adapters read from built SSP roots but must never write to
   `models/` or `artifacts/models/`.

3. **Comparison scripts must not re-run simulations.** `run_comparisons.py`
   compares existing results only. It must not invoke backend simulation
   adapters directly or indirectly.

4. **`experiments.xml` is packaging metadata, not the runtime contract.**
   The simulation window and tolerance are read from `experiments.xml` at setup
   time and frozen into `setup.json`. Runtime dispatch reads `setup.json`, not
   `experiments.xml`. No pipeline stage depends on LS-REF conventions at
   runtime.

5. **Simulation artifacts must not be stored in model directories.** Results,
   configs, logs, and manifests live under `artifacts/simulation/` and
   `artifacts/comparisons/`, never under `models/` or `artifacts/models/`.

6. **Backend-specific logic must not leak into model build scripts.**
   A model's `build.py` builds an SSP. It does not configure, invoke, or
   reference any simulation backend. Backend selection and configuration belong
   to the simulation stage (`run_simulations.py` and the adapter modules).

7. **The simulation registry is the single source of truth for case/backend
   selection.** No pipeline stage derives the run matrix from directory
   scanning, `experiments.xml` content, or any other source.

---

## Document Purpose

This architecture document satisfies the Build → Simulate → Compare pipeline
commitment stated in [docs/00-intent/intent.md](../00-intent/intent.md) by defining the stable
boundaries, interface contracts, and forbidden shortcuts that preserve that
pipeline across changes. Future technical decisions (ADRs) and implementation
work should reference this document as the source of architectural constraints.