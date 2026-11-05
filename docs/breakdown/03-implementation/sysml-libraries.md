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
artifact libraries and the dialect arrive through `pyssp_workflow`'s `sysml`
extra, which is an install bundle: `pyssp_workflow` carries them and imports
none of them.

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
- **Exercised here:** `models/ssp/variation_*/build.py` and `tests/test_variation_cases.py` use the dialect and selection surface; `models/ssp/GainOffset/` is the FMI fixture, with its definition in `models/fmu/GainOffset/` and its compiled outputs in `artifacts/build/GainOffset/`.
