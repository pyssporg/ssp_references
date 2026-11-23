---
id: INFO-012
type: info
title: SysML libraries
summary: pycps_sysml2 is the dialect home; pyssp_sysml2 emits SSP-family artifacts, pyfmi_sysml composes SysML for the pyfmi_interfaces FMI emitters.
date: 2026-11-05
status: current
---

# SysML libraries

`pycps_sysml2` is the dialect's home; the other libraries implement it.
`pyssp_sysml2` emits the SSP family, `pyfmi_interfaces` emits FMI artifacts
from a parser-free reduction, and `pyfmi_sysml` is the composition layer that
owns the SysML reader and the source-taking FMI commands. The FMI emitter is a
base dependency of `pyssp_workflow`, which imports none of them; the dialect
arrives transitively through `pyssp_sysml2` and `pyfmi_interfaces`, and the
composition layer is installed when a fixture drives FMI from SysML.

| Concern | Owner |
|---|---|
| Parse SysML v2 and hold the IR | `pycps_sysml2` |
| Markers, roles, and named attributes | `pycps_sysml2` |
| Parameters: model, paths, resolution, bindings | `pycps_sysml2` |
| Variation: selection, configuration, analysis diagnostics | `pycps_sysml2` |
| Constraints: capture and evaluation | `pycps_sysml2` |
| SSD, SSV, SSM, SSP emission; SSD→SysML synthesis | `pyssp_sysml2` |
| SysML ingestion, one-parse reduction, source-taking FMI commands (`pyfmi-sysml`) | `pyfmi_sysml` |
| FMI 2.0 CS: reduction model, modelDescription, C headers, Modelica connectors, FMI headers, FMU emission | `pyfmi_interfaces` |
| FMI 2.0 documents, codec, validator, archive writer | `pyssp_standard` behind both |

- **Import rule:** consumers import `pycps_sysml2` for the dialect. Build
  scripts that emit FMI go through `pyfmi_sysml`, which calls
  `pyfmi_interfaces`; they never call the parser and the emitters separately.
  `pyssp_sysml2` and `pyfmi_interfaces` never import each other, and
  `pyfmi_sysml` is the only package that composes them.
- **One dialect:** both the SSP and FMI dialects draw markers, parameters, and
  variation from `pycps_sysml2`; `sysmlpy==0.96.4` and
  `pyssp-sysml-definitions` are its only runtime dependencies.
- **Exercised here:** `models/ssp/variation_*/build.py` and
  `tests/test_variation_cases.py` use the dialect and selection surface;
  `models/fmu/GainOffset/build.py` loads the canonical FMU architecture once
  through `pyfmi_sysml.load_architecture` and drives its generators onto
  `pyfmi_interfaces`; the SSP build passes that architecture directory as an
  include and embeds the archive under `artifacts/build/GainOffset/`.
- **Core definitions:** the installable vocabulary lives in
  `pyssp_sysml_definitions` (`core.sysml`, package `PysspCore`, and
  `interop.sysml`, package `PyfmiInterop`); `pycps_sysml2.core_definitions()`
  re-exports its path. `load(model, *includes)` takes the model root first,
  then included definition roots under any package name; the core is one
  include (`load(dir, core_definitions())`, `pyssp --core-definitions`).
  `pyfmi_sysml.load_architecture(source, includes=...)` adds the interop
  vocabulary only when the model imports `PyfmiInterop`. Storage is package
  scoped: the model's package keeps the bare name, another package is stored
  as `<package>::<name>`, so the core shows up as `PysspCore::SspModel` in
  `included_definitions` while `Definition.name` stays bare; a bare reference
  resolves to a qualified key only when exactly one candidate matches. The
  fixture check rejects a local redeclaration, and included names are excluded
  from export (`ADR-019`).
