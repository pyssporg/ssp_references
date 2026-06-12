# System Simulation Use-Case Coverage Analysis

## Status

Updated 2026-06-12 — re-reviewed against current fixture suite; all coverage gaps UC-1 through UC-16 closed.

## Purpose

Define the taxonomy of system simulation use-cases that the fixture suite should
cover, map existing tests against it, identify coverage gaps, and establish a
framework for prioritizing new fixture and test work based on functional
coverage rather than low-level programmatic verification.

## Taxonomy

| ID | Use-Case | Description | Priority | Coverage | Gap Assessment |
|----|----------|-------------|----------|----------|----------------|
| UC-1 | Single-component simulation | Simulate a single FMU wrapped as an SSP | High | ✅ Covered | Covered by simple reference models (BouncingBall, VanDerPol, Dahlquist, Stair, Resource) — single-FMU SSPs built, registered, simulated across 2–3 backends, with comparison signals and reference CSVs. No standalone "single-FMU-SSP" test function isolates this as a named test, but functional coverage exists. No new fixture needed. |
| UC-2 | Multi-component signal routing | Wire two or more FMUs; verify signal reaches the right inputs | High | ✅ Covered | Covered by signal_step_gain, signal_step_add, signal_step_product, signal_delay_detector — all wire multiple FMUs, registered, simulated across backends. No pipeline-level test named after this use-case exists, but the fixtures exercise it end-to-end. |
| UC-3 | Arithmetic signal propagation | Gain, add, product blocks propagate correct values | High | ✅ Covered | Covered by signal_step_gain, signal_step_add, signal_step_product, signal_sine_gain_add — each exercises specific arithmetic operations through wired SSPs with registered comparison signals. |
| UC-4 | Signal fan-out | One source → many receivers; verify all receive the same signal | High | ✅ Covered | Covered by signal_fanout_gain — one-source, multiple-receiver SSP, registered across 3 backends (ssp4sim, OMSimulator, FMPy), built and simulated with comparison signals. |
| UC-5 | Algebraic loops | Feed-through, cyclic dependencies, simultaneous equations | High | ✅ Covered | Covered by signal_algebraic_loop (3 comparison signals, 2 backends) and signal_nested_algebraic_loop (5 comparison signals, 2 backends). Both built, registered, simulated, and compared through the standard pipeline. The test `test_registry_includes_algebraic_loop_fixtures` confirms registry presence. |
| UC-6 | Nested system hierarchy | Sub-SSPs, hierarchical composition | Medium | ✅ Covered | Covered by signal_nested_algebraic_loop, signal_nested_parameter_bindings, signal_nested_external_bindings, signal_nested_pass_through — all are nested SSP structures with sub-systems, registered and simulated across backends. |
| UC-7 | Parameter binding — inline SSV | Parameters supplied inline in SSD | High | ✅ Covered | Covered by signal_parameter_inline_with_mapping — exercises inline `<ssd:ParameterValues>` within SSP structure, registered across ssp4sim+OMSimulator backends, simulated with 1 comparison signal. |
| UC-8 | Parameter binding — external SSV | Parameters loaded from separate .ssv file | High | ✅ Covered | Covered by signal_nested_external_bindings — exercises external SSV parameter bindings in a nested SSP, registered and simulated across 2 backends with 2 comparison signals. |
| UC-9 | Parameter binding — mixed precedence | External SSV + inline, verify precedence rules | High | ✅ Covered | Covered by signal_nested_parameter_bindings — exercises mixed inline+external+SSM parameter bindings with multiple binding levels, registered and simulated across 2 backends with 5 comparison signals. |
| UC-10 | Parameter binding — SSM mapping | Parameter mapping via .ssm file | Medium | ✅ Covered | Covered by signal_parameter_inline_with_mapping (inline SSV + SSM mapping) and signal_nested_pass_through (nested SSM pass-through). Both built, registered, simulated, and compared in the pipeline. |
| UC-11 | Cross-engine comparison | Compare outputs from different backends | High | ✅ Covered | Covered by the standard comparison pipeline (`run_comparisons.py`) which compares real simulation outputs across ssp4sim, OMSimulator, and FMPy for all 20 registered models. Tests `test_compare_runs_writes_metrics_and_manifest`, `test_compare_runs_normalizes_prefixed_signal_names`, and `test_compare_run_batch_writes_results_for_multiple_backends` verify the comparison infrastructure. No longer synthetic-only — real cross-engine comparison is operational. |
| UC-12 | Pipeline integrity | Build → Simulate → Compare end-to-end | High | ✅ Covered | Covered by full integration test `test_full_pipeline_build_simulate_compare` in `tests/test_pipeline_integration.py` — exercises build→simulate→compare chain for signal_step_gain with 3 backends, verifies all manifests, round-trips, and comparison metrics. |
| UC-13 | Simulation registry management | Registry add/remove/query, case management | Medium | ✅ Covered | Covered by existing `test_registry` functions. No action needed. |
| UC-14 | Manifest round-trip | Setup → simulation → comparison manifest chain | Medium | ✅ Covered | Covered by existing `test_manifest_roundtrip`. No action needed. |
| UC-15 | Signal name normalization | Signal name mapping across backends | Low | ✅ Covered | Covered by existing `test_signal_name_normalization`. No action needed. |
| UC-16 | MAT-to-CSV extraction | Convert .mat results to CSV for comparison | Low | ✅ Covered | Covered by existing `test_mat_to_csv_extraction`. No action needed. |

## Engine-Level Verification Tests (Flagged for Transfer)

Two existing tests in this repository perform low-level function verification
that belongs in the simulation engine repositories, not in this fixture suite:

| Test | File | Reason | Target Repository |
|------|------|--------|-------------------|
| `test_reference_csvs_are_not_inverted` | `tests/test_workflow.py` | Checks specific numeric cell values in reference CSVs — value-level correctness verification of reference data | Engine repository (ssp4sim or equivalent) |
| `test_modelica_block_fmus_expose_dependency_metadata` | `tests/test_workflow.py` | Parses FMU modelDescription.xml and checks dependency attribute strings — FMU metadata structure verification | Modelica compiler or FMU export repository |

**Action:** Transfer these tests to the appropriate engine repositories. Once
confirmed, remove them from `tests/test_workflow.py` in this repository.

## Coverage Review Cadence

The coverage matrix should be reviewed and updated each improvement cycle:

1. For each newly-closed gap, update the Coverage column and Gap Assessment.
2. If a new fixture or test type is added, assess whether it introduces a new
   use-case not covered by UC-1 through UC-16.
3. If a use-case is found to be irrelevant or duplicate, mark it as
   `Deprecated` with a note, but keep its row for traceability.

## Traceability

- **Source:** IMP-011 candidate (`product-breakdown/06-evolution/backlog/complete/IMP-011.md`)
- **Product:** PD-002 (fixture hierarchy) — the taxonomy maps directly to fixture classes
- **Architecture:** ADR-001 (pipeline), ADR-002 (fixture hierarchy), ADR-003 (registry), ADR-004 (coverage taxonomy)
- **Verification:** `co_simulation_test_strategy.md` references this taxonomy as the primary coverage lens
- **Backlog:** `improvement-backlog.md` cross-references this analysis document instead of embedding the matrix
