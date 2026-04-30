# Co-Simulation Fixture Mapping

This document complements
[co_simulation_test_strategy.md](co_simulation_test_strategy.md)
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

## Coverage Assessment

The repository already has good coverage for:

- Basic continuous behavior.
- Event handling.
- Larger composite SSP execution.
- Cross-engine result comparison.

The main remaining gap is deliberate coverage of signal-propagation behavior in
small deterministic composite systems.

That gap matters because many orchestration bugs are easiest to detect in
fixtures where:

- The expected signal relationship is obvious.
- There is little or no internal state to mask errors.
- A wrong execution order or step boundary shows up immediately.

## Planned Signal-Propagation Fixtures

These fixtures are still planned and currently only have design notes.

| Fixture | Status | Detail |
| --- | --- | --- |
| `signal_sine_gain_add` | Planned | [signal_sine_gain_add](../models/ssp/signal_sine_gain_add/FIXTURE.md) |
| `signal_step_product` | Planned | [signal_step_product](../models/ssp/signal_step_product/FIXTURE.md) |
| `signal_delay_detector` | Planned | [signal_delay_detector](../models/ssp/signal_delay_detector/FIXTURE.md) |

## Recommended Priority

The custom fixture rollout should be staged.

### Priority 1

Implemented fixtures provide immediate coverage of direct propagation, fan-in,
and fan-out.

### Priority 2

Planned:

- `signal_sine_gain_add`
- `signal_step_product`

### Priority 3

Planned:

- `signal_delay_detector`

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

## Immediate Next Step

The most useful implementation path is:

1. Resolve engine-side runtime issues exposed by the new deterministic
   propagation fixtures.
2. Run `signal_step_gain`, `signal_step_add`, and `signal_fanout_gain` through
   the comparison workflow once both engines accept them.
3. Use those fixtures to define the first strict signal-propagation regression
   checks.
4. Add the Priority 2 fixtures after the initial propagation path is stable.
