# PD-003: Supported Simulation Backends

**Status:** Accepted
**Layer:** product-decision

---

## Context

The repository needs to decide which co-simulation engines to support as
backends for the simulation and comparison pipeline.

## Options Considered

1. **Single backend** — Support only one engine (e.g., OMSimulator) and compare
   against stored reference trajectories.
2. **Three-backend set** — Support OMSimulator, ssp4sim, and FMPy as the initial
   backend set, enabling pairwise engine-to-engine comparison.
3. **Open-ended** — Support any backend that implements the adapter contract,
   without an explicit committed set.

## Decision

The repository commits to supporting three backends as the initial set:
**ssp4sim**, **OMSimulator**, and **FMPy**. Additional backends may be added
later via the adapter mechanism, but the three-backend set is the committed
minimum for pairwise comparison.

## Rationale

Three backends provide meaningful pairwise comparison coverage (six unique
pairs) while keeping the adapter maintenance burden manageable. The set includes
one primary engine (OMSimulator), one reference implementation (ssp4sim), and
one Python-based engine (FMPy) covering different execution models.

## Consequences

- Each backend requires an adapter module, a maintained installation, and CI
  coverage.
- Adding a fourth backend increases the pairwise comparison count quadratically.
- Removing a backend reduces comparison coverage and may require updating the
  committed set.

## Trace

Satisfies the "Engine comparison results are the primary quality gate"
commitment in [docs/00-intent/intent.md](../00-intent/intent.md). The current
backend set is documented in
[docs/05-verification/co_simulation_test_strategy.md](../05-verification/co_simulation_test_strategy.md).

## Sequence Note

PD-003 is the foundational product decision: the backend set constrains the
comparison methodology (PD-001) and the registry schema (PD-002). Evaluate
PD-003 first when reviewing product scope.