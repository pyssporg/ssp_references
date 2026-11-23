# SysML Naming Conventions

Conventions the fixtures under `models/` already follow. They describe the
authored SysML dialect, not the emitted SSP artifacts; fixture shape and
required sections are in
[`docs/breakdown/03-implementation/FIXTURE-template.md`](../breakdown/03-implementation/FIXTURE-template.md).
Product-breakdown identifiers are in
[`breakdown-naming.md`](./breakdown-naming.md).

## Packages

- The package is the CamelCase model name, independent of the directory name:
  `SignalStepGain` in `models/ssp/signal_step_gain/architecture/signal_step_gain.sysml`,
  `RavsV2` in `models/ssp/ravs_v2/architecture/01-interfaces.sysml`.

## Composition

- The exportable composition is `part def System :> SspModel`. The legacy
  dcmotor body uses `<Model>Model :> SspModel` instead: `DcMotorModel` in
  `models/ssp/dcmotor/architecture/dcmotor.sysml`.
- Analysis parts are lowercase (`baseline`, `step_high`), and each carries one
  experiment container: `models/ssp/signal_step_add/architecture/05-analyses.sysml`,
  `models/ssp/variation_conditional_excludes/architecture/05-analyses.sysml`.

## Experiments

- The model carries `<Model>DefaultExperiment :> DefaultExperiment`:
  `SignalStepGainDefaultExperiment` in
  `models/ssp/signal_step_gain/architecture/signal_step_gain.sysml`.
- An analysis adds `<Analysis>Experiment :> Experiment` only where it needs its
  own window: `FastExperiment` and `SlowExperiment` in
  `models/ssp/VanDerPol/architecture/VanDerPol.sysml`.

## Metadata

- Component metadata is `<Component>Fmu :> FmuMetadata`; SSP metadata is
  `<Name>Ssp :> SspMetadata`: `StepFmu` and `GainFmu` in
  `models/ssp/signal_step_gain/architecture/signal_step_gain.sysml`,
  `LegacySsp` in `models/ssp/dcmotor/architecture/dcmotor.sysml`.
- `source` is declared only on the metadata definition, never as a flat
  `attribute source` on the model or a component part.

## Parameter Interfaces and Sets

- A parameter interface is `<Block>Parameters :> ParameterInterface` and is
  always used as `in port parameters : <Block>Parameters`: `GainParameters` in
  `models/ssp/signal_step_gain/architecture/signal_step_gain.sysml`.
- Parameter sets are `<Name>Set`, `Nominal*`, `Boosted*`, `Baseline*`, or
  `HighGain*`, all `:> ParameterSet`: `ScenarioSet` in
  `models/ssp/signal_step_gain/architecture/signal_step_gain.sysml`; `NominalK3`
  and `BoostedK9` in
  `models/ssp/variation_attribute_set/architecture/02-parameters.sysml`;
  `BaselineScenario` and `HighGainScenario` in
  `models/ssp/variation_conditional_excludes/architecture/02-parameters.sysml`.
  The legacy VanDerPol sets keep `FastScenario` and `SlowScenario`.

## Signals

- A signal port is named after the FMU variable and is not renamed to fit
  SysML: `heat_load` and `Alt` in
  `models/fmu/scenario/architecture/Scenario.sysml`. This applies to the
  composing SSP architecture as well: `Alt` in
  `models/ssp/ravs_v2/architecture/03-components.sysml`.
- `RealSignal` and `IntegerSignal` carry exactly one member, `value`:
  `models/ssp/signal_step_gain/architecture/signal_step_gain.sysml`,
  `models/ssp/Stair/architecture/Stair.sysml`.

## File Layout

- A split fixture uses `01-interfaces.sysml` through `05-analyses.sysml`, and
  every file repeats the package: `models/ssp/signal_step_add/architecture/`.

## Invariants

- Never declare a core marker locally (`SspModel`, `Analysis`, `Experiment`,
  `FmuMetadata`, `FmuModel`, `SspMetadata`, `ParameterInterface`,
  `ParameterSet`); they come from `PysspCore::*`.
- Imports are file-scoped: a file imports `PysspCore::*` and, only when it
  names a scalar type, `ScalarValues::*`. A sibling file's import does not
  cover it: `models/ssp/signal_step_add/architecture/01-interfaces.sysml`
  keeps `ScalarValues::*` while the same package's `04-structure.sysml`
  does not.
