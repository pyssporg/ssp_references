# Stair

## Origin

Packaged from the shared `models/fmu/Stair` reference FMU fixture and its CSV
baselines.

## Overview

`Stair` is a simple reference SSP fixture focused on stepped or event-driven
behavior.

## Backends

This fixture is registered for simulation with the following backends:

- ssp4sim
- OMSimulator

## Strategy Role

- Simple reference model.
- Smoke-test candidate.
- Behavioral comparison baseline for time events.

## Main Failures This Catches

- Time-event handling.
- Step transition timing.
- Discrete or event-driven response consistency.

## Typical Use

- Checking whether engines align on event timing and output transitions.
