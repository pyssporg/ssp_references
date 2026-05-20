# DD-004: Signal-Propagation Fixtures Use Deterministic Algebraic FMU Blocks

**Status:** Accepted
**Layer:** technical-decision

---

## Context

Test fixtures could be built from any available FMU, including complex physical
models with nonlinear dynamics.

## Decision

Signal-propagation fixtures are assembled from small, deterministic, algebraic
FMU blocks (sources, gains, adders, products) with algebraically predictable
output.

## Rationale

These fixtures isolate engine orchestration behavior from physical-model
complexity. When a propagation test fails, the likely problem is in scheduling,
data exchange, or connector handling rather than in the model itself. The
predictable output makes cross-engine comparison straightforward with very
tight tolerances.

## Consequences

- Adds a dedicated fixture class that must be maintained separately from the
  simple reference and composite models.
- Packaging alternatives (external SSV, generated SSV, inline parameters) must
  be exercised across these fixtures to cover the parameter-passing surface.

## Trace

Satisfies the fixture hierarchy described in Section 2 of
[02-architecture/architecture.md](../../02-architecture/architecture.md) and
the fixture-class intent in
[ADR-002: Fixture Hierarchy](./ADR-002.md).

## See Also

- [ADR-002: Fixture Hierarchy](./ADR-002.md) — the architectural fixture
  classification that this decision populates.