---
id: IMP-107
type: imp
title: FMI Model Exchange support
summary: Emit Model Exchange artifacts for components whose dynamics need an integrator rather than a co-simulation step.
date: 2026-11-05
status: suggested
---

# FMI Model Exchange support

Model Exchange is a separate FMI 2.0 interface type: the FMU exports its right-hand side and the importer supplies the integrator.

## Objective And End State

`pyfmi_sysml2` emits an FMI 2.0 Model Exchange FMU for one fixture: modelDescription declaring `ModelExchange`, C headers, package layout, and an FMPy load check under `tests/`.

## Evidence

- ADR-017 bounds current FMI scope to 2.0 Co-Simulation on `linux64`.
- `pyfmi_sysml2` roadmap lists Model Exchange as an explicit non-goal for v0.2.0.
- No `models/fmu/` fixture declares `implementation = "ModelExchange"`.

## Rationale

An ME fixture would compare an importer's integrator, which no current CS fixture reaches. Without that fixture the emitted ME document has no consumer and no comparison gate.

## Owner And Blocker

Unowned by design: no fixture needs ME and ADR-017 keeps it out of scope. Start only when a fixture declares Model Exchange and the division between FMI model code and FMU packaging is settled.

## Traceability

- Decision: `ADR-017`, `ADR-015`.
- Related candidate: `IMP-108`.

## References

- `repos/pyfmi_sysml2/docs/breakdown/06-evolution/roadmap.md`.
