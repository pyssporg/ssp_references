# variation_attribute_set

## Origin

Authored in this repository at `architecture/variation_attribute_set.sysml`, adapted from `docs/breakdown/06-evolution/selected/examples/variation-points/02_attribute_variation.sysml`; the composition and FMU metadata follow `models/ssp/signal_step_gain/`. First added 2026-10-29 with the variation-point batch.

## Overview

One attribute variation point, `ScenarioChoice`, over two complete parameter sets that differ only in `k`: `NominalK3` (`k=3`) and `BoostedK9` (`k=9`). The variation usage `scenario` sits in `System` and binds `step.height`, `step.offset`, `step.startTime`, and `gain.k`. Selection changes parameter values, not topology: the exported SSD is identical except for the parameter-set name. There is no structural variation in this fixture.

## Architecture Source

- `architecture/variation_attribute_set.sysml`
- Exportable composition: `System :> SspModel`
- Variation point: `variation attribute def ScenarioChoice` with `variant attribute nominalK3 : NominalK3` and `variant attribute boostedK9 : BoostedK9`
- Both sets fix `height=2.0`, `offset=1.0`, `startTime=0.25`; only `k` differs (3.0 vs 9.0).
- The usage `attribute scenario : ScenarioChoice` is declared in `System`; four `bind` statements connect it to the step and gain parameter ports.
- No legacy SSD, SSV, or SSM is checked into the model directory.

## Studies

- `nominal_k3 :> Study` selects `sut.scenario=nominalK3`; the model build selects `scenario=nominalK3`.
- `boosted_k9 :> Study` selects `sut.scenario=boostedK9`; the model build selects `scenario=boostedK9`.
- Selection is applied at build time through `build_fixture(selections={study: {"study": {...}, "model": {...}}})`; study keys are rooted at the Study, model keys at `System`.
- Experiment: `startTime=0.0`, `stopTime=1.0`, `stepSize=0.001`.
- The model SSP packages `resources/parameter_sets/NominalK3.ssv` or `BoostedK9.ssv` and references it from the SSD through an inline `ParameterMapping`. The SSD differs only in the set name, which `tests/test_variation_cases.py` asserts.
- The study directory holds only `study.json`: the binds live on `System`, so no study-level SSV or SSM is generated.
- Artifacts: `artifacts/studies/variation_attribute_set/<study>/`; studies are never exported as SSPs.
- Registry: not registered; there is no simulation or comparison evidence.

## Strategy Role

- Isolates attribute variation from structural variation.
- Build-level contract test: the SSD must stay identical across selections except for the set name, while the packaged parameter values move from 3 to 9.
- Catches selection leaking into topology, wrong parameter-set resolution, and a missing `extra/org.pyssp/selection.json` record.
- No simulation gate exists for either study.

## Structure

- `step : Step -> gain : Gain`; `step.y -> gain.u`.
- There is no root output port; the signals are `step.y` and `gain.y`.

## Intent

- Prove that selecting a parameter variant changes only the parameter set, never the element tree or connections.

## Expected Behavior

- Both sets fix `height=2.0`, `offset=1.0`, `startTime=0.25`, so `gain.y = k * (1 + 2*[t >= 0.25])`.
- `nominal_k3`: `gain.y = 3` before 0.25 and `9` from 0.25.
- `boosted_k9`: `gain.y = 9` before 0.25 and `27` from 0.25.
- These are algebraic expectations only; no registry gate confirms them.

## Simulation Notes

- Not registered. The parameter set is packaged in the model SSP, not in the study; a runner that expects a study-level SSV/SSM finds none.
- OMSimulator cannot import the inline `ParameterMapping`; the fixture is ssp4sim-only if it is run. Do not read the FMU defaults as the intended values, and do not claim a passing result without a registry case.

## Packaging Notes

- Exported model: `artifacts/models/variation_attribute_set/<study>/model/`
- Study artifacts: `artifacts/studies/variation_attribute_set/<study>/`
- Packaged FMUs: `resources/Step`, `resources/Gain`
- Packaged parameter sets: `resources/parameter_sets/NominalK3.ssv`, `resources/parameter_sets/BoostedK9.ssv`
- Build: `python3 scripts/build_models.py run variation_attribute_set`
