---
id: IMP-110
type: imp
title: Migrate ssp_airplane to pyssp_sysml2 v0.4.0 and pyfmi_sysml2
summary: Move the external ssp_airplane model off the pre-0.4.0 authoring API onto the split libraries.
date: 2026-11-05
status: suggested
---

# Migrate ssp_airplane to pyssp_sysml2 v0.4.0 and pyfmi_sysml2

`ssp_airplane` still authors against the pre-0.4.0 `pyssp_sysml2` API that bundled the dialect and FMI generation.

## Objective And End State

`~/pwa/2_work/ssp_airplane` builds against `pyssp_sysml2` v0.4.0 with `pycps_sysml2` and `pyfmi_sysml2` installed, imports `pycps_sysml2` directly, and calls `pyfmi model-description` instead of the removed `pyssp_sysml2` FMI generator. Its build and tests pass.

## Evidence

- `pyfmi_sysml2` test fixtures were ported from `ssp_airplane/architecture/part_definition.sysml`.
- `pyssp_sysml2` v0.4.0 removed its FMI generator and its FMI artifacts module.
- The v0.4.x `pyssp_sysml2.model`, `.core`, `.metadata`, and `.parameters` shims are temporary until v0.5.0.

## Rationale

A downstream model on removed API cannot take the new pins. The fixture ports prove the dialect carries the airplane's components, but its own build has no migration yet.

## Owner And Blocker

Owner: `ssp_airplane` maintainer; this repository owns the library pins, not that tree. Blocker: that repository's build and test flow must be migrated, not only its imports.

## Traceability

- Decision: `ADR-015`, `ADR-016`.
- Upstream candidate: `IMP-109`.

## References

- `3rd_party/pyssp_workflow/3rd_party/pyfmi_sysml2/tests/fixtures/bus/case.md`.
