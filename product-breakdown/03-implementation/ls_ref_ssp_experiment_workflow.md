---
id: INFO-005
type: info
title: LS-REF Packaging Note
summary: LS-REF experiment XML is packaging metadata, not the runtime contract.
date: 2026-10-22
status: current
pb_exempt: true
---

# LS-REF Packaging Note

LS-REF experiment XML is packaging metadata. It is not the runtime contract for
simulation or comparison.

The runtime flow is driven by:

1. An exported model SSP under `artifacts/models/<fixture>/<build>/`.
2. Study artifacts under `artifacts/studies/<fixture>/<study>/` — scenario SSV,
   SSM mapping, and study/experiment descriptor.
3. Study and backend selection from `artifacts/simulation_registry.json`.
4. Generated `setup.json` files plus the shared simulation and comparison entry
   points under `scripts/` and `pyssp_workflow`.

## Authored vs generated

For SysML-authored fixtures:

- the `SspModel` composition is the authored source for the exported SSP;
- a `Study` composition is the authored source for scenario values and the
  experiment window;
- `extra/org.fmi-standard.fmi-ls-ref/experiments.xml` in the exported SSP, when
  present, is a generated default for standalone use, not the study contract;
- the study descriptor drives the runtime window and tolerance.

For legacy fixtures, `experiments.xml` may still be authored. Keep it focused on
packaging the runnable SSP variant and do not put compare-signal selection in
it.

When a fixture does use LS-REF `experiments.xml`:

- place it under `extra/org.fmi-standard.fmi-ls-ref/experiments.xml` if that is
  how the builder packages the SSP;
- keep execution settings and compare-signal selection out of the XML;
- keep `build.py` close to the VanDerPol pattern: validate, build, package,
  stop.

Most fixtures in this repository do not rely on LS-REF at runtime. For the
current workflow details, read `README.md` and
`../04-verification/co_simulation_test_strategy.md`.
