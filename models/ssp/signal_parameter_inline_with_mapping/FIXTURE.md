# signal_parameter_inline_with_mapping

## Origin

Assembled from the shared `models/fmu/Modelica.Blocks.Sources.Step` fixture.

The parameter values are defined inline in the generated `SystemStructure.ssd`
(no external SSV file). The mapping from flat to hierarchical names is stored
in `models/ssp/signal_parameter_inline_with_mapping/ssp/resources/inline_mapping.ssm`.

## Overview

`signal_parameter_inline_with_mapping` is a deterministic signal-propagation SSP
fixture built from a single Step FMU with an inline system-level parameter set
and an external parameter mapping file.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- OMSimulator

## Structure

- Step (inline SSV + external SSM)

## Strategy Role

- Deterministic signal-propagation fixture.
- Gap coverage for inline SSV with external SSM (no `source=` on `<ssd:ParameterBinding>`).
- Pattern A (generated SSD via `build.py`).

## Intent

- Validate that an inline parameter set combined with an external parameter
  mapping is correctly handled by SSP tooling.
- Ensure that flat inline parameter names are correctly mapped to hierarchical
  component parameters via the external SSM.

## Expected Behavior

- Step output transitions at the configured step time, reaching the configured
  height, with no one-step lag.

## Main Failures This Catches

- Inline parameter values being ignored when a mapping is also present.
- Parameter binding with both inline values and external mapping not supported.
- Mapping resolution failure for inline parameters.

## Packaging Notes

- The parameter values are stored inline in the generated `SystemStructure.ssd`
  via `extend_system_parameterset()`.
- The external mapping file `inline_mapping.ssm` is checked in under
  `ssp/resources/` and added as an SSP resource.
- No experiments.xml `<Parameters>` element — all binding is in the SSD.

## Typical Use

- Tight-tolerance comparison tests for inline+external parameter binding.
- Debugging mapping resolution and precedence rules.
