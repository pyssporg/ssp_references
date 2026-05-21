# Dahlquist

## Origin

Packaged from the shared `models/fmu/Dahlquist` reference FMU fixture and its
CSV baselines.

## Overview

`Dahlquist` is a simple reference SSP fixture for basic integration behavior.

## Backends

This fixture is registered for simulation with the following backends:

- OMSimulator
- FMPy

## Strategy Role

- Simple reference model.
- Behavioral comparison baseline.
- Regression anchor for numerical stability checks.

## Main Failures This Catches

- Basic integration behavior.
- Numerical stability.
- Sensitivity to solver or step-size changes.

## Typical Use

- Fast sanity checks for deterministic continuous behavior.
- Tracking unintended changes in simple exponential-like trajectories.
