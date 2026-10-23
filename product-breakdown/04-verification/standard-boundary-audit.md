---
id: EVAL-009
type: eval
title: Standard-artifact boundary audit
summary: SSP, SSV, SSM, and SSD pass through pyssp_standard; comparison passes through pyssp_vv; non-standard crossings use public API only.
date: 2026-10-22
status: current
---

# Standard-artifact boundary audit

## Current boundary

- Study generation emits standard SSV, SSM, and repo `study.json`.
- Build packages the same SSV/SSM through
  `pyssp_standard.SSP.add_external_parameterset`; the build SSP is the engine
  input and simulation does not mutate it.
- Result CSV reading and writing use `pyssp_simulate.read_result_csv` and `write_result_csv`.
- Signal names canonicalize through `pyssp_simulate.canonicalize_signal`, including the two-segment `fmu.h` form.
- LS-REF experiment windows parse through `pyssp_standard.LSRefExperiments`
  (legacy fixtures only).
- Raw SSP packaging uses `pyssp_standard.package_archive`.
- Comparison alignment, resampling, metric families, global shift search, and local shift primitive live in `pyssp_vv.measure`.
- Gate judgment lives in `pyssp_vv.judge`; `pass`, `fail`, and `invalid` stay distinct.
- Model signal invariants live in `workflow/model_policy.py`, not a generic utility.
- `pyssp_workflow.authoring` returns the `study.json` descriptor path; it does not mirror `pyssp_sysml2.study.StudyArtifacts`.
- Shared workflow records live in `utils.domain`; no duplicate `SimulationWindow` or `ResultSet`.

## Public API surfaces

- `pyssp_standard`: `SSP`, `SSD`, `SSV`, `SSM`, `FMU`, `ModelDescription`,
  LS-REF types, archive helpers, and their documented model aliases.
- `pyssp_simulate`: `SimulationSpec`, `SimulationResult`, `RuntimeSSP`,
  `prepare_runtime_ssp`, result CSV helpers, and the backend registry.
- `pyssp_vv`: `Trajectory`, `Comparison`, `SignalMetrics`, `Policy`,
  `Judgment`, `Verdict`, and `EvidenceBundle`.
- `pyssp_workflow`: `package_scenario`, `read_study_descriptor`, authoring
  functions, and the optional node layer.
- `pyssp_sysml2`: the `pyssp` CLI and documented generation functions.
- `sequence_extensions`: `node`, `execute_flow`, `RunOptions`, and flow
  results.

A non-standard crossing uses only these surfaces. A new public type is a
deliberate API decision, not an accidental export. See `ADR-011`.

## Open smells

- None at the standard-artifact boundary.

## Intentional exceptions

- `engine_compat.py` and `_apply_fmpy_mapping` cover upstream FMPy and OMSimulator gaps.
- `setup._read_root_system_name` stays lenient; the `SSD` facade requires conformant root metadata.
- `check_sysml_roundtrip.py` stays artifact-only; it does not import `pyssp_standard`.
- `study.json` is repository policy; SSV and SSM remain the standard interchange.
- Gate policy applies the `pyssp_vv.measure.local_shift_error` primitive with the repository's first/last two sample exclusion.
