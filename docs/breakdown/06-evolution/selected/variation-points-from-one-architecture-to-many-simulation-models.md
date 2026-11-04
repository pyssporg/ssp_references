---
id: IMP-103
type: imp
title: Variation points from one architecture to many simulation models
summary: Capture structural and parameter variation points in SysML v2 and generate one SSP per selection; ISO/IEC 26580 vocabulary, 15288 as context.
date: 2026-10-27
status: current
---

# Variation points from one architecture to many simulation models

SysML 2.0 defines `variation`, `variant`, and `VariantMembership` as choice-of-one over enumerated alternatives.
The pinned toolchain parses that syntax and discards the marker and its variants.
A build exports one model per architecture, whatever variation the architecture declares.
Parameter variation uses a separate mechanism: an SSV set bound through an SSM.
ISO/IEC/IEEE 15288 supplies life-cycle and architecture process context; it defines no variation vocabulary.
Worked SysML shapes for each route, parsed with the pinned toolchain: `examples/variation-points/`.

## Evidence

- **SysML 2.0**: variation at §7.6.7 and `VariantMembership` at §8.3.6.2; the section cites 26580, not 15288.
- **15288**: no variation-point or variant term; 2023 adds key concept 5.2.5 product line engineering only. Clauses 5.2.5, 6.4.4, 6.4.5 paywalled, unquoted here.
- **26550 §3.29 / 26580 §3.20**: variation point represents variable product-line characteristics; 26580 maps a feature selection to asset content.
- **Vocabulary absent**: no adapter support and no repository hits for variation point, product line, or feature model.
- **Probe**: a `variation part` block loads with no errors; the part survives as an ordinary usage carrying only name, type, and doc.
- **Generator scope**: the adapter reads no usage prefix; `build_ssd` takes no selection argument; `--composition` is the only selector.
- **Unused enumerator**: `exportable_part_definitions` lists exportable compositions and has no caller.
- **Build scope**: `build_fixture` passes one fixed composition to every analysis; only VanDerPol emits several, differing by the `mu` binding.
- **Registry addressing**: a case maps to an analysis name and build name; no variant identifier exists.
- **SSP packaging**: SSP 2.0 permits extra root SSD entries beside `SystemStructure.ssd`; the writer emits exactly one.

## Current Pain Or Risk

- Declared variation is silently flattened; the build succeeds, drops alternatives, and still claims provenance.
- Structural and parameter variation have different mechanisms and no shared identity.
- SysML variation expresses enumerated alternatives only, so a parameter variant stays an SSV set.
- Registry, artifact layout, and comparison naming carry no variant identity; variant packaging would re-shape them.
- The parser pin decides what survives, so adapter scope depends on a vendored dependency.

## Options

- **A. One SSP per selection**: the baseline.
  - Each variant becomes its own package and registry case; matches the current layout and unit-under-test rule.
  - Needs a naming rule for selection identity; package count grows with the variant count.
- **B. One SSP with several root SSDs**: standard-sanctioned packaging.
  - One package holds the default plus each variant SSD.
  - Needs a runtime selector and a registry field; tools without variant support run the default silently.
- **C. Parameter variation only**: SSV and SSM sets over one structure.
  - No dialect change and no new selector; cannot express a swapped component or topology.
- **D. External variation matrix**: a variant list in the build script.
  - No SysML change; variation leaves the architecture, which defeats the single-source goal.

## Decision Criteria

- Structural and parameter variation share one selection identity.
- One authored source per variation point; same selection yields the same SSP and provenance.
- Unresolved variation fails loudly; no silent default.
- The built artifact stays the unit under test; only SSP, SSD, SSV, SSM, or CSV cross.
- Smallest cross-repo change that satisfies the list; no framework growth.

## Proposed Improvement

1. Inventory variation across all fixtures; classify each as structural or parameter.
2. Decide how the adapter preserves `isVariation` and variant members.
3. Define selection identity and its path into build, registry, and comparison.
4. Fix behaviour for unresolved variation: hard error or explicit default.
5. Spike option A on one fixture; record the selection as a decision before implementing.

## Expected Benefit

- One vocabulary: 26580 terms, SysML 2.0 constructs, SSP packaging.
- Declared variation reaches the artifact or fails at build time.
- One selection name addresses both variation kinds; the gate covers every generated model.

## Risk And Blast Radius

- **Cross-repo**: `pyssp_sysml2` adapter, model, generator, CLI, tests; `pyssp_workflow.authoring` build loop and naming.
- **Repo**: registry schema, artifact layout, `FIXTURE.md` template, spike fixtures.
- **Dependency**: the pinned `sysmlpy` release decides whether variant members survive parsing.
- **Methodology**: 15288 alignment claims invite process-conformance scope; hold it as context.
- **Framework drift**: selection stays at build time; no runtime variant switch.
- **Reproducibility**: every variant needs its own build contract entry and provenance record.

## Open Questions

- Does the adapter change land upstream only, or may a local probe precede it?
- Where does selection live, and does a parameter variant reuse the variation construct?
- Which fixture proves the path first: VanDerPol for parameters, or a structural one?
- Does each variant need its own baseline and gate, and how many packages before the layout breaks?

## Owns

- The variation-point vocabulary, capture strategy, and selection identity for one architecture to many models.

## Excludes

- The adapter and generator implementation; an upstream `pyssp_sysml2` task.
- Per-fixture migration; multi-SSD packaging stays unselected.
- Comparison methodology and build pipeline; see `CP-001`, `INFO-002`, and `INFO-008`.
