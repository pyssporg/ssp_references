---
id: IMP-101
type: imp
title: Scenario ownership strategy for SSP fixtures
summary: One strategy selects whether a scenario parameter set is applied by the model, the analysis, or the build; pyfmu motivates the model-owned option.
date: 2026-10-23
status: current
---

# Scenario ownership strategy for SSP fixtures

A scenario parameter set has three possible owners: the `SspModel`, the `Analysis`, or the fixture build.
Fixtures use analysis-owned, model-owned, and fixed-body scenarios.
`pyfmu_csv_source_sink` is the first model-owned fixture.
A model-owned set fixes the scenario for all analyses.

## Evidence

- **pyfmu build**: attaches the generated CsvSource FMU; applies no parameter set.
- **pyfmu SysML**: `System` owns `ScenarioSet`; `baseline :> Analysis` is experiment-only.
- **model-owned export works**: `generate ssp` writes `resources/parameter_sets/ScenarioSet.ssv` and a root binding.
- **runtime equivalent**: the model-owned SSP simulated bit-identically to the legacy result; 1001 rows, max abs diff 0.0.
- **model-owned analysis works**: `generate analysis` writes an experiment-only descriptor for a model-owned set.
- **model-owned binds allowed**: `applied_sets` skips `SspModel` bindings when composing an analysis.
- **experiment-only descriptors exist**: `generate analysis` writes a descriptor with no `scenario` when the analysis applies zero sets.
- **conflict rule**: an analysis set plus a model-owned set raises an error.
- **fixed-body precedent**: `dcmotor` and `embrace` use a fixed body plus an experiment-only analysis.
- **variable-scenario precedent**: `signal_*` fixtures apply the scenario in the analysis.

## Current Pain Or Risk

- Conventions coexist without a rule: analysis-owned, build-owned, and fixed-body.
- A model-owned set plus an analysis set targets the same parameter twice.
- `bind` is equality, so the dialect cannot express override.
- The build has no helper for two root bindings.

## Options

- **A. Analysis-owned scenario**: current dialect.
  - Scenario varies per analysis.
  - Build packages the set; form depends on the fixture hook.
  - No dialect change.
- **B. Model-owned scenario**: `SspModel` owns the set; analysis is experiment-only.
  - One scenario per model; analyses vary only the window.
  - `generate ssp` packages the set; build adds no second binding.
  - Needs dialect change: allow model-owned set usage and binds when an analysis composes the model.
  - Needs conflict rule: reject an analysis set when the model owns one.
  - Artifact form becomes external SSV plus mapping.
- **C. Build-owned scenario**: scenario stays in `build.py`; analysis is experiment-only.
  - Preserves the current inline form.
  - Scenario is not authored in SysML.
  - No `parameters.py` change; relies on experiment-only descriptor support.

## Decision Criteria

- One authored source for the scenario.
- Reproducible build; no second root binding.
- Clear split: model fixes the scenario, analysis fixes the run window.
- Stable artifact form across fixtures.
- No ambiguous binding; all engines read the same scenario.
- Smallest cross-repo change that satisfies the above.

## Proposed Improvement

1. Evaluate options A, B, and C against the criteria.
2. Select one strategy for fixed-scenario fixtures.
3. Record the selection as a decision record.
4. Scope the dialect change and the pyfmu migration as separate tasks.

## Expected Benefit

- One convention per fixture class.
- One rule for fixed-scenario fixtures.

## Risk And Blast Radius

- **Cross-repo**: `pyssp_sysml2` dialect and tests.
- **Repo**: `pyssp_workflow.authoring`, pyfmu build, tests, `FIXTURE.md`.
- **Artifact**: form changes from inline to external SSV plus mapping.
- **Flexibility**: analyses over a model-owned scenario cannot vary the scenario.

## Open Questions

- Does any fixture need multiple analyses with different scenarios over one model?
- Must pyfmu keep the inline parameter form, or is external SSV plus mapping acceptable?
- Should a model-owned set plus an analysis set be a hard error, or a disjoint merge?
- Which fixtures move to model-owned: only fixed-scenario fixtures, or all?

## Owns

- The strategy decision for scenario ownership across SSP fixtures.

## Excludes

- The `pyfmu_csv_source_sink` migration itself; completed as the first case.
- The `pyssp_sysml2` dialect implementation; a separate upstream task.
- LS-REF packaging policy; retired by `AD-014`.
- Build and runtime pipeline; see `INFO-002` and `INFO-008`.
