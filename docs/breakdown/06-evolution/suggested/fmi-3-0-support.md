---
id: IMP-108
type: imp
title: FMI 3.0 support
summary: Emit FMI 3.0 artifacts once an SSP toolchain and a comparison backend can consume them.
date: 2026-11-05
status: suggested
---

# FMI 3.0 support

FMI 3.0 is a new schema with different variable types, interface definitions, and packaging.

## Objective And End State

`pyfmi_sysml2` emits an FMI 3.0 Co-Simulation FMU for one fixture, and a backend here loads it so the comparison stage can judge it.

## Evidence

- ADR-017 bounds current FMI scope to FMI 2.0 Co-Simulation on `linux64`.
- The fixture SSPs and the installed backends consume FMI 2.0.
- `pyfmi_sysml2` emits through `pyssp_standard` FMI 2.0 documents only.

## Rationale

A 3.0 emitter without a loader changes no comparison. The suite's quality gate is a trajectory, so support starts where a backend can run the artifact.

## Owner And Blocker

Unowned by design: no SSP toolchain here imports FMI 3.0 and ADR-017 keeps it out of scope. Blocker: an FMI 3.0-capable SSP importer plus a backend in the simulate stage.

## Traceability

- Decision: `ADR-017`, `ADR-016`.
- Related candidate: `IMP-107`.

## References

- `3rd_party/pyssp_workflow/3rd_party/pyfmi_sysml2/docs/breakdown/06-evolution/roadmap.md`.
