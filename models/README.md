# Model Fixture Catalog

This document lists every SSP and FMU fixture in the repository. Use it to
quickly understand what models are available, what each one demonstrates,
and which backends support it.

## SSP Fixtures

The 20 SSP fixtures are organized into four architectural classes per the
[fixture hierarchy](../product-breakdown/02-architecture/architecture.md#2-fixture-hierarchy).

### Simple Reference Models

Single-FMU SSPs for basic behavioral checks and smoke testing.

| Model | Purpose | Backends | Test Level | FIXTURE.md |
|-------|---------|----------|------------|------------|
| BouncingBall | Classic bouncing-ball simulation; simple continuous dynamics | ssp4sim, OMSimulator | Smoke | [link](./ssp/BouncingBall/FIXTURE.md) |
| VanDerPol | Van der Pol oscillator; self-excited limit-cycle dynamics | ssp4sim, OMSimulator, FMPy | Smoke | [link](./ssp/VanDerPol/FIXTURE.md) |
| Dahlquist | Dahlquist test equation; numerical stability baseline | OMSimulator, FMPy | Smoke | [link](./ssp/Dahlquist/FIXTURE.md) |
| Stair | Stair-step function; discrete-time output behavior | ssp4sim, OMSimulator | Smoke | [link](./ssp/Stair/FIXTURE.md) |
| Resource | Resource consumption and memory management baseline | ssp4sim, OMSimulator, FMPy | Smoke | [link](./ssp/Resource/FIXTURE.md) |

### Deterministic Signal-Propagation Fixtures

SSPs with algebraically predictable output, including closed algebraic loops
used as loop-resolution diagnostics, suitable for cross-engine comparison.

| Model | Purpose | Expected Behavior | Backends | Test Level | FIXTURE.md |
|-------|---------|-------------------|----------|------------|------------|
| signal_step_gain | Step signal through a gain block | Output = gain × step amplitude | ssp4sim, OMSimulator, FMPy | Behavioral | [link](./ssp/signal_step_gain/FIXTURE.md) |
| signal_algebraic_loop | Single closed algebraic loop around a gain/add pair driven by a sine wave | `add = 2 * sine`, `gain = sine` | ssp4sim, OMSimulator, FMPy | Behavioral | [link](./ssp/signal_algebraic_loop/FIXTURE.md) |
| signal_nested_algebraic_loop | Nested algebraic loop inside a larger loop driven by a biased sine wave | Outer and inner loop solutions resolve simultaneously | ssp4sim, OMSimulator | Behavioral | [link](./ssp/signal_nested_algebraic_loop/FIXTURE.md) |
| signal_nested_parameter_bindings | Nested system with external root binding and inline inner binding | Root step is summed with nested sine/gain output | ssp4sim, OMSimulator | Behavioral | [link](./ssp/signal_nested_parameter_bindings/FIXTURE.md) |
| signal_step_add | Two step signals summed | Output = sum of both source signals | ssp4sim, OMSimulator, FMPy | Behavioral | [link](./ssp/signal_step_add/FIXTURE.md) |
| signal_fanout_gain | One source fanned out to two gain blocks | Both outputs = identical (same gain × same source) | ssp4sim, OMSimulator, FMPy | Behavioral | [link](./ssp/signal_fanout_gain/FIXTURE.md) |
| signal_sine_gain_add | Sine source through gain then summed with original | Output = (gain + 1) × sine | ssp4sim, OMSimulator, FMPy | Behavioral | [link](./ssp/signal_sine_gain_add/FIXTURE.md) |
| signal_step_product | Two step signals multiplied | Output = product of both source amplitudes | ssp4sim, OMSimulator, FMPy | Behavioral | [link](./ssp/signal_step_product/FIXTURE.md) |
| signal_delay_detector | Step input through a delayed connection | Output = step delayed by configured lag | ssp4sim, OMSimulator, FMPy | Behavioral | [link](./ssp/signal_delay_detector/FIXTURE.md) |
| signal_parameter_inline_with_mapping | Step with inline SSV and external SSM mapping | Output tracks step configuration | ssp4sim, OMSimulator | Behavioral | [link](./ssp/signal_parameter_inline_with_mapping/FIXTURE.md) |
| signal_nested_external_bindings | Nested system with external SSV+SSM bindings | Root step output routed to system connector | ssp4sim, OMSimulator | Behavioral | [link](./ssp/signal_nested_external_bindings/FIXTURE.md) |

### Composite SSPs

Multi-component SSPs exercising realistic coupling and scheduling.

| Model | Purpose | Backends | Test Level | FIXTURE.md |
|-------|---------|----------|------------|------------|
| dcmotor | DC motor model with electrical and mechanical subsystems | ssp4sim, OMSimulator | Regression | [link](./ssp/dcmotor/FIXTURE.md) |
| embrace | EMBRACE co-simulation benchmark; multi-FMU coupling | ssp4sim, OMSimulator, FMPy | Regression | [link](./ssp/embrace/FIXTURE.md) |

### Special-Purpose SSPs

SSPs that test specific packaging or runtime features.

| Model | Purpose | Backends | Test Level | FIXTURE.md |
|-------|---------|----------|------------|------------|
| pyfmu_csv_source_sink | CSV-backed source and sink FMUs inside an SSP | ssp4sim | Behavioral | [link](./ssp/pyfmu_csv_source_sink/FIXTURE.md) |
| scenario | SSV/SSM parameter injection and structured scenario handling | ssp4sim | Behavioral | [link](./ssp/scenario/FIXTURE.md) |

## FMU Building Blocks

Reusable signal-processing FMUs. These are the base units of the fixture
hierarchy and are referenced by SSP fixtures during the build stage.

| FMU | Source Type | Purpose |
|-----|-------------|---------|
| BouncingBall | Modelica | Continuous bouncing-ball dynamics |
| VanDerPol | Modelica | Van der Pol oscillator |
| Dahlquist | Modelica | Dahlquist test equation |
| Stair | Modelica | Stair-step function |
| Resource | Modelica | Resource consumption baseline |
| Modelica.Blocks.Sources.Sine | Modelica | Sine wave source |
| Modelica.Blocks.Sources.Step | Modelica | Step function source |
| Modelica.Blocks.Math.Gain | Modelica | Signal gain multiplier |
| Modelica.Blocks.Math.Add | Modelica | Signal summation |
| Modelica.Blocks.Math.Product | Modelica | Signal multiplication |

## Test Level Definitions

Per the [test strategy](../product-breakdown/04-verification/co_simulation_test_strategy.md):

| Level | Purpose | Passing Criteria |
|-------|---------|-----------------|
| **Smoke** | Pipeline runs without crashing | Simulation completes; CSV output produced |
| **Behavioral** | Output matches algebraic expectation | Max error within tight tolerance (deterministic fixtures) |
| **Regression** | Output matches trusted baseline | Metrics within tolerance against stored reference |

## Backend Key

| Backend | Description |
|---------|-------------|
| ssp4sim | Simulation adapter for the SSP4Sim engine |
| FMPy | Simulation adapter for the FMPy engine |
| OMSimulator | Simulation adapter for the OMSimulator engine |

---

*Last updated: when adding or removing fixtures, update this catalog and
the corresponding FIXTURE.md files.*
