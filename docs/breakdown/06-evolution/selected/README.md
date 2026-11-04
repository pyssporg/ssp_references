---
title: Selected IMPs
summary: Scoped improvement candidates awaiting implementation.
---

# Selected IMPs

Scoped improvement candidates awaiting implementation.

## Contents

<!-- pb:index:start -->
<!-- GENERATED FILE — do not edit. Regenerate with pb-registers. -->
- **IMP-100** [Raw Improvement Ideas](raw-ideas.md) — Unscoped improvement ideas; route each through the change pipeline.
- **IMP-101** [Scenario ownership strategy for SSP fixtures](scenario-ownership-strategy-for-ssp-fixtures.md) — One strategy selects whether a scenario parameter set is applied by the model, the analysis, or the build; pyfmu motivates the model-owned option.
- **IMP-102** [Per-reference signal selection and reference data](per-reference-signal-selection-and-reference-data.md) — Let a reference CSV name its own signals and mapping so comparisons can target a subset of parameters without changing model-level compare signals.
- **IMP-103** [Variation points from one architecture to many simulation models](variation-points-from-one-architecture-to-many-simulation-models.md) — Capture structural and parameter variation points in SysML v2 and generate one SSP per selection; ISO/IEC 26580 vocabulary, 15288 as context.
- **IMP-104** [Constraint and assert support in pyssp_sysml2](constraint-and-assert-support-in-pyssp-sysml2.md) — Carry SysML constraint and assert elements through the parser adapter and evaluate them after variation selection, so illegal variant combinations fail at build time.
- **IMP-105** [Authored variation selection and condition ownership](authored-variation-selection.md) — Each analysis declares its variant selection in SysML; the adapter resolves it and reports legal, violated, and invalid analyses, leaving build.py with only the fixture's expected partition.
- **IMP-106** [Model-level configurations for variation selection](model-level-configurations.md) — Replace the custom pyssp_selection string with a SysML v2 configuration model that specializes the composition and binds each variation usage to a variant, including nested points.
<!-- pb:index:end -->
