# Co-Simulation Fixture Mapping

This document complements
[co_simulation_test_strategy.md](./co_simulation_test_strategy.md)
by mapping concrete fixtures to the strategy and defining the custom composite
fixtures needed for signal-propagation coverage.

## Purpose

The test strategy is organized around three broad fixture classes:

- Simple reference models.
- Deterministic signal-propagation building blocks.
- Larger composite SSP models.

This document answers two practical questions:

1. Which existing fixtures support which parts of the strategy?
2. Which additional custom fixtures should be added to close the remaining
   gaps, especially for signal propagation?

Detailed notes for each SSP model now live in the corresponding
`models/ssp/<name>/FIXTURE.md` file.

## Existing Fixture Mapping
### Simple Reference SSP Fixtures

These are the main fast-running behavioral checks.

| Fixture | Strategy Role | Detail |
| --- | --- | --- |
| `BouncingBall` | Simple reference model | [BouncingBall](../models/ssp/BouncingBall/FIXTURE.md) |
| `VanDerPol` | Simple reference model | [VanDerPol](../models/ssp/VanDerPol/FIXTURE.md) |
| `Dahlquist` | Simple reference model | [Dahlquist](../models/ssp/Dahlquist/FIXTURE.md) |
| `Stair` | Simple reference model | [Stair](../models/ssp/Stair/FIXTURE.md) |
| `Resource` | Simple reference model | [Resource](../models/ssp/Resource/FIXTURE.md) |

### Composite SSP Fixtures

These cover more realistic coupling behavior.

| Fixture | Strategy Role | Detail |
| --- | --- | --- |
| `dcmotor` | Composite SSP model | [dcmotor](../models/ssp/dcmotor/FIXTURE.md) |
| `embrace` | Composite SSP model | [embrace](../models/ssp/embrace/FIXTURE.md) |

### Reusable FMU Building Blocks

These are the basis for deterministic signal-propagation fixtures.

| FMU | Role In Strategy | Main Use |
| --- | --- | --- |
| `Modelica.Blocks.Sources.Step` | Deterministic source | Reveals timing, ordering, and one-step lag |
| `Modelica.Blocks.Sources.Sine` | Deterministic source | Reveals amplitude, phase, and propagation drift |
| `Modelica.Blocks.Math.Gain` | Algebraic transform | Checks scaling and direct feedthrough |
| `Modelica.Blocks.Math.Add` | Algebraic combiner | Checks fan-in, summation, and connector mapping |
| `Modelica.Blocks.Math.Product` | Algebraic combiner | Checks multiplicative propagation and multi-input ordering |

Use these building blocks for:

- Minimal SSP fixtures with easy-to-predict outputs.
- Tight-tolerance comparison tests.
- Diagnosing scheduling and connection issues without physical-model complexity.

### Implemented Custom Signal-Propagation Fixtures

These fixtures now exist as SSP models under `models/ssp/`.

| Fixture | Status | Detail |
| --- | --- | --- |
| `signal_step_gain` | Implemented | [signal_step_gain](../models/ssp/signal_step_gain/FIXTURE.md) |
| `signal_step_add` | Implemented | [signal_step_add](../models/ssp/signal_step_add/FIXTURE.md) |
| `signal_fanout_gain` | Implemented | [signal_fanout_gain](../models/ssp/signal_fanout_gain/FIXTURE.md) |
| `signal_sine_gain_add` | Implemented | [signal_sine_gain_add](../models/ssp/signal_sine_gain_add/FIXTURE.md) |
| `signal_step_product` | Implemented | [signal_step_product](../models/ssp/signal_step_product/FIXTURE.md) |
| `signal_delay_detector` | Implemented | [signal_delay_detector](../models/ssp/signal_delay_detector/FIXTURE.md) |
| `signal_algebraic_loop` | Implemented | [signal_algebraic_loop](../models/ssp/signal_algebraic_loop/FIXTURE.md) |
| `signal_nested_algebraic_loop` | Implemented | [signal_nested_algebraic_loop](../models/ssp/signal_nested_algebraic_loop/FIXTURE.md) |
| `signal_parameter_inline_with_mapping` | Implemented | [signal_parameter_inline_with_mapping](../models/ssp/signal_parameter_inline_with_mapping/FIXTURE.md) |
| `signal_nested_external_bindings` | Implemented | [signal_nested_external_bindings](../models/ssp/signal_nested_external_bindings/FIXTURE.md) |

## Coverage Assessment

The repository already has good coverage for:

- Basic continuous behavior.
- Event handling.
- Larger composite SSP execution.
- Cross-engine result comparison.

The main remaining gap is engine-side validation and regression coverage, not
fixture construction.

That gap matters because many orchestration bugs are easiest to detect in
fixtures where:

- The expected signal relationship is obvious.
- There is little or no internal state to mask errors.
- A wrong execution order or step boundary shows up immediately.

## Packaging Coverage

The deterministic signal fixtures now cover the main packaging alternatives:

- `signal_step_gain`, `signal_fanout_gain`, and `signal_delay_detector` use
  checked-in external `.ssv` files linked during the SSP build.
- `signal_step_add` uses a checked-in external `.ssv` plus an external
  `.ssm` mapping linked during the SSP build.
- `signal_step_product` generates the external `.ssv` and `.ssm` during its
  build script before linking them into the SSP.
- `signal_sine_gain_add` remains the inline system-level regression anchor.
- `signal_algebraic_loop` and `signal_nested_algebraic_loop` use checked-in
- `signal_parameter_inline_with_mapping` uses inline system-level SSV with an
  external SSM mapping, covering the case where the ParameterBinding has
  inline `<ssd:ParameterValues>` plus an external `<ssd:ParameterMapping>`.
- `signal_nested_external_bindings` uses external SSV and SSM bindings inside
  a nested `<ssd:System>`, covering the nested system external parameter
  packaging path.
-  uses inline system-level SSV with an
  external SSM mapping, covering the case where the ParameterBinding has
  inline  plus an external .
-  uses external SSV and SSM bindings inside
  a nested , covering the nested system external parameter
  packaging path.
  external `.ssv` files and deliberately close feedback cycles instead of
  remaining acyclic.

## Comparison Expectations Per Fixture Class

### Simple Reference SSPs

- Moderate to tight tolerances depending on the model.
- Focus on overall behavioral agreement and event timing.

### Deterministic Signal-Propagation Fixtures

- Very tight tolerances.
- Comparison should emphasize exact algebraic relationships at each recorded
  step.
- Missing or delayed transitions should be treated as failures.

### Larger Composite SSPs

- Broader tolerances.
- Focus on signal coverage, trend agreement, and absence of major orchestration
  errors.

## Pass/Fail Guidance

The custom propagation fixtures should be interpreted more strictly than the
larger physical models.

Recommended pass/fail rules for these fixtures:

- Expected output signals must all be present.
- Time coverage must match the requested simulation window.
- Step transitions must occur at the expected recorded step.
- Algebraic relationships must hold within very small tolerances.
- Any apparent one-step lag should be considered a failure unless explicitly
  designed into the fixture.
- A closed algebraic loop that fails to converge, converges to the wrong
  fixed point, or only works in one backend should be treated as a regression.

## Immediate Next Step

The most useful follow-up is to run the full deterministic signal set through
the comparison workflow and keep the full mix of external-parameter fixtures,
generated-parameter fixtures, the inline regression anchor, and the new
algebraic-loop cases in the maintained regression suite.
