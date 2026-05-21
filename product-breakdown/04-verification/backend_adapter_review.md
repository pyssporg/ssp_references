# Backend Adapter Contract Review

**Review ID:** IMP-CAND-H  
**Date:** 2026-05-20  
**Status:** Completed  
**Scope:** Backend adapter contracts between `ssp4sim` and `OMSimulator` in the Simulation Registry and Comparison Pipeline.

## Config Contract

The `SimulationSetup.to_dict()` method (in `scripts/workflow/setup.py`) produces a setup manifest with the following fields:

| Field | Type | Source | Required |
|-------|------|--------|----------|
| `model` | `str` | `layout.model_name` | Yes |
| `case` | `str` | `layout.case_name` | Yes |
| `ssp_root` | `path` (relative to manifest) | `layout.ssp_root` | Yes |
| `window` | `dict` with `start_time`, `stop_time`, `interval` | LS-REF experiments XML | Yes |
| `tolerance` | `float` | LS-REF experiments XML | Yes |
| `backends` | `list[str]` | `SimulationCaseSpec.backends` | Yes |
| `compare_signals` | `list[str]` | `SimulationCaseSpec.compare_signals` | Yes |
| `root_system_name` | `str` | `SystemStructure.ssd` root `<System>` name | Yes |
| `system_structure` | `path` (relative to manifest) | `layout.system_structure_path` | Yes |
| `ls_ref_experiments` | `path` (relative to manifest) | `layout.ls_ref_experiments_path` | Yes |
| `resources_dir` | `path` (relative to manifest) | `layout.resources_dir` | Yes |
| `description` | `str` or `null` | LS-REF experiments XML (`description` attribute) | No |

### Adapter Consumption of Config Fields

| Config Field | `ssp4sim` Adapter | `OMSimulator` Adapter |
|---|---|---|
| `model` / `case` | Used via `SimulationSetup` for layout paths | Used via `SimulationSetup` for layout paths |
| `ssp_root` | Copied to runtime temp dir via `_runtime_ssp_copy()` | Packaged into zip archive via `_runtime_ssp_archive()` |
| `window.start_time` | Written to config.json `simulation.start_time` | Set via `instantiated_model.setStartTime()` |
| `window.stop_time` | Written to config.json `simulation.stop_time` | Set via `instantiated_model.setStopTime()` |
| `window.interval` | Written to config.json `simulation.timestep` | Set via `instantiated_model.setLoggingInterval()` |
| `tolerance` | Written to config.json `simulation.tolerance` | **NOT SET** — see Gap 1 |
| `root_system_name` | Not consumed directly (no prefix in CSV output) | Used in `normalize_column_name()` to strip `{root_system_name}.` prefix from CSV columns |
| `resources_dir` | Not consumed directly | Skimmed for FMU repacking in `_runtime_ssp_archive()` |
| `system_structure` | Not consumed by adapter | Read during `_read_root_system_name()` in setup phase |

## Result CSV Contract

### Format

- **File type:** Standard CSV (`.csv`)
- **Engine format:** First row is headers; all subsequent rows are numeric values (floats)
- **Loading:** `load_numeric_csv()` in `scripts/utils/csv.py`
- **Required column:** `time` (independent variable)
- **Column values:** `numpy.ndarray` of `float64`

### Column Naming

- Raw headers loaded as-is via `csv.reader`, stripped of whitespace
- `normalize_column_name()` strips (in order):
  1. Leading/trailing whitespace
  2. `root.` prefix (OMSimulator output convention, only when `engine="omsimulator"`)
  3. `{root_system_name}.` prefix (when `root_system_name` is provided)
  4. `fmu.` prefix
- `canonicalize_signal_name()` in `scripts/utils/comparison.py` applies the same normalization but preserves `"time"` unmodified
- Comparison uses `canonicalize_signal_name()` for matching selected signals to result columns

### Resampling and Comparison

- `compare_result_sets()` expects a `time` column in both result sets
- Both result sets are resampled to a uniform grid via `build_time_grid(window)` using `np.linspace(start, stop, steps + 1)`
- Missing/NaN times and values are filtered; signals are interpolated with `np.interp()`
- Metrics: `max_abs_error`, `mean_abs_error`, `rmse` per signal plus summary aggregates

## Adapter-Specific Differences

| Aspect | `simulate_ssp4sim()` | `simulate_omsimulator()` |
|--------|----------------------|--------------------------|
| **Config file** | Writes `config.json` via `_ssp4sim_config_payload()` | Does **not** write `config.json` |
| **Result file format** | Direct CSV (`result.csv`) | MAT (`result.mat`) then `unpack_mat_to_csv()` → CSV |
| **Tolerance** | ✅ Written to config (`simulation.tolerance`) | ❌ **Not set** — OMSimulator uses default tolerance |
| **SSP handling** | `_runtime_ssp_copy()` — directory copy via `shutil.copytree` | `_runtime_ssp_archive()` — repack FMUs, zip archive |
| **Process model** | Child process via `multiprocessing.Process` (spawn) | In-process via OMSimulator Python bindings (`SSP`, `Settings`) |
| **Artifacts recorded** | `(config.json, simulation.log)` | `(result.mat,)` |
| **Working directory** | Config key `working_dir` set to `result_file.parent` | `_temporary_cwd` context manager inside `request.run_dir` |
| **Initialization** | `Simulator(config_path).init()` + `.simulate()` | `model.instantiate()`, then `setStartTime`, `setStopTime`, `setLoggingInterval`, `setResultFile`, `initialize()`, `simulate()`, `terminate()`, then `delete()` |
| **Logging** | `simulation.log` via config `simulation.log.file` | No explicit log file (OMSimulator console output only) |
| **Executor config** | Config includes full executor block (jacobi method, thread pool, etc.) | Not applicable (in-process) |
| **Recording config** | Config includes full recording block (CSV, InfluxDB) | Not applicable (MAT output handled by OMSimulator) |
| **Stray artifacts cleanup** | Not needed | Cleans up `result/` directory created by OMSimulator (`shutil.rmtree`) |
| **Consumed config fields** | `window.*`, `tolerance`, `ssp_root` | `window.*`, `ssp_root`, `root_system_name` (via CSV normalization) |
| **Error handling** | Checks `process.exitcode != 0`, raises `RuntimeError` | Exception propagates from Python bindings; `finally` block calls `instantiated_model.delete()` |
| **Result validation** | Checks `request.result_path.is_file()` after simulation | Checks `request.result_path.is_file()` after MAT-to-CSV conversion |

## Gaps and Findings

### Gap 1: OMSimulator Tolerance Not Set

`simulate_omsimulator()` does not call `setTolerance()` on the instantiated model. The tolerance value parsed from LS-REF experiments (`setup.tolerance`) is available but unused.

**Impact:** OMSimulator may use its default tolerance (typically `1e-4`), while `ssp4sim` receives the explicit tolerance from the setup. If the fixture expects a different tolerance (e.g., `1e-6`), comparison metrics may show larger discrepancies that are purely due to solver tolerance mismatch.

**Location:** `scripts/workflow/simulate.py`, `simulate_omsimulator()`, lines 457–468.

### Gap 2: No Config.json for OMSimulator

`simulate_omsimulator()` does not produce a `config.json` artifact. This means:
- The OMSimulator run lacks a structured record of the parameters used
- `simulate_ssp4sim` archives `(config.json, simulation.log)`, while OMSimulator archives only `(result.mat,)`
- Reproducing an OMSimulator run requires reconstructing parameters from the setup manifest and the simulation run manifest

**Impact:** Diagnostic asymmetry between backends. A failed OMSimulator run has less instrumentation than a failed ssp4sim run.

**Location:** `scripts/workflow/simulate.py`, `simulate_omsimulator()`, artifacts tuple at line 483.

### Gap 3: Backlog Item References Nonexistent Adapter Files

The backlog item `IMP-CAND-H` refers to `scripts/workflow/ssp4sim_adapter.py` and `scripts/workflow/omsimulator_adapter.py`. These files do not exist; the adapter logic is in `scripts/workflow/simulate.py` as functions `simulate_ssp4sim()` and `simulate_omsimulator()`.

**Impact:** Misleading file references in documentation. A developer searching for adapter files will not find them.

**Location:** Backlog item `IMP-CAND-H`, Task Contract Seed section.

### Gap 4: OMSimulator Creates Stray `result/` Directory

OMSimulator writes per-component result files to a `result/` directory under the current working directory (inside `_temporary_cwd` context). This directory is cleaned up via `shutil.rmtree` after MAT-to-CSV conversion.

**Impact:** Minor — cleanup is already in place. But the stray directory indicates OMSimulator-side output that is not captured by the pipeline (component-level MAT files are discarded in favor of the aggregated `result.mat`).

**Location:** `scripts/workflow/simulate.py`, `simulate_omsimulator()`, lines 473–475.

### Finding 5: Column Normalization Order Dependency

`normalize_column_name()` checks engine-specific prefix (`root.`) before checking `root_system_name` prefix and `fmu.` prefix. The order matters:
- If an OMSimulator output column is `root.{root_system_name}.signal_name`, the `root.` prefix is stripped first, then `{root_system_name}.` is stripped.
- If the CSV has `root.fmu.signal_name`, the `root.` prefix is stripped (for OMSimulator), then `fmu.` prefix is stripped.

**Status:** Confirmed correct behavior for current fixtures. No action required, but any future prefix conventions must account for this ordering.

## Recommendations

1. **Set OMSimulator tolerance:** Add `instantiated_model.setTolerance(setup.tolerance)` after `setStopTime()` in `simulate_omsimulator()`. This closes Gap 1 and ensures both adapters use the same tolerance for equivalent comparisons.

2. **Consider OMSimulator config artifact:** Optionally write a lightweight config.json (or equivalent run metadata) for OMSimulator to improve diagnostic symmetry. This is lower priority than tolerance.

3. **Update backlog file references:** Correct the backlog item to reference `scripts/workflow/simulate.py` functions instead of the nonexistent `*_adapter.py` files.

4. **Document prefix stripping order:** Add a docstring or comment to `normalize_column_name()` explicitly stating the stripping order (whitespace → `root.` (omsimulator) → `{root_system_name}.` → `fmu.`). This makes the dependency explicit for future maintainers.

## Traceability

### Forward Trace

- **Config shape** → `scripts/workflow/setup.py`, `SimulationSetup.to_dict()`
- **SSP4sim adapter** → `scripts/workflow/simulate.py`, `simulate_ssp4sim()`, `_ssp4sim_config_payload()`
- **OMSimulator adapter** → `scripts/workflow/simulate.py`, `simulate_omsimulator()`, `_runtime_ssp_archive()`
- **CSV loading** → `scripts/utils/csv.py`, `load_numeric_csv()`
- **Column normalization** → `scripts/utils/csv.py`, `normalize_column_name()`
- **Signal canonicalization** → `scripts/utils/comparison.py`, `canonicalize_signal_name()`
- **Comparison** → `scripts/utils/comparison.py`, `compare_result_sets()`
- **MAT-to-CSV** → `scripts/utils/csv.py`, `unpack_mat_to_csv()`

### Backward Trace

- **Architecture context** → `02-architecture/architecture.md` (Pipeline stage contracts)
- **Implementation context** → `03-implementation/` (Adapter source code)
- **Backlog origin** → `06-evolution/backlog/IMP-CAND-H-backend-adapter-review.md`
- **Review plan** → `06-evolution/backlog/complete/review-plan.md`, Item 2
- **Verification layer** → `04-verification/README.md`

### Related Documents

- [Simulation Registry Coverage Review](./simulation_registry_coverage_review.md) — companion review for registry coverage (IMP-CAND-G)
- [Co-Simulation Test Strategy](./co_simulation_test_strategy.md) — overall test flow (prepare, simulate, compare)
- [Co-Simulation Fixture Mapping](./co_simulation_fixture_mapping.md) — fixture-to-strategy mapping