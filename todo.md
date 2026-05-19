# Simulation Comparison Plan

The goal is to compare simulations between different engines with a simple
three-stage workflow:

1. Build stand-alone SSPs.
2. Run registered simulation cases with one or more backends.
3. Compare the produced trajectories.

## Current Direction

- `build.py` stays SSP-only.
- `artifacts/simulation_registry.json` maps each model to one or more case
  definitions, and each case lists its explicit backends.
- Each generated `setup.json` repeats that backend list so later stages do not
  rely on hidden defaults.
- `scripts/run_simulations.py` writes setup and run manifests under
  `artifacts/simulation/<model>/<case>/`.
- `scripts/run_comparisons.py` writes comparison artifacts under
  `artifacts/comparisons/<model>/<case>/` and compares all unique backend
  combinations from the selected setup by default.
- The setup, simulation, and comparison manifests are the fixed interface
  between stages.

## Review Plan

1. Review the registry coverage and confirm which model/case/backend
   combinations should be kept in the registry.
2. Review backend adapters for `ssp4sim` and `OMSimulator` against the current
   config shape and result CSV contract.
3. Review the setup manifest and run manifest fields for anything that is still
   missing or redundant.
4. Review comparison metrics and decide which are gate-worthy versus
   diagnostic-only.
5. Review whether additional backends or model cases should be added to the
   registry once the first comparison path is stable.

## Open Questions For Further Review

- Which summary metrics should become acceptance criteria?
- Which additional registry entries should be added?

## Current Decisions

Each entry records the decision, context, rationale, and consequences.

### 1. Simulation Settings Belong to the Runtime Layer, Not `experiments.xml`

**Context:** Early discussions considered using `experiments.xml` (from the
LS-REF convention) as the runtime configuration source for simulation dispatch.

**Chosen approach:** The simulation window is read from `experiments.xml` at
setup time and frozen into `setup.json`. The runtime layer
(`run_simulations.py` and backend adapters) reads from `setup.json`, not from
`experiments.xml` directly.

**Rationale:** Decouples the build pipeline (which produces SSPs with LS-REF
metadata) from the simulation pipeline (which needs a stable, flat configuration
file). Keeps `experiments.xml` as packaging metadata without making it the
runtime contract. Avoids re-parsing XML on every simulation dispatch.

**Consequences:** `setup.json` must be regenerated if the experiment window or
tolerance changes. The `experiments.xml` file must still be present and valid
in each built SSP root because it is the source of truth at setup time.

### 2. Comparison Is Engine-to-Engine Only

**Context:** The repository could compare results against analytical
expectations, CSV baselines, or other engineered references.

**Chosen approach:** Comparison is always pairwise engine-to-engine. At least
two distinct backend runs are required. Baselines stored under
`models/fmu/<model>/references/` are used as fixture reference data, not as
comparison targets in the pipeline.

**Rationale:** Engine-to-engine comparison detects behavioral differences in
the orchestration layer without requiring analytical truth for every fixture.
It keeps the comparison pipeline symmetric and avoids maintaining
engine-specific pass/fail criteria for each model.

**Consequences:** A single-backend run cannot be compared. Adding a new backend
requires at least one other backend run for the comparison to produce results.
Absolute correctness checks against analytical solutions are out of scope.

### 3. Runtime Artifacts Stay Under `artifacts/`, Not Inside SSP Trees

**Context:** Simulation results could be stored next to each model's build
output under `artifacts/models/<model>/<case>/`.

**Chosen approach:** Runtime artifacts live in
`artifacts/simulation/<model>/<case>/` and
`artifacts/comparisons/<model>/<case>/`, completely separate from build
artifacts under `artifacts/models/`.

**Rationale:** Keeps build output immutable once produced. Simulation and
comparison runs can be cleaned or re-run without affecting the built SSPs.
Prevents accidental coupling between build logic and runtime configuration.

**Consequences:** Three parallel directory trees under `artifacts/` (models,
simulation, comparisons). Cleanup must target each tree independently.

### 4. `build.py` Remains Build-Only

**Context:** A model's `build.py` could optionally run a smoke simulation after
building to validate the SSP immediately.

**Chosen approach:** `build.py` is strictly build-only. It transforms an
authored model definition into a built SSP root. It does not invoke any
simulation backend, write runtime configs, or register cases.

**Rationale:** Keeps the build stage fast and isolated. Simulation failures do
not block the build pipeline. Each stage can be invoked independently for
debugging or incremental work.

**Consequences:** Validation of a built SSP requires a separate simulation step.
There is no "build and smoke test" shortcut at the model level.

### 5. Signal-Propagation Fixtures Use Deterministic Algebraic FMU Building Blocks

**Context:** Test fixtures could be built from any available FMU, including
complex physical models with nonlinear dynamics.

**Chosen approach:** Signal-propagation fixtures are assembled from small,
deterministic, algebraic FMU blocks (sources, gains, adders, products) with
algebraically predictable output.

**Rationale:** These fixtures isolate engine orchestration behavior from
physical-model complexity. When a propagation test fails, the likely problem
is in scheduling, data exchange, or connector handling rather than in the
model itself. The predictable output makes cross-engine comparison
straightforward with very tight tolerances.

**Consequences:** Adds a dedicated fixture class that must be maintained
separately from the simple reference and composite models. Packaging
alternatives (external SSV, generated SSV, inline parameters) must be
exercised across these fixtures to cover the parameter-passing surface.

### 6. Simulation Registry Is the Single Source of Truth for Case/Backend Selection

**Context:** The run matrix could be derived from directory scanning of built
SSPs, from `experiments.xml` content, or from a registry file.

**Chosen approach:** `artifacts/simulation_registry.json` is the exclusive
source of truth for which model/case/backend combinations are active.

**Rationale:** A single explicit registry avoids hidden defaults, makes the
active test matrix visible without running any code, and allows selective
enablement/disablement of cases without modifying model sources or build
scripts.

**Consequences:** Adding a new model or case requires a registry update.
Removing a case requires only a registry change (no rebuild needed as long
as the SSP root already exists).
