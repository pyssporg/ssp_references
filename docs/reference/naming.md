---
id: INFO-007
type: info
title: Naming Conventions
summary: Stable ID prefixes, archive record names, and citation rules.
date: 2026-10-22
status: current
pb_exempt: true
---

# Naming Conventions

- **Current state**: layer leaves carry `id`, `type`, `title`, `summary`, `date`, and `status` front-matter.
- **Citations**: cite another node by ID in backticks, never by a markdown path.
- **Decision records**: live in `docs/archive/archive.zip`, read with `pb archive read <ID>`.
- **Generated registers**: `docs/archive/README.md`, `docs/archive/design-choice-log.md`, and `docs/archive/traceability-map.md` are generated; never edit them by hand.

## Leaf ID Prefixes

- `INFO` - current-state reference leaf.
- `EVAL` - verification, review, or assessment leaf.
- `CP` - product capability or promise.
- `IMP` - evolution candidate.
- `CON` - constraint.
- `REQ` - requirement.
- `TEST` - test or verification asset.
- `RQ` - research question.
- `TR` - trace.

## Record ID Prefixes

- `PD` - product decision.
- `ADR` - architecture decision record.
- `DD` - design decision.

## Archive Record Names

Decision records use `<PREFIX>-<NNN>-<kebab-slug>.md` inside the archive:

```text
PD-001-comparison-engine-to-engine.md
PD-004-sysml-sspmodel-authoring.md
ADR-001-three-stage-pipeline.md
ADR-007-sysml-build-boundary.md
DD-007-signal-step-gain-model-export.md
DD-009-runtime-scenario-injection.md
```

## Adding a Record

1. Write the record with the skill template.
2. Run `pb archive --root docs/breakdown add <record>`.
3. The command validates, stores the record, and deletes the loose file.
4. Update the owning layer leaf in the same change so its `state:` target holds the current fact.

## Adding a Leaf

1. Run `pb new <layer-dir> "<Title>" --summary "<one-line>" --type <type>`.
2. Keep one current-state fact per line, present tense.
3. Cite other nodes by ID, not by path.
