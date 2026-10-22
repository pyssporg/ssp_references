# DD-008: Study Scenario Generation and SSM Prefix Stripping

**Status:** Accepted
**Layer:** implementation-decision

---

## Context

A study consumes an exported `SspModel` and supplies parameter values plus one
experiment. The exported SSP has parameter connectors on components; the study
binds scenario members to nested `sut.*` paths. The runtime needs an SSV, an
SSM, and experiment data, but must not produce an SSP.

## Decision

Add a study definition for `signal_step_gain`:

```sysml
part def test_baseline :> Study {
  attribute experiment_baseline : Baseline;
  part sut : System;

  attribute nominal : NominalSet;
  bind sut.step.parameters.height = nominal.height;
  bind sut.step.parameters.offset = nominal.offset;
  bind sut.step.parameters.startTime = nominal.startTime;
  bind sut.gain.parameters.k = nominal.k;
}
```

`pyssp_sysml2` gains a `generate study` command (or an equivalent
`generate ssp --study` mode) that emits, under
`artifacts/studies/<model>/<study>/`:

- `NominalSet.ssv` with the scenario values;
- `test_baseline.ssm` with mappings relative to the exported SSP root:
  ```text
  height    -> step.height
  offset    -> step.offset
  startTime -> step.startTime
  k         -> gain.k
  ```
- a study descriptor containing the experiment window, step size, tolerance,
  target SSD name, base model name, and the scenario artifact paths.

Rules:

- The study's `sut` usage is the root of the exported SSP; the `sut.` prefix is
  stripped from SSM targets.
- One study declares one experiment initially.
- A study composition is rejected by `generate ssp`.
- Scenario SSV/SSM files are standardized SSP artifacts; the study descriptor is
  repository-internal.
- Partial set application may emit "members not bound" warnings; this is
  expected when one scenario set targets several components with explicit binds.

## Rationale

Keeping the scenario out of the exported SSP makes studies reusable and keeps
the model artifact stable. Stripping `sut.` is the minimal generic rule that
lets a study compose the model without changing the exported SSD hierarchy.

## Consequences

- The study artifact directory contains no `SystemStructure.ssd` and no `.ssp`.
- The study descriptor becomes the input to runtime scenario injection.
- Experiment data no longer needs to be authored in the exported SSP's
  `experiments.xml`, except for a standalone default.
- The study name is the registry case name.

## Verification

- The generated SSV values match the scenario set.
- The SSM targets are relative to the exported SSP root.
- `generate ssp` on `test_baseline` fails with an explicit "study is not
  exportable" error.
- The study artifacts are reproducible.

## Trace

Implements [PD-006](../../01-product/decisions/PD-006-studies-consume-exported-ssps.md)
and [ADR-009](../../02-architecture/decisions/ADR-009.md). Runtime application is
in [DD-009](./DD-009-runtime-scenario-injection.md).
