---
id: CP-001
type: capability
title: Model export, analysis, and comparison contract
summary: Exported SspModel SSPs run under analyses; comparison is engine-to-engine with registry policy.
date: 2026-10-22
status: current
---

# Model export, analysis, and comparison contract

- **Exportable model**: each `SspModel` definition exports to one SSP.
- **Analysis**: each `Analysis` definition supplies scenario data and one experiment
  (`startTime`, `stopTime`, `stepSize`). Tolerance is an FMU property, not an
  experiment field.
- **Parameter form**: the suite preserves the parameter-application forms it
  exercises. Authoring must not flatten them.
- **Analysis export**: analyses are never exported as SSPs.
- **Backends**: ssp4sim, OMSimulator, and FMPy are supported.
- **Comparison**: comparison is pairwise engine-to-engine; no engine is golden.
- **Registry**: the simulation registry selects active model builds, analyses, backends, signals, references, and gate policy.
- **Verdict**: a comparison verdict is pass, fail, or invalid.
- **Ownership**: generic build, run, compare, and verify behavior comes from the pyssp ecosystem.
- **FMI fixtures**: FMI fixtures generate through the `pyfmi_sysml` composition layer, which drives the `pyfmi_interfaces` emitters — C headers, modelDescription, Modelica connectors — and packages through `pyssp_standard.FMU.package`.
- **FMI ownership**: `pyssp_sysml` emits no FMI; its `generate fmi` command is removed, and `pyfmi-sysml` owns the source-taking FMI commands while `pyfmi_interfaces` owns the emitters.
- **Library boundaries**: pass standardized artifacts first; when no standard exists, pass only documented public API types, never private or adapter-only structures.

## Owns
- Product promise for model export, analysis runs, and comparison.

## Excludes
- Pipeline organization: `INFO-002`.
- Boundary contracts: `INFO-003`.
- Runtime mechanism: `INFO-008`.
- Verification procedure: `EVAL-001`.
