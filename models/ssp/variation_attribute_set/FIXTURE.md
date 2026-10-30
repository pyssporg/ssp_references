# variation_attribute_set

## Origin

Authored in this repository at `architecture/variation_attribute_set.sysml`, adapted from `docs/breakdown/06-evolution/selected/examples/variation-points/02_attribute_variation.sysml`; the composition and FMU metadata follow `models/ssp/signal_step_gain/`. First added 2026-10-29 with the variation-point batch.

## Overview

One attribute variation point, `ScenarioChoice`, over two complete parameter sets that differ only in `k`: `NominalK3` (`k=3`) and `BoostedK9` (`k=9`). Selection changes parameter values, not topology. Each analysis declares its own attribute usage typed by `ScenarioChoice` and binds it to the fixed `step`/`gain` parameters, so the build packages an external SSV plus an external SSM; the two analyses are the only difference in the deployed topology. The selection is authored on each analysis's scenario usage as a feature value (`ScenarioChoice::nominalK3` or `ScenarioChoice::boostedK9`); there is no structural configuration, and `build.py` builds the adapter's legal plans. There is no structural variation in this fixture. Parameter form: external SSV + external SSM.

## Architecture Source

- `architecture/variation_attribute_set.sysml`
- Exportable composition: `System :> SspModel`
- Variation point: `variation attribute def ScenarioChoice` with `variant attribute nominalK3 : NominalK3` and `variant attribute boostedK9 : BoostedK9`
- Both sets fix `height=2.0`, `offset=1.0`, `startTime=0.25`; only `k` differs (3.0 vs 9.0).
- Each analysis declares its own usage: `nominal_scenario : ScenarioChoice` in `nominal_k3`, `boosted_scenario : ScenarioChoice` in `boosted_k9`, each with four `bind` statements to the step and gain parameter ports.
- No legacy SSD, SSV, or SSM is checked into the model directory.

## Analyses

- `nominal_k3 :> Analysis` declares `attribute nominal_scenario : ScenarioChoice = ScenarioChoice::nominalK3`; the analysis's own scenario usage carries its variant as a feature value.
- `boosted_k9 :> Analysis` declares `attribute boosted_scenario : ScenarioChoice = ScenarioChoice::boostedK9`; the analysis's own scenario usage carries its variant as a feature value.
- Binds target `sut.step.parameters.height/offset/startTime` and `sut.gain.parameters.k`; the packaged SSM targets `step.height`, `step.offset`, `step.startTime`, and `gain.k`.
- The adapter derives the selection from each analysis's scenario feature value and returns a plan; `build.py` builds the `legal` plans.
- Experiment: `startTime=0.0`, `stopTime=1.0`, `stepSize=0.001`.
- Each analysis directory carries its own SSV/SSM (`NominalK3.ssv`/`nominal_k3.ssm` or `BoostedK9.ssv`/`boosted_k9.ssm`); the build binds them into the exported SSP after `build_fixture`.
- The exported SSD is identical across the two analyses apart from the binding: the packaged SSV selects `k=3.0` vs `k=9.0`.
- Artifacts: `artifacts/analyses/variation_attribute_set/<analysis>/`; analyses are never exported as SSPs.
- Registry: both `nominal_k3` and `boosted_k9` are registered on ssp4sim and OMSimulator, comparing `step.y` and `gain.y`; both comparisons pass their gate.

## Strategy Role

- Isolates attribute variation from structural variation.
- Build-level contract test: the SSD must stay identical across selections except for the binding, while the packaged parameter values move from 3 to 9.
- Catches selection leaking into topology, wrong parameter-set resolution, a scenario packaged as an inline mapping, and a missing `extra/org.pyssp/selection.json` record.
- Both cases are registered in the cross-engine comparison gate; both comparisons currently pass.

## Structure

- `step : Step -> gain : Gain`; `step.y -> gain.u`.
- There is no root output port; the signals are `step.y` and `gain.y`.

## Intent

- Prove that selecting a parameter variant changes the packaged parameter set and its external SSV/SSM mapping, never the element tree or connections.

## Expected Behavior

- Both sets fix `height=2.0`, `offset=1.0`, `startTime=0.25`, so `gain.y = k * (1 + 2*[t >= 0.25])`.
- `nominal_k3`: `gain.y = 3` before 0.25 and `9` from 0.25.
- `boosted_k9`: `gain.y = 9` before 0.25 and `27` from 0.25.

## Simulation Notes

- Both cases run the built SSP as-is; the scenario is packaged, not injected.
- The registered gate passes for both cases on the shift-tolerant metric (0 for `step.y` and `gain.y`). The raw `gain.y` max abs error equals `k` (3 on nominal, 9 on boosted) and comes from ssp4sim's zero first sample; it is a lag, not a k misapplication, and the gate accepts it.

## Limitations

- The selection is authored as a feature value on each analysis's scenario usage and the adapter returns `legal`, `violated`, or `invalid`; a `violated` analysis is expected only where the fixture documents a pruned branch.

## Packaging Notes

- Exported model: `artifacts/models/variation_attribute_set/<analysis>/model/`
- Analysis artifacts: `artifacts/analyses/variation_attribute_set/<analysis>/`
- Packaged FMUs: `resources/Step`, `resources/Gain`
- Packaged parameter sets: `resources/NominalK3.ssv` or `resources/BoostedK9.ssv`, with `resources/<analysis>.ssm` (external SSV + external SSM)
- Selection record: `extra/org.pyssp/selection.json` records the derived selection; there is no configuration name because each analysis composes `System` directly.
- Build: `python3 scripts/build_models.py run variation_attribute_set`
