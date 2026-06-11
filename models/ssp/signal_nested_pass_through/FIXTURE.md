# signal_nested_pass_through

## Origin

Assembled from the shared `models/fmu/Modelica.Blocks.Sources.Step`,
`models/fmu/Modelica.Blocks.Math.Add`, and
`models/fmu/Modelica.Blocks.Math.Gain` fixtures.

All parameter bindings are inline (checked into the SSD); no external SSV or
SSM files are required.

## Overview

`signal_nested_pass_through` is a nested SSP fixture that validates signal
propagation through a nested system boundary using a Step → Gain → Add chain.
The Step component drives a Gain inside a nested subsystem, whose output feeds
an Add component at the root level. All parameters are set inline to isolate
signal routing from parameter resolution concerns.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- OMSimulator

## Strategy Role

- Nested composite SSP fixture with pure inline parameter bindings.
- Gap coverage for signal pass-through (input → process → output) across a
  nested system boundary.
- Pattern C (checked-in `SystemStructure.ssd`).

## Structure

```
Root system "system"
├── Component "step"  (Step.fmu, inline param: height=1.0, offset=0.0, startTime=0.0)
├── Component "add"   (Add.fmu,  inline param: k1=1.0, k2=1.0)
├── System "inner"
│   ├── Connector: "in"  (input)
│   ├── Connector: "out" (output)
│   └── Component "gain" (Gain.fmu, inline param: k=1.0)
│       Connection: in → gain.u
│       Connection: gain.y → out
└── Connections:
    step.y → inner.in
    inner.out → add.u1
    add.y → system.y
```

## Intent

- Validate that a signal correctly enters a nested system via an input
  connector, propagates through an internal component, and exits via an output
  connector.
- Ensure that inline parameter bindings inside a nested system resolve
  correctly alongside root-level inline bindings.
- Serve as a minimal pass-through baseline before introducing scaling
  (non-unity gain) or external bindings.

## Expected Behavior

- `step.y` jumps from 0.0 to 1.0 at t=0.0 (startTime=0.0, height=1.0,
  offset=0.0).
- `gain.y` = k × gain.u = 1.0 × step.y = step.y.
- `add.y` = k1 × u1 + k2 × u2 = 1.0 × inner.out + 1.0 × 0.0 = step.y.
- Root output `system.y` = add.y = step.y.

## Main Failures This Catches

- Signal not entering a nested system (input connector miswired).
- Signal not exiting a nested system (output connector miswired).
- Incorrect connection routing when both input and output connectors exist on
  the same nested system.
- Missing inline parameter binding inside a nested scope.
- Component parameter binding conflicting with system-level defaults.

## Packaging Notes

- The `SystemStructure.ssd` is checked in (Pattern C).
- All parameter bindings are inline `<ssd:ParameterValues>` — no external SSV
  or SSM files.
- The FMUs are shared Modelica-generated resources packaged during the build
  step.
- No stimuli or reference CSVs are required (deterministic signal propagation).

## Typical Use

- Integration testing for nested system signal pass-through.
- Cross-engine comparison of basic nested system signal routing.
- Baseline for more complex nested fixtures with non-unity gain or feedback.
