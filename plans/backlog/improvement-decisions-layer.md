# Improvement Backlog — Decisions Layer Separation (KM-005)

Generated from critical review of `docs/03-technical-decisions/` against KM-005 documentation layer separation.

Each candidate is proposed. None is approved for implementation. Each needs a scoped task contract before any code or documentation changes begin.

---

## Individual Candidates

Each candidate is in its own file under this directory:

| File | ID | File | ID | Theme | Priority | Blast Radius | Status |
|---|------|----|-------|----------|-------------|--------|
| 1 | [IMP-006.md](./IMP-006.md) | IMP-006 | Product Decisions Layer | High | Low-Medium | proposed |
| 2 | [IMP-007.md](./IMP-007.md) | IMP-007 | ADR Template and Layer Boundary Clarification | High | Low | proposed |
| 3 | [IMP-008.md](./IMP-008.md) | IMP-008 | Verification Documentation Layer | Medium | Low | proposed |

---

## Summary

| ID | Theme | Priority | Prerequisite | Blast Radius | Status |
|----|-------|----------|-------------|-------------|--------|
| IMP-006 | Product Decisions Layer | High | None | Low-Medium | proposed |
| IMP-007 | ADR Template and Layer Boundary Clarification | High | None | Low | proposed |
| IMP-008 | Verification Documentation Layer | Medium | None | Low | proposed |

---

## Cross-Cutting Note: KM-005 Layer Mapping

All candidates respect KM-005's documentation-layer separation:

- **IMP-006** sits at the Product Decisions layer — fills the gap between Intent and System Architecture.
- **IMP-007** sits at the Technical Decisions layer — fixes the tooling and conventions for recording decisions.
- **IMP-008** sits at the Verification layer — moves verification artifacts out of Implementation.

Together they complete the KM-005 chain:

```
Intent → Product Decisions → System Architecture → Technical Decisions → Implementation → Verification
         ↑                      ↑                      ↑                ↑
     (IMP-006 fills     (IMP-007 clarifies     (unchanged)     (IMP-008 populates
      Product Decisions  layer boundaries                       Verification layer
      between Intent     and fixes template)                    with existing docs)
      and Architecture)
```

No candidate mixes layers, links downward into implementation details, or adds implementation details to higher-layer documents.

---

## Origin

These candidates were generated from a critical review of `docs/03-technical-decisions/` against KM-005. The review identified 6 findings; these 3 candidates address the actionable subset. Findings not addressed by these candidates (e.g., ADR-001/002 content duplication with architecture.md) are either absorbed into IMP-007's scope or deferred as lower-priority follow-ups.

See the review output for full finding details.
