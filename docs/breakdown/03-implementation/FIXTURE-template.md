---
id: INFO-004
type: info
title: Fixture Note Template
summary: Canonical FIXTURE.md shape for model fixtures.
date: 2026-10-22
status: current
pb_exempt: true
---

# Fixture Note Template

## Origin

<!--
Required. Describe where this fixture came from:
- For authored SSPs: directory location and key source components.
- For packaged reference models: the source FMU and any CSV baselines.
- Include provenance (upstream project, commit reference, when it was added).
-->

## Overview

<!--
Required. One-paragraph description of what this fixture is and its primary
purpose (e.g., "simple reference SSP", "deterministic signal-propagation
fixture", "composite SSP model").
-->

## Architecture Source

<!--
Required for SysML-authored fixtures.
- Path to architecture/*.sysml.
- Composition name of the exportable `SspModel`.
- Parameter interfaces and sets authored in SysML.
- Whether any legacy SSD/SSV/SSM remains checked in (and why).
-->

## Studies

<!--
Required for SysML-authored fixtures with studies.
- Study composition names (`part def ... :> Study`).
- Scenario/parameter-set names applied by each study.
- Experiment windows (`startTime`, `stopTime`, `stepSize`). Tolerance is an FMU
  property and is not part of the experiment.
- Artifact locations under artifacts/studies/<model>/<study>/.
- Confirmation that studies are not exported as SSPs.
-->

## Strategy Role

<!--
Required. How this fixture supports the test strategy:
- Fixture class (simple reference, deterministic propagation, composite).
- Which test level it targets (smoke, behavioral, regression).
- Specific risks or behaviors this fixture is designed to expose.

Keep this to 2-5 bullet points or a short paragraph.
-->

## Structure

<!--
Optional. Signal flow or component wiring diagram (text-based).
E.g., "Step -> Gain -> Add" or a short ASCII diagram showing how FMU
components connect within the SSP.
-->

## Intent

<!--
Optional. What design or validation intent this fixture addresses:
- Why it exists as a separate fixture (not covered by other models).
- Specific orchestration, packaging, or simulation scenario it targets.
-->

## Expected Behavior

<!--
Optional. What outputs this fixture should produce under correct simulation:
- Algebraic or numerical relationships between input and output signals.
- Timing expectations (e.g., "step transition occurs at the correct
  communication step, not one step later").
- Reference to expected CSV baseline if applicable.
-->

## Main Failures This Catches

<!--
Optional. Common failures or regressions this fixture is designed to detect:
- One-step propagation lag.
- Wrong parameter handling.
- Incorrect connector mapping.
- Missing signals or incorrect routing.
-->

## Simulation Notes

<!--
Optional. Notes specific to running this fixture:
- Backend-specific setup or requirements.
- Known workarounds, patches, or limitations.
-->

## Packaging Notes

<!--
Optional. Notes about how this fixture is packaged:
- Runnable SSP path: `artifacts/models/<model>/<study>/<build>/`.
- Packaging function the fixture calls after `build_fixture`.
- Generated vs checked-in SSD/SSV/SSM.
- Study scenario and experiment artifacts.
- FMU source references.
- Special build steps or resource handling.
-->

## Engine-Specific Notes

<!--
Optional. Notes about how specific backends handle this fixture differently:
- OMSimulator-specific options (--ignoreInitialUnknowns, etc.).
- FMPy-specific patches or workarounds.
- ssp4sim-specific config adjustments.
-->

## Typical Use

<!--
Recommended. Common use cases and scenarios for this fixture:
- Which test suite or validation step uses this fixture.
- How results are interpreted (e.g., "pass if step occurs in correct step
  and gain relationship holds").
-->