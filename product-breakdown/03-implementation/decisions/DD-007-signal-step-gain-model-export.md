# DD-007: `signal_step_gain` Model Export

**Status:** Accepted
**Layer:** implementation-decision

---

## Context

`signal_step_gain` is the first fixture ported to SysML authoring. It has two
FMUs (`Step`, `Gain`), one direct connection, and four parameters. It is small
enough to validate the full authoring path without nested systems.

## Decision

Add `models/ssp/signal_step_gain/architecture/signal_step_gain.sysml` containing:

- `port def ParameterInterface;`
- `attribute def ParameterSet;`
- a flat `RealSignal` port definition using `pyssp_flat_connector`;
- `StepParameters` (`height`, `offset`, `startTime`) and `GainParameters` (`k`);
- FMU metadata for `Step` and `Gain` with extracted-FMU sources and
  `CoSimulation`;
- `part def System :> SspModel` with `step`, `gain`, and `connect step.y to gain.u`.

The model SSP carries parameter connectors but **no study bindings**. It is
built to:

```text
artifacts/models/signal_step_gain/model/
```

`build.py`:

1. calls `pyssp_workflow.authoring.derive_ssp_from_sysml` with
   `composition="System"`;
2. unpacks the derived archive with `pyssp_standard` using recursive FMU
   extraction;
3. strips Model Exchange from the unpacked FMUs;
4. writes the build artifact root.

The existing authored SSV under `ssp/resources/` is removed. Scenario values are
supplied by the study in DD-008.

## Rationale

One exported model with a stable SSD proves the `SspModel` export path before
study injection is added. Keeping the scenario out of the exported SSP prevents
the first port from baking in the study contract.

## Consequences

- The model artifact has an SSD with parameter connectors and no
  `ParameterBinding`.
- The model can be inspected independently of the `baseline` study.
- Standalone use falls back to FMU defaults unless a scenario is applied.
- The existing `signal_step_gain` comparison signals (`step.y`, `gain.y`) remain
  valid because the exported SSD root stays `System`.

## Verification

- `pyssp generate ssd` produces `step`, `gain`, `step.y -> gain.u`, and the four
  parameter connectors.
- The generated SSD round-trips through `check_sysml_roundtrip.py --strict`.
- `artifacts/models/signal_step_gain/model/` contains no scenario SSV binding.
- The model build is reproducible.

## Trace

Implements [PD-004](../../01-product/decisions/PD-004-sysml-sspmodel-authoring.md)
and [ADR-007](../../02-architecture/decisions/ADR-007.md). The study is in
[DD-008](./DD-008-study-scenario-generation.md).
