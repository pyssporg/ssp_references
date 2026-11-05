---
id: INFO-012
type: info
title: SysML libraries
summary: pycps_sysml2 is the dialect home; pyssp_sysml2 emits SSP-family artifacts and pyfmi_sysml2 emits FMI 2.0 CS artifacts.
date: 2026-11-05
status: current
---

# SysML libraries

`pycps_sysml2` is the dialect's home; the other libraries implement it. Both
artifact libraries and the dialect are base dependencies of `pyssp_workflow`, so
a plain install carries them; `pyssp_workflow` imports none of them.

| Concern | Owner |
|---|---|
| Parse SysML v2 and hold the IR | `pycps_sysml2` |
| Markers, roles, and named attributes | `pycps_sysml2` |
| Parameters: model, paths, resolution, bindings | `pycps_sysml2` |
| Variation: selection, configuration, analysis diagnostics | `pycps_sysml2` |
| Constraints: capture and evaluation | `pycps_sysml2` |
| SSD, SSV, SSM, SSP emission; SSD→SysML synthesis | `pyssp_sysml2` |
| FMI 2.0 CS: modelDescription, C headers, Modelica connectors, FMU packaging | `pyfmi_sysml2` |
| FMI 2.0 documents, codec, validator, archive writer | `pyssp_standard` behind both |

- **Import rule:** consumers import `pycps_sysml2`. `pyssp_sysml2.model`, `.core`, `.metadata`, and `.parameters` are v0.4.x re-export shims removed in v0.5.0; `pyssp_sysml2` and `pyfmi_sysml2` never import each other.
- **One dialect:** both the SSP and FMI dialects draw markers, parameters, and variation from `pycps_sysml2`; `sysmlpy==0.96.4` is its only runtime dependency.
- **Exercised here:** `models/ssp/variation_*/build.py` and `tests/test_variation_cases.py` use the dialect and selection surface; `models/fmu/GainOffset/` owns the FMI fixture's canonical FMU definitions (the `Generator :> FmuModel` definition) and source, `models/ssp/GainOffset/architecture/System.sysml` owns the system and passes the FMU architecture directory as an include, the SSP build embeds the archive, and the generated definition and compiled outputs live in `artifacts/build/GainOffset/`.
- **Core definitions:** `pycps_sysml2` ships `definitions/core.sysml` (`package PysspCore`) with the eight dialect markers (including `FmuModel`) and metadata schemas; `core_definitions()` returns its path. `load(model, *includes)` takes the model root first, then included definition roots under any package name; the core is one include (`load(dir, core_definitions())`, `pyssp --core-definitions`). Storage is package scoped: the model's own package keeps the bare name, another package is stored as `<package>::<name>`, so the core shows up in `included_definitions` as `PysspCore::SspModel` and so on while `Definition.name` stays bare; a bare reference resolves to a qualified key only when exactly one candidate matches. The fixture check rejects a local redeclaration, and included names are excluded from export (`ADR-019`).
