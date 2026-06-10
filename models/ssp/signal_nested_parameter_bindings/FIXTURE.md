# signal_nested_parameter_bindings

## Origin

Assembled from the shared `models/fmu/Modelica.Blocks.Sources.Step`,
`models/fmu/Modelica.Blocks.Sources.Sine`, `models/fmu/Modelica.Blocks.Math.Gain`,
and `models/fmu/Modelica.Blocks.Math.Add` fixtures.

The root-level parameter values are stored in
`models/ssp/signal_nested_parameter_bindings/ssp/resources/signal_nested_parameter_bindings_parameters.ssv`
and mapped through
`models/ssp/signal_nested_parameter_bindings/ssp/resources/signal_nested_parameter_bindings_mapping.ssm`.

The resolved parameter state after loading is captured in
`models/ssp/signal_nested_parameter_bindings/ssp/resources/signal_nested_parameter_bindings_final_values.ssv`.

## Overview

`signal_nested_parameter_bindings` is a small nested SSP fixture that mixes an
external root parameter set with inline system- and component-scoped parameter
bindings.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- OMSimulator

## Strategy Role

- Nested composite SSP fixture.
- Integration test target for parameter packaging and binding resolution.
- Regression anchor for nested system traversal.
- Exercises system-level, nested-system-level, and component-level parameter
  binding scopes in one fixture.

## Loading Order

The standard describes precedence, not a required chronological load sequence.
For this fixture, the precedence rules are:

1. Higher-level bindings override lower-level bindings.
2. Within the same hierarchy level, later `ParameterBinding` entries override
   earlier ones.
3. A root-system binding therefore overrides a nested-system binding, which
   overrides a component binding inside that nested system.

The SSP 2.0.1 standard says that a parameter source can parameterize complete
sub-hierarchies using hierarchical names, that later `ParameterBinding`
entries at the same hierarchy level take priority, and that higher hierarchy
levels take precedence over lower levels. See section 5.2.3 of the standard
for the full wording: https://ssp-standard.org/docs/2.0.1/

## Structure

- Root step: component-level inline parameter binding
- Root add: external root parameter set
- Nested system: system-level sine binding plus component-level gain binding
- Root sum: `Add.y = Step.y + inner.y`

## Intent

- Exercise both external parameter binding at the root system and internal
  inline parameter binding inside a nested system, plus a component-scoped
  binding inside each of the root and nested systems.
- Validate that packaged resources, nested connectors, and parameter mapping
  all survive SSP assembly.

## Expected Behavior

- `step.y` stays at its offset until the configured step time, then jumps by
  the configured height.
- `inner.y` follows the nested sine/gain configuration.
- `add.y` is the sum of the root step signal and the nested subsystem output.

## Main Failures This Catches

- Wrong resolution of nested system connectors.
- Broken external SSV/SSM packaging.
- Inline parameter values being ignored inside nested systems.
- One-step propagation or binding errors at the system boundary.

## Packaging Notes

- The root system uses the checked-in external SSV and SSM files.
- The nested system keeps its parameter values inline in `SystemStructure.ssd`.
- The FMUs are shared Modelica-generated resources that are packaged during
  the build step.

## Typical Use

- Integration testing for SSP assembly and packaging.
- Cross-engine comparison of nested parameter handling.
