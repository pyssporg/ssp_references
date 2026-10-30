---
id: IMP-105
type: imp
title: Authored variation selection and condition ownership
summary: Each analysis declares its variant selection in SysML; the adapter resolves it and reports legal, violated, and invalid analyses, leaving build.py with only the fixture's expected partition.
date: 2026-10-30
status: current
---

# Authored variation selection and condition ownership

A variation fixture currently restates its combination table in `build.py` and translates it into two key scopes.
The analysis already names the combination; the selection is the only part outside the architecture.
The adapter also owns the legality condition, but each build re-implemented the predicate.

## Evidence

- `variation_conditional_requires/build.py` and `variation_conditional_excludes/build.py` carried `AUTHORED`, `SCOPED`, `SELECTIONS`, `PRUNED`, `_scoped`, `_selection_is_legal`, and `_validate_guard` around a four-row table.
- The excludes build needed `MODEL_SCENARIOS` naming all four analyses, including the pruned one, because a model build required every composing analysis's attribute point.
- `variation.resolve` accepted a bare selection key while `constraints._bind` looked up the authored binding path, so `--select source=…` resolved variation but failed constraint evaluation with `no selection for 'sut.source'`.
- `pyssp_sysml2` now exposes `analysis_plans` and `resolve_selected`; both conditional builds are reduced to a plan lookup and an explicit expected partition.

## Current Pain Or Risk

- A renamed variation point or variant breaks every fixture table even when the architecture still admits the documented combination.
- Two key languages make a legal CLI selection fail at constraint evaluation.
- A pruned analysis's scenario usage leaks into the model build as a required selection.
- Fixture build scripts own adapter mechanics, so a new variation fixture copies them.

## Options

- **A. Keep the external table.** No adapter change; duplication and key translation stay.
- **B. Author the selection on the analysis.** One `pyssp_selection` attribute; the adapter resolves it and reports the plan. Recommended and implemented.
- **C. Infer the selection from `bind` paths.** No new syntax; heuristic, ambiguous, and contrary to the no-guessing rule.

## Decision Criteria

- One authored source per selection.
- Fixtures keep only their claim: the expected legal and violated analyses.
- Variation and constraints share one key language.
- A model build depends only on its own composition.
- Smallest cross-repo change; no runtime variant switch.

## Proposed Improvement

1. Add `pyssp_selection` to every analysis in the six variation architectures. Done.
2. Parse and plan it in `pyssp_sysml2.parameters.selection`; canonicalize keys in `variation.resolve_selected`. Done.
3. Scope required attribute points to the target composition. Done.
4. Make `build_fixture` forward one selection map to both derivations. Done.
5. Pin the expected legal and violated analyses in the two conditional builds. Done.

## Expected Benefit

- The architecture is the single source of a selection.
- A fixture build declares names and packaging, not adapter mechanics.
- A bare or dotted selection key works for variation and constraints alike.

## Risk And Blast Radius

- **Cross-repo**: `pyssp_sysml2` selection, variation, constraints, and artifacts; `pyssp_workflow.authoring`; six fixtures and tests.
- **Dialect**: `pyssp_selection` is a repo convention, not standard SysML; it must stay documented and validated.
- **Artifact provenance**: `selection.json` records the analysis's authored selection, so the global scenario table disappears.
- **Framework drift**: selection stays build-time and per analysis; no runtime switch.

## Open Questions

- Should a future workflow choose among several authored selections per analysis?
- Does a selection need more structure than `key=variant` pairs?
- When should IMP-104 and this IMP move to `implemented/` and close the pin?

## Owns

- The authored-selection policy for SSP fixtures and the ownership split between fixture intent and adapter mechanics.

## Excludes

- Variation resolution and constraint evaluation semantics; see `IMP-103` and `IMP-104`.
- Comparison methodology and the build pipeline; see `CP-001` and `INFO-002`.
