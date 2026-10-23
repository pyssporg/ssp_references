---
id: EVAL-004
type: eval
title: Backend Adapter Contract Review
summary: Contract between the setup manifest, the local simulate wrapper, and the pyssp_simulate backends.
date: 2026-10-23
status: current
pb_exempt: true
---

# Backend Adapter Contract Review

**Review ID:** IMP-CAND-H
**Scope:** backend adapter contract between the Simulation Registry, the setup
manifest, and `pyssp_simulate`.

## Config Contract

`SimulationSetup.to_dict()` in `scripts/workflow/setup.py` produces the setup
manifest. It records:

- `model`, `case`, and `ssp_root` from the artifact layout.
- `window` with `start_time`, `stop_time`, and `interval` from `study.json`.
- `backends` and `compare_signals` from the registry case.
- `root_system_name` from the root `<System>` in `SystemStructure.ssd`.
- `gate` with `atol`, `rtol`, and `max_invariant_abs_error` from the registry.
- `system_structure` and `resources_dir`, relative to the manifest.
- `tolerance` only when the manifest was loaded with one; a fresh setup carries
  none.
- `description`, `study`, and `study_root` when the registry case supplies them.

## Adapter Consumption of Config Fields

`scripts/workflow/simulate.py` builds one `SimulationSpec` per backend and calls
`pyssp_simulate.simulate`. The spec carries `fixed_step=False`,
`validate_ssd=False`, and `omsimulator_options`, so no engine workaround stays
in this repository.

- **SSP root:** `prepare_runtime_ssp` writes a temporary runtime copy; the
  caller's build SSP is never modified.
- **Window:** `start_time`, `stop_time`, and `step_size` come from
  `setup.window`.
- **Tolerance:** `spec.tolerance` is the manifest value, or `None`.
- **Fixed step:** `fixed_step=False` keeps OMSimulator event handling; other
  backends ignore it.
- **SSD validation:** `validate_ssd=False` skips FMPy's bundled SSP 1.0 schema
  check; other backends ignore it.
- **Engine options:** `omsimulator_options` applies the repository option tuple
  process-wide before the run.
- **Root system:** result canonicalization uses the runtime container names;
  `setup.root_system_name` feeds comparison and model policy.

## Result CSV Contract

- **Loading:** `pyssp_simulate.read_result_csv`.
- **Column naming:** `canonicalize_signal` strips runtime container names, so
  `fmu.h` becomes `h`; `time` stays unchanged.
- **Comparison:** `pyssp_workflow.execute.compare_result_csvs` loads two result
  CSVs and measures through `pyssp_vv.measure`; the metric-row schema is
  `pyssp_vv.evidence`. Gate policy stays local in `scripts/workflow/gate.py`.

## Adapter-Specific Differences

- **ssp4sim:** runs in a child process; keeps unpacked FMU directories in the
  runtime package (`repackage_fmus=False`); writes `config.json` and
  `ssp4sim.log`; writes `result.csv`. The engine rejects a configuration
  without `simulation.tolerance`, so composition supplies
  `BACKEND_REQUIRED_TOLERANCE` and records it in `simulation.json`.
- **OMSimulator:** runs in-process through the Python bindings; sets start
  time, stop time, and logging interval; sets a fixed step only when
  `fixed_step` is true; sets the tolerance only when the spec carries one;
  writes `result.csv` and no `config.json`.
- **FMPy:** runs in-process; resolves system-boundary connections with its own
  traversal; applies only the parameter set the system definition declares;
  uses a fixed-step Jacobi scheme.

## Findings

- **No local engine patch.** FMPy boundary mapping and OMSimulator step
  handling live in `pyssp_simulate`; this repository keeps neither (`DD-013`).
- **OMSimulator runs in-process.** A malformed fixture can abort the host
  process; the campaign runner isolates each simulation in a subprocess.
- **ssp4sim needs the pinned wheel.** Only Linux `x86_64` wheels are published
  for the tested version.
- **FMPy has simple SSP support.** It records SSD connector values and
  validates against its bundled SSP 1.0 schema, so SSP 2.0 details need the
  validation bypass.

## Traceability

### Forward Trace

- **Config shape:** `scripts/workflow/setup.py`, `SimulationSetup.to_dict()`.
- **Simulation spec:** `scripts/workflow/simulate.py`, `_simulation_spec()`.
- **Engine execution:** `pyssp_simulate.simulate` and its internal backends.
- **Result CSV:** `pyssp_simulate.read_result_csv`, `canonicalize_signal`.
- **Comparison composition:** `pyssp_workflow.execute.compare_result_csvs`.
- **Measurement:** `pyssp_vv.measure`.
- **Gate:** `scripts/workflow/gate.py`.

### Backward Trace

- **Architecture context:** `INFO-002` (stage contracts), `INFO-003` (boundary contract).
- **Implementation context:** `INFO-008` (build, study, and runtime workflow).
- **Review origin:** `IMP-CAND-H`.
- **Verification layer:** `04-verification/README.md`.

### Related Documents

- `EVAL-007` - registry coverage review.
- `EVAL-001` - co-simulation test strategy.
- `EVAL-003` - fixture-to-strategy mapping.
