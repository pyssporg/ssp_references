---
id: IMP-106
type: imp
title: Model-level configurations for variation selection
summary: Replace the custom pyssp_selection string with a SysML v2 configuration model that specializes the composition and binds each variation usage to a variant, including nested points.
date: 2026-10-30
status: current
---

# Model-level configurations for variation selection

SysML v2 defines variation points and variants but no selection construct.
The standard idiom is a 100% configuration: specialize the family and bind each variation usage with a redefinition and a feature value.
`pyssp_selection` stands in for that idiom with a custom string.
This IMP evaluates replacing it with a model-level configuration, and scopes the nested-selection problem.

## Evidence

- SysML v2.0 Language §7.6.7 defines `variation` and `variant`; §8.3.6.5 defines `VariantMembership`. Neither carries a selection or default attribute.
- §7.6.1 says a configuration is selected by selecting a variant for each variation, gives no notation, and delegates the job to external variability tooling.
- The official `VehicleVariabilityModel.sysml` example uses `part :>> engine = engine::'4cylEngine';` in a 100% model.
- Probe: `part :>> source = SourceChoice::step;` loads, but the adapter records an anonymous part usage with `type_name=None`; the redefinition target and feature value are lost.
- Probe: `part nestedGainPath :> PathChoice::nestedPath { part :>> inner_stage = StageChoice::gainStage; }` loads, but the specialization target and body are lost.
- Probe: `attribute :>> scenario = ScenarioChoice::nominalK3;` keeps the value string but loses the redefinition target.
- `PartUsage` has no `redefines` or value field; `Attribute` has `value` but no `redefines`. Recovery needs new model fields and raw-tree capture, as variation already does.
- The current string is documented as a proposal in `examples/variation-points/07_selection_configuration.sysml` and IMP-105.

## Current Pain Or Risk

- The selection encoding is custom and stringly typed; a typo is a build error, not a model error.
- The string can express an inner selection without the outer one, which the resolver must catch.
- A model-level configuration makes the dependency structural: the inner point is reachable only through the selected outer variant.
- Migration touches the adapter model, parser, selection resolver, fixtures, and provenance.

## Options

- **A. Keep `pyssp_selection`.** No change; least standard.
- **B1. Configuration model, derive the map.** Author a configuration part def; the adapter derives the canonical selection map and generation stays on `System`. Recommended.
- **B2. Configuration model, generate the configuration.** Generate the specialized composition directly; no selection map at runtime. Stronger alignment, larger blast radius.
- **C. Typed selection element.** Replace the string with a `selection` part or attribute record. Still custom.

## Proposed Improvement

1. Add `redefines` to `PartUsage` and `Attribute`, and a feature value to `PartUsage`. Done.
2. Capture redefinitions, feature values, and variant-usage bodies in `parser.py`, with raw-tree fallback. Done.
3. Add a configuration resolver: find the analysis's `sut` type, walk redefinitions to declared variants, recurse into specialized variant usages, and return the canonical map. Done.
4. Reuse `resolve_selected`, constraints, and `build_fixture`; add `configuration` to `selection.json`. Done.
5. Migrate `variation_nested` first, then the remaining fixtures. Done; all six are migrated.

The benefit is a standard configuration model, structurally ordered nested selection, and provenance that names the configuration and the derived variants.

## Examples

Simple structural configuration (experiment and binds elided):

```sysml
part def StepSystem :> System {
  part :>> source = SourceChoice::step;
}
```

Nested configuration (the hard case):

```sysml
part def NestedGainSystem :> System {
  part nestedGainPath :> PathChoice::nestedPath {
    part :>> inner_stage = StageChoice::gainStage;
  }
  part :>> path = nestedGainPath;
}
```

Derived map: `{"path": "nestedPath", "path.inner_stage": "gainStage"}`.
The outer binding is the feature value of `path`; the inner binding is a redefinition inherited from the specialized variant usage.
A flat `path.inner_stage` value on the original `path` is not valid, because the inner point exists only after the outer variant is selected.

Full examples: `examples/model-configurations/`.

## Risk And Blast Radius

- Cross-repo: `pyssp_sysml2` model, parser, selection, fixtures; `pyssp_workflow` if the build input changes.
- Parser pin: the probe shows `sysmlpy` drops redefinition targets and variant-usage bodies; raw-tree recovery is mandatory.
- Semantics: variant-usage specialization is standard, but the adapter must map a specialized usage back to its declared variant.
- Artifact identity: B1 keeps `System`; B2 changes composition names, registry cases, and selection provenance.
- Migration: one fixture first; do not change all six before the nested shape works.

## Open Questions

- Is `part nestedGainPath :> PathChoice::nestedPath { ... }` the intended standard shape, or is a separate configuration package preferred?
- Does a configuration need to bind every point, or may an unbound point inherit a declared default? SysML has no variant default.
- How should `selection.json` name the configuration without breaking consumers?

## Owns

- The model-level configuration shape and its adapter derivation.

## Excludes

- The current `pyssp_selection` implementation; see IMP-105.
- Variation resolution and constraint semantics; see IMP-103 and IMP-104.
