---
id: INFO-003
type: info
title: Pipeline and Tool Boundaries
summary: Artifact and tool contracts at the build, simulate, compare, and SysML boundaries.
date: 2026-10-22
status: current
pb_exempt: true
---

# Pipeline and Tool Boundaries

**Status:** Canonical
**Layer:** system-architecture

This document is the canonical definition of the artifact-level contract
between the repository's pipeline stages and external tools. The
[System Architecture](architecture.md) describes the complete architecture;
this file is the single reference for what each boundary reads and writes,
and for which artifacts are allowed to cross a tool boundary.

If a boundary changes, update this document first, then the affected entry
points and tests.

## Canonical Boundary

```text
Authoring -> reads SysML, invokes external pyssp CLI, writes SSP + study data
Build     -> reads model/study sources + FMU sources, writes model SSP + study artifacts
Simulate  -> reads model SSP + study artifacts + registry, writes CSV + run manifests
Compare   -> reads run manifests + CSV, writes comparisons
SysML     -> reads SSD, invokes external pyssp CLI, writes SSD (round-trip checker)
```

The arrows describe artifacts, not Python objects. No stage imports another
stage's in-memory model, and no tool adds compatibility behavior to a producer
library to satisfy a consumer.

## Boundary Contract

| Boundary | Entry point | Reads | Writes | Must not |
| --- | --- | --- | --- | --- |
| Authoring | `pyssp_workflow.authoring` → external `pyssp` | `architecture/*.sysml`, FMU sources | Derived `.ssp`, SSD, SSV, SSM, study descriptor | Import `pyssp_sysml2` / `pyssp_vv`, mutate source SysML |
| Build | `scripts/build_models.py` → `models/ssp/<model>/build.py` | Model directory incl. `architecture/*.sysml`, FMU sources, legacy `.ssv` / `.ssm` / `experiments.xml` | Exported model SSP at `artifacts/models/<model>/<build>/`; study artifacts at `artifacts/studies/<model>/<study>/` | Simulate, write comparison output, modify `artifacts/simulation_registry.json` |
| Simulate | `scripts/run_simulations.py` → `pyssp_workflow` / `pyssp_simulate` | Exported model SSP, study artifacts, `artifacts/simulation_registry.json` | `setup.json`, `artifacts/simulation/<model>/<study>/<backend>/result.csv`, `simulation.json`, `config.json`, logs | Rebuild the SSP, mutate exported model artifacts, run comparisons |
| Compare | `scripts/run_comparisons.py` → `pyssp_vv` target | `simulation.json` run manifests, `result.csv`, `setup.json`, registry reference entries | `artifacts/comparisons/<model>/<study>/<pair>/comparison.json`, `metrics.csv`, batch summary | Re-run simulations, rebuild SSPs, modify simulation outputs |
| SysML checker | `scripts/check_sysml_roundtrip.py` → external `pyssp` | `SystemStructure.ssd` | Generated SysML and regenerated SSD under the requested output directory | Import `pyssp_sysml2` / `pyssp_standard`, modify the source SSD, read simulation or comparison artifacts |

## Artifact Classes

### Standardized, cross-tool artifacts

These are the only artifacts that may cross a tool boundary:

- The exported model SSP root: `SystemStructure.ssd`, `resources/`, and an
  optional default `extra/org.fmi-standard.fmi-ls-ref/experiments.xml`.
- SSP XML members: `.ssd`, `.ssv`, `.ssm`, and the LS-REF experiment file.
- Study scenario artifacts: the scenario `.ssv` and `.ssm`. These are
  standardized SSP XML even though they live outside the exported SSP.
- Simulation result CSV: the normalized trajectory written by the simulate
  stage.

A tool may be replaced or upgraded as long as it produces or consumes these
artifacts in a conformant way.

### Repository-internal artifacts

These are contracts between stages in this repository, not general SSP
interchange formats:

- `artifacts/simulation_registry.json`
- `artifacts/studies/<model>/<study>/study.json` (study/experiment descriptor)
- `artifacts/simulation/<model>/<study>/setup.json`
- `artifacts/simulation/<model>/<study>/<backend>/simulation.json`
- `artifacts/comparisons/<model>/<study>/comparison.json`
- `artifacts/comparisons/<model>/<study>/metrics.csv`
- `artifacts/comparisons/<model>/<study>/comparisons.json`

They may use repository-specific fields, but they must remain self-contained:
paths are recorded relative to the manifest that contains them.

## Tool Environments

Each tool may run in its own virtual environment. Version alignment is needed
only when an artifact format changes, not when a Python model API changes.

For development, one git submodule under `3rd_party/` owns the ecosystem
checkouts. The capabilities are nested inside it:

| Submodule | Used by |
| --- | --- |
| `3rd_party/pyssp_workflow` | Composition layer: authoring, build, execute, measure/judge nodes, development tree |
| `3rd_party/pyssp_workflow/3rd_party/pyssp_standard` | Build and SSP XML inspection |
| `3rd_party/pyssp_workflow/3rd_party/pyssp_simulate` | Simulate |
| `3rd_party/pyssp_workflow/3rd_party/pyssp_sysml2` | Authoring (CLI) and SysML round-trip checker |
| `3rd_party/pyssp_workflow/3rd_party/sequence_extensions` | Build/simulation/compare campaign orchestration |
| `3rd_party/pyssp_workflow/3rd_party/pyssp_vv` | Measurement, judgment, evidence, and reporting |

See [`3rd_party/README.md`](../../3rd_party/README.md) for initialization and
local-patch guidance.

| Tool | Dependency expectation | Environment |
| --- | --- | --- |
| Authoring | `pyssp_workflow.authoring` + external `pyssp` CLI (`pyssp_sysml2`) | Runtime venv or a separate SysML environment via `PYSSP` |
| Build | `pyssp_workflow` + `pyssp_standard` with the refactored model API | Runtime venv |
| Simulate | `pyssp_workflow` + `pyssp_simulate` plus the selected engines | Runtime venv |
| Compare | `pyssp_workflow` + `pyssp_vv` (target); local comparison utilities during migration | Runtime venv or a compatible environment |
| SysML checker | `pyssp_sysml2` targeting the refactored `pyssp_standard` API | Separate environment allowed |

The SysML checker accepts an explicit executable:

```bash
python3 scripts/check_sysml_roundtrip.py \
  artifacts/models/<model>/<build>/SystemStructure.ssd \
  --output /tmp/sysml_roundtrip \
  --pyssp /path/to/venv-sysml/bin/pyssp
```

`PYSSP` may be used instead of `--pyssp`.

## Rules

1. **Artifacts, not object models.** A boundary is crossed by reading or
   writing a file, never by passing a `pyssp_standard` model object.
2. **No producer-side compatibility shims.** Adapt the consumer or the
   artifact boundary. Do not add legacy facade properties to the producer
   library for a downstream caller.
3. **Explicit tool invocation.** External tools are invoked through a CLI or
   subprocess with an explicit executable path, not imported into the calling
   pipeline.
4. **Relative paths in manifests.** Manifests record paths relative to their
   own location so the artifact tree can be moved without rewriting metadata.
5. **Fail loudly on missing or invalid artifacts.** A missing SSP root,
   manifest, or result CSV is an error, not a silent fallback to a model
   object or a different tool.
6. **Exported SSPs are immutable build outputs.** Scenario and experiment data
   is applied to a runtime copy. A study must not modify
   `artifacts/models/<model>/<build>/`.
7. **Studies are data, not SSPs.** A `Study` definition produces SSV, SSM, and
   a study descriptor. It must not produce a `SystemStructure.ssd` or `.ssp`.

## Backward Trace

- `ADR-001` - three-stage pipeline
- `ADR-005` - pyssp ecosystem adoption
- `ADR-006` - standardized artifacts at tool boundaries
- `ADR-007` - SysML authoring at the build boundary
- `ADR-008` - workflow capability ownership
- `ADR-009` - `SspModel`/`Study` markers
- `ADR-010` - runtime scenario injection
