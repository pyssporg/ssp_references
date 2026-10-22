# DD-009: Runtime Scenario Injection and Registry Build/Case Split

**Status:** Accepted
**Layer:** implementation-decision

---

## Context

The exported model SSP and the study scenario are separate artifacts. The
registry currently assumes one SSP root per `model/case` and one experiment file
inside that root. That assumption no longer holds once a model is exported once
and multiple studies consume it.

## Decision

### Registry split

A model entry names its exported build; a case names its study:

```json
{
  "name": "signal_step_gain",
  "build": "model",
  "compare_signals": ["step.y", "gain.y"],
  "cases": [
    {
      "name": "baseline",
      "study": "test_baseline",
      "backends": ["ssp4sim", "omsimulator", "fmpy"]
    }
  ]
}
```

- `build` defaults to `model` when omitted.
- `study` defaults to the case name when omitted, for transition compatibility.
- The registry remains the exclusive source of truth for active cases and
  backends (PD-002).

### Artifact layout

```text
artifacts/models/<model>/<build>/          exported model SSP root
artifacts/studies/<model>/<study>/         SSV, SSM, study descriptor
artifacts/simulation/<model>/<study>/       setup.json + per-backend runs
artifacts/comparisons/<model>/<study>/      comparisons
```

`setup.json` records:

- the exported SSP root;
- the study name and study artifact directory;
- the scenario SSV/SSM paths;
- the experiment window, step size, and tolerance;
- backends, compare signals, references, and gate policy.

### Runtime injection

- `pyssp_workflow.params` resolves the study scenario and mappings into an
  immutable record.
- `pyssp_workflow.execute` copies the exported SSP into a runtime workspace,
  adds the scenario SSV under `resources/`, and adds a root-level
  `ParameterBinding` with the generated SSM mapping.
- The exported SSP root is never modified.
- The runtime copy is the only input passed to the simulation backends.
- Result canonicalization strips all container names from the runtime SSP, so
  compare signals remain `step.y`, `gain.y`, and similar.

### Campaign nodes

- One `build_model` node per selected model builds the exported SSP.
- One `build_study` node per selected study generates the scenario artifacts.
- Each `simulate` node depends on both its model build and its study build.
- Each `compare` node depends on its simulations.
- `--no-build` skips build and study generation and uses existing artifacts.

## Rationale

The split keeps the exported SSP stable, lets scenarios change without rebuilds,
and makes the model/study boundary visible in both the registry and the artifact
layout. Runtime injection is generic workflow behavior, not fixture code.

## Consequences

- Registry, layout, setup, and campaign code must be updated together.
- The existing `artifacts/models/<model>/baseline/` paths change to
  `artifacts/models/<model>/model/` for migrated fixtures.
- The current `experiments.xml` window/tolerance reader is replaced by the study
  descriptor for migrated studies; the exported SSP may keep a default
  `experiments.xml` for standalone use.
- `pyssp_vv` verdict migration must distinguish `invalid` from `fail` in the
  campaign result.

## Verification

- The runtime SSP copy contains exactly one added root-level
  `ParameterBinding`.
- All three backends produce the expected `step.y` / `gain.y` trajectories.
- The exported SSP checksum is unchanged after simulation.
- Two studies can run against the same exported SSP without a rebuild.
- `run_campaign.py --model signal_step_gain --fail-on-gate` builds once and runs
  the study.

## Trace

Implements [ADR-010](../../02-architecture/decisions/ADR-010.md) and
[PD-005](../../01-product/decisions/PD-005-fixtures-and-policy-not-pipeline.md).
Registry authority remains [PD-002](../../01-product/decisions/PD-002-simulation-registry-source-of-truth.md).
