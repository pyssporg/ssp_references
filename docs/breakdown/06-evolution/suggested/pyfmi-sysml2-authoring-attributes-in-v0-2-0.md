---
id: IMP-109
type: imp
title: pyfmi_sysml2 authoring attributes in v0.2.0
summary: Carry guid policy, modelName override, capabilities, units, and declared causality or variability from the dialect into FMI 2.0 documents.
date: 2026-11-05
status: suggested
---

# pyfmi_sysml2 authoring attributes in v0.2.0

FMI 2.0 exposes authoring choices the dialect cannot yet express, so the emitter derives defaults.

## Objective And End State

`pycps_sysml2` v0.2.0 defines the dialect facts: guid policy, modelName override, capability flags, units, and declared causality/variability. `pyfmi_sysml2` v0.2.0 emits them instead of deriving them, with a golden fixture per field.

## Evidence

- `FmuMetadata` in the dialect carries only `source` and `implementation` today.
- `pyfmi_sysml2` modelDescription and packaging code stamp derived defaults.
- The roadmap puts these attributes first, behind `pycps_sysml2` v0.2.0.

## Rationale

Derived defaults are the contract, not a placeholder to patch locally. Emitting an attribute without a dialect fact would fork the dialect, which `ADR-016` refuses.

## Owner And Blocker

Owner: `pycps_sysml2` maintainer for the dialect facts, then `pyfmi_sysml2` maintainer for emission. Blocker: `pycps_sysml2` v0.2.0 must land before any emitter change.

## Traceability

- Decision: `ADR-016`, `ADR-015`.
- Downstream: `IMP-110`.

## References

- `repos/pyfmi_sysml2/docs/breakdown/06-evolution/roadmap.md`.
