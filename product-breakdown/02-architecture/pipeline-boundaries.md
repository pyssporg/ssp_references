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
Build    -> SSP root: SSD / SSV / resources / experiments.xml
Simulate -> reads SSP root + registry, writes CSV + run manifests
Compare  -> reads run manifests + CSV, writes comparisons
SysML    -> reads SSD, invokes external pyssp CLI, writes SSD
```

The arrows describe artifacts, not Python objects. No stage imports another
stage's in-memory model, and no tool adds compatibility behavior to a producer
library to satisfy a consumer.

## Boundary Contract

| Boundary | Entry point | Reads | Writes | Must not |
| --- | --- | --- | --- | --- |
| Build | `scripts/build_models.py` → `models/ssp/<model>/build.py` | Model directory, FMU sources, authored `.ssv` / `.ssm` / `experiments.xml` | `artifacts/models/<model>/<case>/` containing `SystemStructure.ssd`, `resources/`, `extra/org.fmi-standard.fmi-ls-ref/experiments.xml` | Simulate, write comparison output, modify `artifacts/simulation_registry.json` |
| Simulate | `scripts/run_simulations.py` | Built SSP root + `artifacts/simulation_registry.json` | `setup.json`, `artifacts/simulation/<model>/<case>/<backend>/result.csv`, `simulation.json`, `config.json`, logs | Rebuild the SSP, modify model sources, run comparisons |
| Compare | `scripts/run_comparisons.py` | `simulation.json` run manifests, `result.csv`, `setup.json`, registry reference entries | `artifacts/comparisons/<model>/<case>/<pair>/comparison.json`, `metrics.csv`, batch summary | Re-run simulations, rebuild SSPs, modify simulation outputs |
| SysML | `scripts/check_sysml_roundtrip.py` → external `pyssp` | `SystemStructure.ssd` | Generated SysML and regenerated `SystemStructure.ssd` under the requested output directory | Import `pyssp_sysml2` / `pyssp_standard`, modify the source SSD, read simulation or comparison artifacts |

## Artifact Classes

### Standardized, cross-tool artifacts

These are the only artifacts that may cross a tool boundary:

- The unpacked SSP root: `SystemStructure.ssd`, `resources/`, and
  `extra/org.fmi-standard.fmi-ls-ref/experiments.xml`.
- SSP XML members inside the root: `.ssd`, `.ssv`, `.ssm`, and the LS-REF
  experiment file.
- Simulation result CSV: the normalized trajectory written by the simulate
  stage.

A tool may be replaced or upgraded as long as it produces or consumes these
artifacts in a conformant way.

### Repository-internal artifacts

These are contracts between stages in this repository, not general SSP
interchange formats:

- `artifacts/simulation_registry.json`
- `artifacts/simulation/<model>/<case>/setup.json`
- `artifacts/simulation/<model>/<case>/<backend>/simulation.json`
- `artifacts/comparisons/<model>/<case>/comparison.json`
- `artifacts/comparisons/<model>/<case>/metrics.csv`
- `artifacts/comparisons/<model>/<case>/comparisons.json`

They may use repository-specific fields, but they must remain self-contained:
paths are recorded relative to the manifest that contains them.

## Tool Environments

Each tool may run in its own virtual environment. Version alignment is needed
only when an artifact format changes, not when a Python model API changes.

For development, one git submodule under `3rd_party/` owns the ecosystem
checkouts. The capabilities are nested inside it:

| Submodule | Used by |
| --- | --- |
| `3rd_party/pyssp_workflow` | Composition layer and development tree (submodule only; not imported by the pipeline yet) |
| `3rd_party/pyssp_workflow/3rd_party/pyssp_standard` | Build |
| `3rd_party/pyssp_workflow/3rd_party/pyssp_simulate` | Simulate |
| `3rd_party/pyssp_workflow/3rd_party/pyssp_sysml2` | SysML |
| `3rd_party/pyssp_workflow/3rd_party/sequence_extensions` | Campaign orchestration |
| `3rd_party/pyssp_workflow/3rd_party/pyssp_vv` | Verification and validation capability (measurement, judgment, evidence) |

See [`3rd_party/README.md`](../../3rd_party/README.md) for initialization and
local-patch guidance.

| Tool | Dependency expectation | Environment |
| --- | --- | --- |
| Build | `pyssp_standard` with the refactored model API | Runtime venv |
| Simulate | `pyssp_simulate` plus the selected engines | Runtime venv |
| Compare | Python standard library and repository comparison utilities | Runtime venv or a compatible environment |
| SysML | `pyssp_sysml2` targeting the refactored `pyssp_standard` API | Separate environment allowed |

The SysML checker accepts an explicit executable:

```bash
python3 scripts/check_sysml_roundtrip.py \
  artifacts/models/<model>/<case>/SystemStructure.ssd \
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

## Backward Trace

- [ADR-001](decisions/ADR-001.md) — three-stage pipeline
- [ADR-005](decisions/ADR-005.md) — pyssp ecosystem adoption
- [ADR-006](decisions/ADR-006.md) — standardized artifacts at tool boundaries
