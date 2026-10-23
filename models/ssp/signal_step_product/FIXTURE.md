# signal_step_product

## Origin

Assembled from shared Modelica FMUs. The model and study are authored in SysML
at `architecture/signal_step_product.sysml`.

## Overview

`signal_step_product` is a deterministic signal-propagation SSP fixture built from shared
Modelica FMUs. Parameter form: external SSV + external SSM.

## Architecture Source

- `architecture/signal_step_product.sysml`
- Exportable composition: `System :> SspModel`
- Study composition: `baseline :> Study`
- No legacy SSD, SSV, or SSM is checked into the model directory.

## Studies

- `baseline :> Study`
- Scenario set: `ScenarioSet`
- Experiment: `startTime=0.0`, `stopTime=1.0`, `stepSize=0.001`
- Tolerance is not part of the experiment; it comes from the FMU model
  descriptions.
- Artifacts: `artifacts/studies/signal_step_product/baseline/`
- Studies are never exported as SSPs.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- OMSimulator
- FMPy

## Structure

- `Step -> Product.u1`
- `Sine -> Product.u2`

## Strategy Role

- Deterministic signal-propagation fixture.
- Priority 2 propagation test.
- Multiplicative gating reproducer.

## Intent

- Validate deterministic gating behavior through a multiplicative block.

## Expected Behavior

- Output is zero before the step activates.
- Output follows the sine scaled by the step level after activation.

## Main Failures This Catches

- Wrong time alignment between inputs.
- Incorrect product input wiring.
- Step-boundary ordering issues.

## Simulation Notes

- The build packages the `ScenarioSet` scenario into the exported SSP in the
  fixture's parameter form.
- The runtime runs the built SSP as-is; it does not inject a scenario.
- Form: external SSV + external SSM.

## Packaging Notes

- Exported model: `artifacts/models/signal_step_product/baseline/model/`
- Study artifacts: `artifacts/studies/signal_step_product/baseline/`
- FMU sources:
- `models/fmu/Modelica.Blocks.Sources.Step/fmu`
- `models/fmu/Modelica.Blocks.Sources.Sine/fmu`
- `models/fmu/Modelica.Blocks.Math.Product/fmu`
- Build: `python3 scripts/build_models.py run signal_step_product`

## Typical Use

- Tight-tolerance cross-engine comparison.
