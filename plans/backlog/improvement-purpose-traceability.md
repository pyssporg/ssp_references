# Improvement Backlog — Purpose & Traceability

Generated from improvement workflow: intake → broad read-only discovery → architecture/requirement pressure analysis → backlog candidates → final report.

Each candidate is proposed. None is approved for implementation. Each needs a scoped task contract before any code or documentation changes begin.

---

## Individual Candidates

Each candidate is in its own file under this directory:

| File | ID | Theme | Priority | Blast Radius |
|------|----|-------|----------|-------------|
| [IMP-001.md](./IMP-001.md) | IMP-001 | Purpose/Intent Document | High | Low |
| [IMP-002.md](./IMP-002.md) | IMP-002 | System Architecture Document | High | Low |
| [IMP-003.md](./IMP-003.md) | IMP-003 | Architecture Decision Record Mechanism | Medium | Medium |
| [IMP-004.md](./IMP-004.md) | IMP-004 | FIXTURE.md Template Standardization | Medium | Low-Medium |
| [IMP-005.md](./IMP-005.md) | IMP-005 | Design Decisions Log | Medium | Low |

---

## Summary

| ID | Theme | Priority | Prerequisite | Blast Radius |
|----|-------|----------|-------------|-------------|
| IMP-001 | Purpose/Intent Document | High | None | Low |
| IMP-002 | System Architecture Document | High | IMP-001 (preferred) | Low |
| IMP-003 | Architecture Decision Record Mechanism | Medium | IMP-001, IMP-002 | Medium |
| IMP-004 | FIXTURE.md Template Standardization | Medium | None | Low-Medium |
| IMP-005 | Design Decisions Log | Medium | IMP-003 (optional) | Low |

## Cross-Cutting Note: KM-005 Preservation

All candidates respect KM-005's documentation-layer separation:
- **IMP-001** sits at the Intent and Commitments layers.
- **IMP-002** sits at the Architecture layer.
- **IMP-003** sits at the Technical Decisions layer.
- **IMP-004** sits at the Implementation layer.
- **IMP-005** bridges the Technical Decisions and Implementation layers.

No candidate mixes layers, links downward into implementation details, or adds implementation details to higher-layer documents.