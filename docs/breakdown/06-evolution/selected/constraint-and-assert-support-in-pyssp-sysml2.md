---
id: IMP-104
type: imp
title: Constraint and assert support in pyssp_sysml2
summary: Carry SysML constraint and assert elements through the parser adapter and evaluate them after variation selection, so illegal variant combinations fail at build time.
date: 2026-10-30
status: current
---

# Constraint and assert support in pyssp_sysml2

SysML v2 `constraint def`, `constraint` usage, and `assert` are authoring-time legality rules.
`sysmlpy` parses them. `pyssp_sysml2` drops them.
`Architecture` holds parts, ports, attributes, requirements. No constraint collection.
`loader._merge_packages` merges those four kinds only.
`variation.resolve` selects after load. No consumer evaluates constraints.
The two conditional fixtures duplicate the rule in `build.py`. Workaround, not contract.

## Objective And End State

Carry constraints through the adapter. Evaluate for a selected architecture. Reject illegal selections at build time. Remove the fixture-local rule.

- `Architecture` carries constraint definitions and usages: name, parameters, expression/body, doc, source.
- `load` retains them; `variation.resolve` preserves them.
- Public API returns pass, fail, invalid, and unasserted per constraint.
- CLI rejects failed asserted constraints before writing an artifact.
- Exporter preserves constraints or refuses to erase them.
- Fixtures call the adapter API; `is_legal` goes away.
- Tests cover capture, selection, rejection, export, no-constraint behavior.

## Evidence

- `sysmlpy` exposes `package.constraints`; the fixture package has one.
- `System.children` holds `Constraint requiresSingleStage` and an unnamed `assert`; `sysmlpy.check_constraints(model, bindings=None)` exists.
- `Architecture` has no constraint field; `loader._merge_packages` ignores `package.constraints`.
- No adapter code models or evaluates constraints. Built SSD is identical with or without the constraint.
- Workaround: `models/ssp/variation_conditional_requires/build.py` and `.../variation_conditional_excludes/build.py` own `AUTHORED`, `is_legal`, `SELECTIONS`, `PRUNED`.
- Traceability: parent `IMP-103`; fixture notes in both `variation_conditional_*` directories; adapter paths listed in Scope.

## Scope

- `pyssp_sysml2`: `model/parser.py` capture; `model/model.py` and `model/loader.py` model and merge; new `parameters/constraints.py` or `variation.py` evaluation; `cli.py` rejection; `model/exporter.py` and `sysml/sync.py` erasure policy.
- `pyssp_sysml2` tests and fixtures.
- `pyssp_workflow` authoring if the build surfaces rejection.
- `ssp_references` fixtures and tests after the pin.
- Gitlink order: `pyssp_sysml2`, `pyssp_workflow`, `ssp_references`.
- Out of scope: full OCL/SysML semantics, constraint solving, runtime enforcement, SSP packaging, replacing build-time selection, changing the `sysmlpy` pin.

## Constraints

- Only `parser.py` imports `sysmlpy`; the model stays independent.
- SSP, SSD, SSV, SSM, and FMI artifacts do not change.
- Evaluate after `variation.resolve`; declarations alone cannot decide a variant rule.
- Fail loud on unknown variant, missing parameter, or non-boolean result.
- `constraint def` is a definition; `assert` is the obligation.
- Support the variant-legality subset. No general expression language.
- Do not edit nested `pyssp_sysml2/3rd_party/pyssp_standard`.
- Authority: implementer may choose A or B, must record the choice, report deviations, and keep the SSP artifact schema unchanged.

## Design Choice

- **A. Bridge `sysmlpy.check_constraints`.** Reuse evaluator; needs a selected `sysmlpy` model. More coverage, more coupling.
- **B. Repo-owned constraint model plus small evaluator.** Fits adapter boundary; limited subset. Recommended.
- **C. Keep the build guard.** Status quo; duplicates the rule; not the end state.
- Decision record required before implementation.

## Task Contract

1. **Capture.** Model carries every constraint definition, usage, and assert. `parser.py`, `model.py`, `loader.py`, tests. Acceptance: name, parameters, expression, asserted flag; empty when absent; suite green.
2. **Evaluate.** Public call and CLI reject illegal selection. New constraint module, `variation.py`, `cli.py`, tests. Acceptance: legal pass; illegal fail with named constraint; unknown variant and malformed expression distinct; no artifact on failure.
3. **Migrate.** Two `build.py` and `tests/test_variation_cases.py`. Acceptance: legal builds byte-identical; pruned branches absent; adapter rejects; registry and gates unchanged.
4. **Record and pin.** `pyssp_sysml2` docs, `pyssp_workflow` gitlink, root gitlink. Acceptance: upstream and `ssp_references` tests green; pin order recorded.

## Acceptance Criteria

- `pytest` in `pyssp_sysml2` and `pyssp_workflow` passes.
- `python3 -m pytest tests/` in `ssp_references` passes.
- `build_models.py run variation_conditional_requires variation_conditional_excludes` passes.
- `artifacts/models/**/sine_two` and `artifacts/models/**/sine_high` stay absent.
- `run_comparisons.py ... --fail-on-gate` passes.
- New tests: illegal selection exits nonzero with no artifact; adapter, not `build.py`, rejects it; export preserves or refuses to erase constraints.
- `pb check --strict` and `pb node-size --strict` pass.

## Risks And Blast Radius

- Cross-repo: adapter, loader, parser, CLI, exporter, tests, two gitlinks.
- `sysmlpy` 0.96.4 decides what survives; a bump may change the raw tree.
- `sync` regenerates SysML from SSD; constraints have no SSD form. Preserve or refuse.
- New public API is a deliberate addition; document it.
- Definition vs obligation semantics can hide failed rules.
- Adapter-level test is mandatory; fixture-only guards can pass while constraints drop.

## Owns / Excludes

- Owns: constraint and assert capture in the adapter.
- Owns: evaluation after variation selection and the build-time legality contract.
- Excludes: variation resolution (`IMP-103`), SSP/SSV/SSM/FMI schema (`pyssp_standard`), simulation-time enforcement (`pyssp_simulate`).
