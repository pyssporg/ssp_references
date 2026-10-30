# variation_conditional_requires

## Origin

Authored in this repository under `architecture/`, adapted from the constrained-selection shape in `docs/breakdown/06-evolution/selected/examples/variation-points/06_constrained_selection.sysml`; the FMU metadata follows `models/ssp/variation_source_swap/`. First added 2026-10-30 with the conditional-branching batch.

## Overview

Two structural variation points, `SourceChoice` and `GainChoice`, with one legality rule between them: selecting the sine source requires the single gain stage. Four source/gain combinations exist; the rule admits three. The three legal analyses are built and registered, and the fourth (`sine_two`) is authored so the pruned branch is visible in the architecture but never reaches an SSP.

The `pyssp_sysml2` adapter captures the SysML `constraint` and `assert` and evaluates them after variation selection. Each analysis composes a configuration (`StepSingleSystem`, `StepTwoSystem`, `SineSingleSystem`, `SineTwoSystem`) that binds both points; the adapter returns a plan with status `legal`, `violated`, or `invalid`, and `build.py` builds only the `legal` plans. Parameter form: external SSV + external SSM.

## Architecture Source

- `architecture/` split by section: `01-interfaces.sysml`,
  `02-parameters.sysml`, `03-components.sysml`, `04-structure.sysml`,
  `05-analyses.sysml`
- Exportable composition: `System :> SspModel`
- Source point: `variation part def SourceChoice` with `variant part stepImplementation : Step` and `variant part sineImplementation : Sine`
- Gain point: `variation part def GainChoice` with `variant part singleStage : Gain` and `variant part twoStages : CascadedGain`
- Constraint: `constraint def SineRequiresSingleStage` with `chosenSource == SourceChoice::sineImplementation implies chosenGain == GainChoice::singleStage`; a named usage `requiresSingleStage` is asserted on `System`
- `CascadedGain` has no parameter port of its own: it exposes `u`/`y` and contains `firstStage` and `secondStage`. The analysis binds the two internal stages directly, avoiding the parameter-port connection the adapter rejects.
- No legacy SSD, SSV, or SSM is checked into the model directory.

## Analyses

- `step_single :> Analysis` composes `StepSingleSystem` (`source=SourceChoice::stepImplementation`, `gain=GainChoice::singleStage`). Legal.
- `step_two :> Analysis` composes `StepTwoSystem` (`source=SourceChoice::stepImplementation`, `gain=GainChoice::twoStages`). Legal.
- `sine_single :> Analysis` composes `SineSingleSystem` (`source=SourceChoice::sineImplementation`, `gain=GainChoice::singleStage`). Legal.
- `sine_two :> Analysis` composes `SineTwoSystem` (`source=SourceChoice::sineImplementation`, `gain=GainChoice::twoStages`). The adapter reports it as `violated`, so `build.py` never builds it; the test pins it as the expected violated analysis.
- Experiment: `startTime=0.0`, `stopTime=1.0`, `stepSize=0.001`.
- Each built analysis carries `ScenarioSet.ssv` and `<analysis>.ssm`; the build binds them into the exported SSP after `build_fixture`.
- Artifacts: `artifacts/analyses/variation_conditional_requires/<analysis>/`; analyses are never exported as SSPs.
- Registry: the three legal analyses are registered on ssp4sim and OMSimulator, comparing `source.y`; all three comparisons pass their gate.

## Strategy Role

- Isolates a condition between two structural variation points: the source choice narrows the legal gain choices.
- Build-level contract test: `tests/test_variation_cases.py` asserts the per-selection element tree, the packaged external SSV+SSM, the mapping targets, and that the adapter reports `sine_two` as `violated`.
- Catches a constraint bypass (the illegal branch building), a rule that is only documented and never enforced, a source selection that silently changes the gain topology, and a two-stage gain that loses a stage parameter binding.
- Both legal structural shapes are registered in the cross-engine comparison gate.

## Structure

- `System` = `source : SourceChoice` -> `gain : GainChoice`; `source.y -> gain.u`. There is no root output port.
- `singleStage`: `gain` is one `Gain` component.
- `twoStages`: `gain` is a `CascadedGain` subsystem containing `firstStage` and `secondStage`, wired `u -> firstStage.u`, `firstStage.y -> secondStage.u`, `secondStage.y -> y`.
- Signals: `source.y`; for the single stage `gain.y`; for the two-stage branch `gain.firstStage.y` and `gain.secondStage.y` (ssp4sim does not expose the subsystem-level `gain.y`).

## Intent

- Prove that a condition over variation points is a build-time legality rule: legal combinations produce one SSP each, and the illegal combination is pruned before generation.
- Prove that the conditional branch is visible in the artifact: the single-stage case packages one Gain, while the two-stage case packages a synthesized `gain` subsystem with two Gains.

## Expected Behavior

- Packaged set: `height=2`, `offset=1`, `startTime=0.25`, `amplitude=2`, `f=1`, `k=3`.
- `step_single`: `source.y = 1 + 2*[t >= 0.25]`; `gain.y = 3 * source.y`.
- `step_two`: `source.y` is the same; `firstStage.y = 3 * source.y`, `secondStage.y = 9 * source.y`.
- `sine_single`: `source.y = 1 + 2*sin(2*pi*(t-0.25))` for `t >= 0.25` and `1` before it; `gain.y = 3 * source.y`.
- `sine_two` is not built. Its algebraic behavior would be `9 * source.y`, but the adapter reports the selection as `violated` and it never reaches generation.

## Simulation Notes

- The registered compare signal is `source.y` for all three legal cases. The source selection is therefore covered by the gate; the gain branch is covered by the structural tests and by the OMSimulator-only subsystem signal.
- `step_single` and `step_two` compare `source.y` with zero error. `sine_single` has a shift-tolerant max error of ~5e-7, the usual sampling difference between the engines.
- ssp4sim exposes the two-stage branch only through the leaf signals `firstStage.y` and `secondStage.y`; it does not emit `gain.y` for a synthesized subsystem. This is why the registry does not compare `gain.y`.
- The first-stage signal shows the known ssp4sim zero first sample: `firstStage.y` is 0 at the first step and 3 from the next step onward. It is a lag, not a wrong gain.

## Limitations

- The selection is authored by each analysis's configuration and the adapter returns `legal`, `violated`, or `invalid`; a `violated` analysis is expected only where the fixture documents a pruned branch.

## Packaging Notes

- Exported model: `artifacts/models/variation_conditional_requires/<analysis>/model/`
- Analysis artifacts: `artifacts/analyses/variation_conditional_requires/<analysis>/`
- Packaged scenario: `resources/ScenarioSet.ssv` with `resources/<analysis>.ssm` (external SSV + external SSM)
- Mapping targets: `source.height`, `source.offset`, `source.startTime`, and `gain.k` for the single-stage cases; `source.height`, `source.offset`, `source.startTime`, `gain.firstStage.k`, and `gain.secondStage.k` for `step_two`.
- FMU sources: `models/fmu/Modelica.Blocks.Sources.Step/fmu`, `models/fmu/Modelica.Blocks.Sources.Sine/fmu`, and `models/fmu/Modelica.Blocks.Math.Gain/fmu`
- Selection record: `extra/org.pyssp/selection.json` records the composed configuration and its derived selection.
- Build: `python3 scripts/build_models.py run variation_conditional_requires`
