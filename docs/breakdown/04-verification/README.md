---
title: Verification
summary: How claims about models, studies, and backends are checked.
---

# Verification

How claims about models, studies, and backends are checked.

## Contents

<!-- pb:index:start -->
<!-- GENERATED FILE — do not edit. Regenerate with pb-registers. -->
- **EVAL-001** [Co-Simulation Engine Test Strategy](co_simulation_test_strategy.md) — Prepare an exported model and study, simulate every registered backend, compare results.
- **EVAL-002** [Ecosystem Adoption Assessment](ecosystem_adoption_assessment.md) — Fit of pyssp_simulate, pyssp_sysml2, pyssp_vv, and sequence_extensions to the fixture suite.
- **EVAL-003** [Co-Simulation Fixture Mapping](co_simulation_fixture_mapping.md) — Fixture classes mapped to the test strategy and oracles.
- **EVAL-004** [Backend Adapter Contract Review](backend_adapter_review.md) — Contract between the setup manifest, the local simulate wrapper, and the pyssp_simulate backends.
- **EVAL-005** [Comparison Metrics Gate Review](comparison_metrics_gate_review.md) — Metric schema from pyssp_vv.evidence and the gate rules implemented in the local workflow.
- **EVAL-006** [Manifest Field Review](manifest_field_review.md) — Review of setup and run manifest fields.
- **EVAL-007** [Simulation Registry Coverage Review](simulation_registry_coverage_review.md) — Audit of active model, study, and backend combinations.
- **EVAL-008** [System Simulation Use-Case Coverage Analysis](use-case-coverage-analysis.md) — Coverage analysis of simulation use cases.
- **EVAL-009** [Standard-artifact boundary audit](standard-boundary-audit.md) — SSP, SSV, SSM, and SSD pass through pyssp_standard; comparison passes through pyssp_vv; non-standard crossings use public API only.
- **EVAL-010** [pyssp project verification plan](pyssp_project_verification_plan.md) — Audit of the six vendored pyssp_* and sequence_extensions test suites, the level ladder each one was missing, and the restructuring that closed the contract, determinism, and failure-path gaps.
- **EVAL-011** [Test suite restructuring and fixture credibility](test-suite-restructuring.md) — Critical audit of the six vendored pyssp_* and sequence_extensions suites plus the root contract suite, focused on the file-fixture layer, and the restructuring that makes every fixture traceable, layout-checked, and write-protected.
- **EVAL-012** [Fixture layer implementation record](fixture-layer-implementation.md) — What the fixture restructuring built in each suite, the counts after the change, the defect injected to prove each gate red, and the gaps that remain.
- **EVAL-013** [Package layout review across the vendored libraries](package-layout-review.md) — Flatness measurements for the six vendored packages, the two that were restructured into domain packages, and why the other four keep their layout.
<!-- pb:index:end -->
