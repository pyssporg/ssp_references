---
id: IMP-101
type: imp
title: Scenario ownership strategy for SSP fixtures
summary: One strategy selects whether a scenario parameter set is applied by the model, the study, or the build; pyfmu motivates the model-owned option.
date: 2026-10-23
status: current
---

# Scenario ownership strategy for SSP fixtures

A scenario parameter set has three possible owners: the `SspModel`, the `Study`, or the fixture build.
Fixtures use study-owned, model-owned, and fixed-body scenarios.
`pyfmu_csv_source_sink` is the first model-owned fixture.
A model-owned set fixes the scenario for all studies.

## Evidence

- **pyfmu build**: attaches the generated CsvSource FMU; applies no parameter set.
- **pyfmu SysML**: `System` owns `ScenarioSet`; `baseline :> Study` is experiment-only.
- **model-owned export works**: `generate ssp` writes `resources/parameter_sets/ScenarioSet.ssv` and a root binding.
- **runtime equivalent**: the model-owned SSP simulated bit-identically to the legacy result; 1001 rows, max abs diff 0.0.
- **model-owned study works**: `generate study` writes an experiment-only descriptor for a model-owned set.
- **model-owned binds allowed**: `applied_sets` skips `SspModel` bindings when composing a study.
- **experiment-only descriptors exist**: `generate study` writes a descriptor with no `scenario` when the study applies zero sets.
- **conflict rule**: a study set plus a model-owned set raises an error.
- **fixed-body precedent**: `dcmotor` and `embrace` use a fixed body plus an experiment-only study.
- **variable-scenario precedent**: `signal_*` fixtures apply the scenario in the study.

## Current Pain Or Risk

- Conventions coexist without a rule: study-owned, build-owned, and fixed-body.
- A model-owned set plus a study set targets the same parameter twice.
- `bind` is equality, so the dialect cannot express override.
- The build has no helper for two root bindings.

## Options

- **A. Study-owned scenario**: current dialect.
  - Scenario varies per study.
  - Build packages the set; form depends on the fixture hook.
  - No dialect change.
- **B. Model-owned scenario**: `SspModel` owns the set; study is experiment-only.
  - One scenario per model; studies vary only the window.
  - `generate ssp` packages the set; build adds no second binding.
  - Needs dialect change: allow model-owned set usage and binds when a study composes the model.
  - Needs conflict rule: reject a study set when the model owns one.
  - Artifact form becomes external SSV plus mapping.
- **C. Build-owned scenario**: scenario stays in `build.py`; study is experiment-only.
  - Preserves the current inline form.
  - Scenario is not authored in SysML.
  - No `parameters.py` change; relies on experiment-only descriptor support.

## Decision Criteria

- One authored source for the scenario.
- Reproducible build; no second root binding.
- Clear split: model fixes the scenario, study fixes the run window.
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
- **Repo**: `scripts/utils/authoring.py`, pyfmu build, tests, `FIXTURE.md`.
- **Artifact**: form changes from inline to external SSV plus mapping.
- **Flexibility**: studies over a model-owned scenario cannot vary the scenario.

## Open Questions

- Does any fixture need multiple studies with different scenarios over one model?
- Must pyfmu keep the inline parameter form, or is external SSV plus mapping acceptable?
- Should a model-owned set plus a study set be a hard error, or a disjoint merge?
- Which fixtures move to model-owned: only fixed-scenario fixtures, or all?

## Owns

- The strategy decision for scenario ownership across SSP fixtures.

## Excludes

- The `pyfmu_csv_source_sink` migration itself; completed as the first case.
- The `pyssp_sysml2` dialect implementation; a separate upstream task.
- LS-REF packaging policy; see `INFO-005`.
- Build and runtime pipeline; see `INFO-002` and `INFO-008`.
