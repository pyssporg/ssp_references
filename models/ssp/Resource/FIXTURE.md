# Resource

## Origin

Packaged from the shared `models/fmu/Resource` reference FMU fixture.

## Overview

`Resource` is a simple reference SSP fixture used to validate FMU resource
handling inside an SSP.

## Strategy Role

- Simple reference model.
- Packaging and runtime integration check.

## Main Failures This Catches

- FMU resource loading.
- Packaged SSP resource resolution.
- Runtime failures caused by missing bundled files.

## Typical Use

- Verifying that engines can execute resource-dependent FMUs after SSP
  packaging.
