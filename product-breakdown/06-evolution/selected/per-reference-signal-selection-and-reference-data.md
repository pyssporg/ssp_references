---
id: IMP-102
type: imp
title: Per-reference signal selection and reference data
summary: Let a reference CSV name its own signals and mapping so comparisons can target a subset of parameters without changing model-level compare signals.
date: 2026-10-23
status: current
---

# Per-reference signal selection and reference data

The registry owns reference baselines, compare signals, and gate policy.
A reference CSV currently carries only `label`, `path`, and `gate`.
`compare_signals` is model-level and applies to every engine pair and every reference.
The compare stage loads each reference with `SimulationResult.from_reference_csv(model_name=...)`.
That helper strips the `default.<model>.` prefix and leaves the remaining columns as-is.
The old LS-REF `experiments.xml` carried a per-reference `<Signal>` list and an SSM mapping.
The migrated fixtures no longer carry either; the reference SSM files were deleted.
`VanDerPol` ships `resources/vanderpol_reference_fast.csv`, but the registry does not use it.
`references/*-me.csv` is registered as a non-gate reference.

## Evidence

- **registry shape**: `RegistryReferenceCsv` has `label`, `path`, `gate`; no signal list or mapping.
- **model-level selection**: `SimulationSetup.compare_signals` comes from the registry model entry.
- **reference loader**: `from_reference_csv` supports only a `default.<model>.` prefix.
- **legacy metadata**: deleted files mapped `default.<Model>.<signal>` to `fmu.<signal>`.
- **fast reference unused**: `vanderpol_reference_fast.csv` has columns `x0`, `x1` and no registry entry.
- **engine comparison**: engine pairs share the same model-level signal list.

## Current Pain Or Risk

- A reference cannot select a subset of signals without changing every comparison for that model.
- A reference with a non-standard column prefix has no mapping path.
- Per-reference and per-signal gates are not expressible.
- The fast VanDerPol reference is available but not wired.
- Reference policy is split between a deleted LS-REF bundle and the registry.

## Options

- **A. Registry-owned reference metadata**: extend `reference_csvs` with optional `signals` and `mapping`.
  - Keeps references and signal selection in the verification policy layer.
  - Compare stage selects signals per reference.
  - No Study or SysML change.
  - Smallest blast radius.
- **B. Study-owned reference metadata**: author references in the Study and emit them into `study.json`.
  - Couples the build input to the comparison stage.
  - Breaks the current split between build and verification policy.
  - Needs a SysML dialect extension for reference elements.
- **C. Case-level signal lists**: add `compare_signals` per registry case.
  - Simple, but still not per reference.
  - Does not restore reference mapping.

## Decision Criteria

- References remain verification policy, not build input.
- Per-reference signal selection is possible without duplicating cases.
- Standard artifacts stay the interchange format; no internal objects cross.
- The change stays inside `scripts/workflow` plus tests.
- Existing model-level `compare_signals` remains the default.

## Proposed Improvement

1. Extend `RegistryReferenceCsv` with optional `signals` and `mapping`.
2. Default `signals` to the model-level `compare_signals`.
3. Pass the per-reference selection into `compare_reference`.
4. Support a mapping source when column names do not follow `default.<model>.`.
5. Wire the VanDerPol fast reference as the first per-reference signal case.
6. Record the result as a decision before implementation.

## Expected Benefit

- Compare specific signals or parameter columns against a specific reference.
- Keep one case per study without splitting it for signal selection.
- Restore the mapping capability lost with the LS-REF files.

## Risk And Blast Radius

- **Repo**: `scripts/workflow/registry.py`, `scripts/workflow/reference.py`, `scripts/workflow/setup.py`, tests.
- **Artifact**: registry JSON gains optional fields; comparison manifests record the selected signals.
- **Policy**: per-reference gates may need their own tolerance policy.
- **Boundary**: do not move reference data into the Study or SysML.

## Open Questions

- Is a `default.<model>.` prefix enough, or is an arbitrary SSM mapping required?
- Should a reference signal list override or intersect the model-level list?
- Should the VanDerPol fast reference gate the `fast` case?
- Are per-reference gates needed, or is one gate per case enough?

## Owns

- The decision on per-reference signal selection and reference mapping in the verification policy layer.

## Excludes

- Study description and multi-study build support; implemented separately.
- LS-REF packaging policy; see `INFO-005`.
- Simulation registry technical mechanism; see `DD-005`.
- Runtime window and tolerance; see `DD-001`.
