# variation_conditional_excludes

## Origin

Authored in this repository at `architecture/variation_conditional_excludes.sysml`, adapted from the exclusion shape in `docs/breakdown/06-evolution/selected/examples/variation-points/06_constrained_selection.sysml` and the attribute-set shape in `02_attribute_variation.sysml`; the FMU metadata follows `models/ssp/variation_source_swap/`. First added 2026-10-30 with the conditional-branching batch.

## Overview

One structural point, `SourceChoice`, and one attribute point, `ScenarioChoice`, with an exclusion between them: the sine source excludes the high-gain scenario. Four source/scenario combinations exist; the rule admits three. The three legal analyses are built and registered, and the fourth (`sine_high`) is authored so the pruned branch is visible in the architecture but never reaches an SSP.

The `pyssp_sysml2` adapter captures the SysML `constraint` and `assert` and evaluates them after variation selection. `build.py` asks the adapter for each combination and prunes the illegal ones; the CLI would also reject an illegal `--select`. Parameter form: external SSV + external SSM.

## Architecture Source

- `architecture/variation_conditional_excludes.sysml`
- Exportable composition: `System :> SspModel`
- Source point: `variation part def SourceChoice` with `variant part stepImplementation : Step` and `variant part sineImplementation : Sine`
- Attribute point: `variation attribute def ScenarioChoice` with `variant attribute baseline : BaselineScenario` and `variant attribute highGain : HighGainScenario`
- Constraint: `constraint def SineExcludesHighGain` with `chosenSource == SourceChoice::sineImplementation implies chosenScenario != ScenarioChoice::highGain`; a named usage `excludesHighGain` is asserted in every analysis because the scenario point lives on the analysis, not on `System`
- The fixed `gain : Gain` is not varied; the scenario selects its `k` value (3.0 baseline, 9.0 high gain).
- No legacy SSD, SSV, or SSM is checked into the model directory.

## Analyses

- `step_baseline :> Analysis` — step source, baseline scenario. Legal.
- `step_high :> Analysis` — step source, high-gain scenario. Legal.
- `sine_baseline :> Analysis` — sine source, baseline scenario. Legal.
- `sine_high :> Analysis` — sine source, high-gain scenario. Authored but **pruned**: `build.py` puts it in `PRUNED` and `build_fixture` never receives it.
- Each analysis declares its own scenario attribute (`step_baseline_scenario`, `step_high_scenario`, `sine_baseline_scenario`, `sine_high_scenario`) because the adapter addresses attribute usages by name.
- Selection maps are generated from one authored table: `SELECTIONS` holds the legal subset and `PRUNED` the rejected subset. The model scope must resolve every analysis scenario usage, so `MODEL_SCENARIOS` names all four; only the analysis scope selects `sut.source`.
- Experiment: `startTime=0.0`, `stopTime=1.0`, `stepSize=0.001`.
- Each built analysis carries `BaselineScenario.ssv` or `HighGainScenario.ssv` plus `<analysis>.ssm`; the build binds them into the exported SSP after `build_fixture`.
- Artifacts: `artifacts/analyses/variation_conditional_excludes/<analysis>/`; analyses are never exported as SSPs.
- Registry: the three legal analyses are registered on ssp4sim and OMSimulator, comparing `source.y` and `gain.y`; all three comparisons pass their gate.

## Strategy Role

- Isolates a condition that crosses from a structural point to an attribute point: the source choice narrows the legal scenario choices.
- Build-level contract test: `tests/test_variation_cases.py` asserts the per-selection element tree, the packaged external SSV+SSM, the `gain.k` mapping target, and that the guard rejects `sine_high`.
- Catches a constraint bypass (the illegal branch building), a scenario that leaks into the wrong source selection, and a packaged SSV whose `k` came from the wrong variant.
- Both the structural and the parameter side are registered in the cross-engine comparison gate.

## Structure

- `System` = `source : SourceChoice` -> `gain : Gain`; `source.y -> gain.u`. There is no root output port.
- `stepImplementation`: `source` is `Step.fmu`; `sineImplementation`: `source` is `Sine.fmu`.
- `gain` is always one `Gain.fmu`; only its `k` parameter changes with the scenario.
- Signals: `source.y` and `gain.y`.

## Intent

- Prove that a condition between a structural point and an attribute point is a build-time legality rule: legal combinations produce one SSP each, and the illegal combination is pruned before generation.
- Prove that the legal branch reaches the artifact: the packaged SSV carries `k=3` for baseline and `k=9` for high gain, and the fixed gain maps from `gain.k`.

## Expected Behavior

- Baseline scenario: `height=2`, `offset=1`, `startTime=0.25`, `amplitude=2`, `f=1`, `k=3`.
- High-gain scenario: the same values except `k=9`.
- `step_baseline`: `source.y = 1 + 2*[t >= 0.25]`; `gain.y = 3 * source.y`.
- `step_high`: the same `source.y`; `gain.y = 9 * source.y`.
- `sine_baseline`: `source.y = 1 + 2*sin(2*pi*(t-0.25))` for `t >= 0.25` and `1` before it; `gain.y = 3 * source.y`.
- `sine_high` is not built. Its algebraic behavior would be `9 * source.y`, but the build guard rejects the selection before generation.

## Simulation Notes

- The registered compare signals are `source.y` and `gain.y`. `source.y` matches exactly across the engines in all three cases.
- `gain.y` shows the known ssp4sim zero first sample: the raw max abs error is 3 for the baseline cases and 9 for `step_high`, because ssp4sim emits `gain.y = 0` at the first step while OMSimulator already reports the algebraic value. The gate accepts it as a first-sample lag; it is not a wrong `k`.
- `sine_baseline` additionally has a shift-tolerant error of ~5e-7 on both signals, the usual sampling difference.

## Limitations

- The rule is adapter-enforced: `build.py` calls `evaluate` for every authored combination.
- The model scope must resolve every analysis scenario usage, including the pruned analysis, because the adapter collects attribute usages from every analysis that composes `System`. `MODEL_SCENARIOS` is therefore longer than the set of built analyses; dropping a key would make a legal build fail on the pruned analysis's scenario.

## Packaging Notes

- Exported model: `artifacts/models/variation_conditional_excludes/<analysis>/model/`
- Analysis artifacts: `artifacts/analyses/variation_conditional_excludes/<analysis>/`
- Packaged scenario: `resources/BaselineScenario.ssv` or `resources/HighGainScenario.ssv` with `resources/<analysis>.ssm` (external SSV + external SSM)
- Mapping targets: `source.height`, `source.offset`, `source.startTime`, and `gain.k` for the step cases; `source.amplitude`, `source.f`, `source.offset`, `source.startTime`, and `gain.k` for the sine case.
- FMU sources: `models/fmu/Modelica.Blocks.Sources.Step/fmu`, `models/fmu/Modelica.Blocks.Sources.Sine/fmu`, and `models/fmu/Modelica.Blocks.Math.Gain/fmu`
- Build: `python3 scripts/build_models.py run variation_conditional_excludes`
