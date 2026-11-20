# ravs_v2

Reference Aircraft Vehicle Systems (RAVS), version 2: the D16 aerospace
hydraulic/thermal demonstrator.

## Version

- v1 is the legacy EMBRACE-derived composite (`models/ssp/ravs_v1`).
- v2 is the D16 aerospace demo SSP contributed as
  `opsc_d16_aerospace_demo.ssp`.
- Both are separate models in the registry, and both are exercised by tests.
- DEC-001 (accepted 2026-11-19) fixes the versioned family: neither version
  replaces the other.

## Origin

Source archive: `opsc_d16_aerospace_demo.ssp` (SSP 1.0, 24.4 MB), added to the
workspace root on 2026-11-19. It carries a single `SystemStructure.ssd`, 13
component FMUs, and one UQ setup file. The FMU bodies were unpacked from the
archive and are checked in under `resources/`; the archive itself is not part
of this repository.

The FMUs originate from the OpenScaling D16 demonstrator. The Modelica sources
live in the sibling `openscaling` checkout under
`ModelicaDemonstratorSource/Source/OpenScaling/ParkerSimulationPackage/`
(`D16_aero.mo`, `D16_auto.mo`, and their stimuli variants).

## Overview

`ravs_v2` is a hydraulic/thermal/atmospheric composite: eight FMI 2.0
CoSimulation FMUs wired over 37 top-level connections plus the nested `valve`
subsystem, which has its own boundary ports. It is the first fixture in the
repository that exercises subsystem nesting and boundary connectors from SysML.

## Architecture Source

- `architecture/01-interfaces.sysml` — the flat scalar signal ports, the
  `FluidState` fluid port (plain and conjugated), the `SwSignals` grouped
  proxy port, and the two parameter interfaces (`InterfaceModelParameters`,
  `ValveModelParameters`).
- `architecture/02-parameters.sysml` — scenario set and experiment window.
- `architecture/03-components.sysml` — FMU metadata, the six top-level
  components, the two `valve` members, and the nested `valve` definition.
- `architecture/04-structure.sysml` — `System :> SspModel` composition and
  wiring.
- `architecture/05-analyses.sysml` — `baseline :> Analysis` and the parameter
  binds.
- No legacy SSD, SSV, or SSM is checked in.

`System` is exported from SysML; the
[port dialect](../../../docs/reference/port-dialect.md) explains how ports are
shaped around FMU variable names. Here `fuel.pmhn` is `FluidState` (`pmhn.p`
output, `pmhn.m` input) while `fuel.pmh` is `FluidStateConjugate`. The source SSD has
no `<Dimension>` entries, so the `X[1..3]` variables are three distinct
scalars.

Three deviations from the source SSD are deliberate:

- **Connector orientation.** SysML requires boundary inputs at the start and
  boundary outputs at the end of a connection. Eight `valve` boundary
  connections therefore run in the opposite direction to the archive's SSD.
  The endpoint pairs are identical; SSP connections are undirected.
- **Unused components.** `FMU_16_aero_stimuli`, `FMU_16_auto_interface`,
  `FMU_16_auto_stimuli`, `FMU_UQ_interface`, and the UQ setup file
  `od_L90LS_UD_OS_OS.xml` are not referenced by the SSD and are not carried.
- **Enumeration signal.** `ecs_sw`'s `Input.Aircraft_State` is an FMI
  Enumeration variable; the dialect has no enumeration type, so the `SwSignals`
  proxy port carries it as `attribute Aircraft_State : Integer`, and `adaption`
  takes a matching `in port Aircraft_State : RealSignal`.

The two source `ParameterSet`s are informative duplicates of the FMU start
values. `consumer` and `ecs_hw` additionally declare non-default starts for
`cd.DPlin` and `cd.mmin`; the archive maps neither, so they stay at the FMU
defaults here as well.

## Analyses

- `baseline :> Analysis`
- Scenario set: `ScenarioSet` in `architecture/02-parameters.sysml`, applied to
  `interface_model` and `valve_model`.
- Experiment window and step: see `architecture/02-parameters.sysml`; the
  0.0–10.0 bounds are the exported `DefaultExperiment`.
- The source SSD has no `<DefaultExperiment>`. The window is derived: 10 s is
  the common stop time of the D16 FMUs, and 0.0333 s is the `ecs_sw` step. The
  Modelica-derived FMUs default to a 1 s window and would truncate the run.
- Artifacts: `artifacts/analyses/ravs_v2/baseline/`
- Analyses are never exported as SSPs.

## Structure

Wiring, including the nested `valve` connections, lives in
`architecture/04-structure.sysml`.

## Strategy Role

- Composite SSP model.
- Nested-subsystem and boundary-connector coverage.
- Pre-merge comparison candidate.

## Intent

- Exercise subsystem nesting and boundary ports, which no earlier SysML
  fixture covered at this size.
- Carry an externally authored, resource-heavy demonstrator into the standard
  build/simulate/compare pipeline.

## Expected Behavior

- The eight FMUs exchange the D16 signal set over the source wiring.
- The two parameter sets apply their values; they equal the FMU defaults, so
  trajectories are unchanged by parameter binding alone.
- The `omsimulator` baseline completes with finite signals; a cross-engine
  gate waits for a second backend that can load the `adaption` FMU.

## Main Failures This Catches

- Export of a nested `<System>` with its own boundary connectors.
- Fan-in at a subsystem boundary (`valve.p1`) and fan-out from one source.
- Quoted dotted names surviving into the SSD without quotes.
- Eight-FMU orchestration and resource loading.
- Enumeration variables crossing a connection into an Integer port.

## Simulation Notes

- The build applies the scenario as an external SSV plus SSM.
- The runtime runs the built SSP as-is; it does not inject a scenario.
- `validate_fmus=False`: `L90LS_UD_OS_OS` declares both ModelExchange and
  CoSimulation, and the pyssp_standard FMI2 reader keeps only the first
  interface.

## Packaging Notes

- Exported model: `artifacts/models/ravs_v2/baseline/model/`
- Analysis artifacts: `artifacts/analyses/ravs_v2/baseline/`
- FMU sources: `models/ssp/ravs_v2/resources/{adaption,atmos,consumer,ecs_hw,ecs_sw,fuel,interface_model,valve_model}`
- Build: `python3 scripts/build_models.py run ravs_v2`
- The source archive is not checked in; `resources/` holds the unpacked FMU
  bodies that the archive carried.

## Engine-Specific Notes

`omsimulator` completes the baseline window (296 records, no non-finite
values). It emits `fmi2GetRealOutputDerivatives` warnings from `fuel` at
`t=0`; they do not affect the recorded signals.

`ssp4sim` cannot run this fixture: it segfaults while instantiating
`adaption`. The same crash reproduces on the unpacked source archive
(`SystemStructure.ssd` plus the original `.fmu` files), so it is a property of
the `AdaptionUnit` FMU and not of the SysML export. The registry therefore
lists `omsimulator` only.

No trusted reference trajectory has been recorded yet. The first comparison
run establishes it; until then the fixture has no cross-engine gate.

## Typical Use

- Validating engine behavior on a nested, resource-heavy aerospace model where
  subsystem boundaries and signal fan-in/fan-out dominate the wiring.
