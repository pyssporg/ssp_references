# signal_nested_external_bindings

## Origin

Assembled from the shared `models/fmu/Modelica.Blocks.Sources.Step` and
`models/fmu/Modelica.Blocks.Sources.Sine` fixtures.

The nested system's parameter values are stored in
`models/ssp/signal_nested_external_bindings/ssp/resources/inner_parameters.ssv`
with the external mapping in
`models/ssp/signal_nested_external_bindings/ssp/resources/inner_mapping.ssm`.

## Overview

`signal_nested_external_bindings` is a nested SSP fixture that combines a root
Step component with inline parameter binding and a nested system containing a
Sine component with external SSV+SSM bindings.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- OMSimulator

## Strategy Role

- Nested composite SSP fixture.
- Gap coverage for external SSV+SSM bindings inside a nested subsystem.
- Pattern C (checked-in `SystemStructure.ssd`).

## Structure

- Root Step: inline component-level parameter binding (height=1.0, offset=0.0,
  startTime=0.25)
- Root connector: `y` (output)
- Inner system `inner`: Sine component with external SSV+SSM binding
- Inner connector: `y` (output)
- Connections: `sine.y → inner.y` and `step.y → system.y`

## Intent

- Validate that external SSV and SSM files are correctly resolved when placed
  inside a nested system-level `<ssd:ParameterBinding>`.
- Ensure that flat names in the SSV are correctly mapped to hierarchical
  targets via the SSM inside the nested scope.

## Expected Behavior

- `step.y` stays at its offset (0.0) until the configured step time (0.25),
  then jumps by height (1.0) to 1.0.
- `inner.y` follows the Sine configuration: amplitude=2.0, f=5.0, offset=0.5.
- Root output `system.y` equals `step.y`.

## Main Failures This Catches

- Wrong resolution of nested system external parameter bindings.
- Flat-to-hierarchical mapping failure inside a nested scope.
- External SSV/SSM files not being packaged into the SSP.
- Missing or incorrect resource paths inside a nested system.

## Packaging Notes

- The root system uses inline ParameterValues for the Step component.
- The nested system uses external SSV+SSM files checked in under
  `ssp/resources/`.
- The FMUs are shared Modelica-generated resources packaged during the build
  step.
- The `SystemStructure.ssd` is checked in (Pattern C).

## Typical Use

- Integration testing for nested external parameter packaging.
- Cross-engine comparison of nested system parameter binding resolution.
