# Naming Conventions

This document records the stable identifier prefixes and filename conventions
used in this repository. Follow these conventions when creating new artifacts.

## Active Prefixes

| Prefix | Meaning | Location |
| --- | --- | --- |
| INT | Intent | `00-intent/intent.md` |
| PD | Product Decision | `01-product/decisions/PD-*.md` |
| ADR | Architecture Decision Record | `02-architecture/decisions/ADR-*.md` |
| DD | Design Decision | `03-implementation/decisions/DD-*.md` |
| IMP | Improvement Candidate | `06-evolution/backlog/IMP-*.md` and `06-evolution/backlog/complete/IMP-*.md` |

## Filename Convention

All decision files use lowercase kebab-case after the stable ID prefix and
sequence number:

```text
PD-001-comparison-engine-to-engine.md
PD-002-simulation-registry-source-of-truth.md
PD-003-supported-backends.md
ADR-001.md
ADR-002.md
ADR-003.md
DD-001-simulation-settings-runtime-layer.md
DD-002-runtime-artifacts-under-artifacts.md
DD-003-build-py-remains-build-only.md
DD-004-signal-propagation-deterministic-blocks.md
DD-005-simulation-registry-technical.md
```

**Notes:**
- ADR files use only the prefix and number (e.g., `ADR-001.md`) — no kebab-case
  title suffix.
- PD files include a kebab-case title suffix after the sequence number.
- DD files include a kebab-case title suffix after the sequence number.
- IMP files use the prefix with either `-NNN` (completed items) or `-CAND-X`
  (proposed candidates).

## Reference Prefixes (from templates, not yet in active use)

The following prefixes are defined in the product-breakdown naming template
but are not currently used in this repository. They are reserved for future
use when the corresponding layer artifacts are created:

| Prefix | Meaning |
| --- | --- |
| OUT | Outcome |
| ASM | Assumption |
| CON | Constraint |
| CAP | Capability |
| UC | Use case |
| REQ | Requirement |
| OD | Operational Decision |
| ED | Evolution Decision |
| RISK | Risk |
| TEST | Test or verification artifact |