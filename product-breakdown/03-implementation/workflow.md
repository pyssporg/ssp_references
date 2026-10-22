---
id: INFO-008
type: info
title: Build, study, and runtime workflow
summary: Build exports SspModel SSPs and study artifacts; simulate injects study data into a runtime SSP copy.
date: 2026-10-22
status: current
---

# Build, study, and runtime workflow

- **Authoring**: `pyssp_workflow.authoring` invokes the `pyssp` CLI; no `pyssp_sysml2` import.
- **Model build**: `build.py` exports `artifacts/models/<model>/<build>/`.
- **Study build**: study produces SSV, SSM, and descriptor under `artifacts/studies/<model>/<study>/`.
- **Runtime**: `pyssp_workflow.params` resolves scenario; `pyssp_workflow.execute` copies the exported SSP and adds a root-level `ParameterBinding`.
- **Immutability**: exported SSP is never mutated.
- **Canonicalization**: strip all runtime container names from result signals.
- **Campaign**: build, study, simulate, and compare run as `sequence_extensions` nodes.
- **Registry**: `build` selects the exported SSP; `study` selects study artifacts.
- **Capability ownership**: `pyssp_workflow` composes `pyssp_standard`, `pyssp_simulate`, `pyssp_vv`, and `pyssp_sysml2`.

## Owns
- Concrete build, study, and runtime mechanism.

## Excludes
- Product promise: `CP-001`.
- Stage boundary: `INFO-002`.
- Verification: `EVAL-001`.
