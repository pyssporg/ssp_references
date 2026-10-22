# PD-006: Studies Consume Exported SSPs and Are Never Exported

**Status:** Accepted
**Layer:** product-decision

---

## Context

An earlier direction built one SSP per case: every test composition became an
SSP root under `artifacts/models/<model>/<case>/`. That is convenient for LS-REF
packaging but it couples study configuration to model packaging. Changing a
scenario or an experiment window forces an SSP rebuild, and a test composition
can accidentally be exported as if it were the model.

The repository needs a durable separation:

- a model that is exported once;
- studies that apply data and scenarios to that exported model;
- a registry that selects which studies run on which backends.

## Options Considered

1. **One SSP per case** — Keep the current layout; each test composition is an
   SSP root.
2. **Model SSP + study data** — Export the model once; studies supply scenario
   SSV/SSM and experiment data at runtime.
3. **Model SSP only** — Drop study definitions and express everything in the
   registry.

## Decision

Option 2.

- A SysML `part def` marked `:> SspModel` is exportable as an SSP.
- A SysML `part def` marked `:> Study` is never exported as an SSP.
- A study references an exported model through `part sut : <Model>` and supplies:
  - a scenario parameter set and its mappings;
  - one experiment definition (window, step size, tolerance, target).
- The registry maps a model build to one or more studies and selects backends,
  compare signals, reference baselines, and gate policy.
- Scenario data is applied to a runtime copy of the exported SSP. The exported
  SSP is never mutated.

One study declares one experiment initially. Multiple experiments per study are
deferred until the registry and artifact layout distinguish a study/build name
from an experiment/case name.

## Rationale

Separating the model from the study keeps the exported artifact stable while
scenarios and experiment windows evolve. It also prevents a test composition
from being shipped as a model SSP and makes "build once, run many" possible for
parallel campaigns.

## Consequences

- The build produces model SSPs and study artifacts, not one SSP per case.
- Simulation setup must combine an exported SSP with a study scenario and
  experiment descriptor.
- The registry schema needs a build/study split; see
  [DD-009](../../03-implementation/decisions/DD-009-runtime-scenario-injection.md).
- Runtime scenario injection becomes a generic `pyssp_workflow` capability;
  see [ADR-010](../../02-architecture/decisions/ADR-010.md).
- The exported SSP keeps parameter connectors but no study-specific bindings.
  A default `experiments.xml` may still be packaged for standalone use.

## Trace

Satisfies the reproducibility commitment in
[00-intent/intent.md](../../00-intent/intent.md) by keeping the exported model
stable across studies. Builds on [PD-004](./PD-004-sysml-sspmodel-authoring.md).
Export rules are in [ADR-009](../../02-architecture/decisions/ADR-009.md);
runtime application is in [ADR-010](../../02-architecture/decisions/ADR-010.md).
