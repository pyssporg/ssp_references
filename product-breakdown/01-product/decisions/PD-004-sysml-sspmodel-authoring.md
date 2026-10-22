# PD-004: SysML `SspModel` Definitions and Parameter Sets Are the Authoring Source

**Status:** Accepted
**Layer:** product-decision

---

## Context

SSP fixtures are currently authored directly in `build.py`, hand-written SSD
XML, and checked-in SSV/SSM files. SysML v2 is used only by the SSD → SysML →
SSD round-trip checker. That leaves the model structure, FMU metadata, parameter
interfaces, and parameter values spread across several unrelated formats.

The repository wants one authored source for what a model *is* and what
parameters it exposes, with the SSP archive treated as a build artifact.

## Options Considered

1. **Keep XML and SSV authoring** — Continue writing SSD wiring and parameter
   files by hand or through `pyssp_standard` calls in `build.py`.
2. **Make SysML the authoring source** — Author `SspModel` definitions, ports,
   FMU metadata, parameter interfaces, and parameter sets in SysML v2; derive
   SSD, SSV, and SSP artifacts during the build.
3. **Hybrid** — Use SysML for structure but keep parameter sets in SSV files.

## Decision

Option 2, staged across fixtures.

- A SysML `part def` marked `:> SspModel` is an exportable model definition.
- Component definitions, flat ports, FMU metadata, and wiring are authored in
  SysML.
- Parameter interfaces (`port def ... :> ParameterInterface`) are authored in
  SysML.
- Scenario parameter sets (`attribute def ... :> ParameterSet`) are authored in
  study definitions and applied to an exported model at runtime.
- The exported `.ssp` archive and its `SystemStructure.ssd` are build artifacts,
  not checked-in sources. The exported model carries parameter interfaces, not
  study-specific values.
- Studies that supply scenarios and experiment data are authored separately and
  are never exported as SSPs (PD-006).

Legacy fixtures remain on their current authoring path until they are ported
individually. The first port is `signal_step_gain`.

## Rationale

SysML v2 is the only authored format that can express structure, FMU metadata,
parameter interfaces, and scenario values in one place. `pyssp_sysml2` already
generates SSD, SSV, SSM, FMI descriptions, and complete SSP archives from that
model. Keeping a second authored SSD/SSV path would preserve two sources of
truth and make drift inevitable.

## Consequences

- A migrated build requires a `pyssp` executable and the `pyssp_sysml2` CLI.
- Generated SSD files are not checked in; study SSV/SSM files are generated
  study artifacts. The SysML model and study definitions are the review surface.
- Parameter changes become SysML edits, not SSV edits.
- The build can no longer be understood from `build.py` alone; the model
  directory must include `architecture/*.sysml`.
- Existing fixtures can be ported incrementally without changing the pipeline
  contract.

## Trace

Satisfies the reproducibility and explicit-provenance commitments in
[00-intent/intent.md](../../00-intent/intent.md). The architectural boundary is
defined in [ADR-007](../../02-architecture/decisions/ADR-007.md); export rules
are in [ADR-009](../../02-architecture/decisions/ADR-009.md).
