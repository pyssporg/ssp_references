# Product Decisions

This document records product-level decisions for the `ssp_references` repository.
It sits at the **Product Decisions** layer in the documentation chain, between
[docs/01-intent/intent.md](../01-intent/intent.md) (Intent and Product Commitments) and
[docs/02-architecture/architecture.md](../02-architecture/architecture.md) (System Architecture).

Each entry states the context, alternatives considered, the chosen approach,
rationale, and consequences — following the same structure as the ADR template
but at the product-decision scope.

---

### PD-001: Comparison Methodology — Engine-to-Engine Only

**Context:** The repository could compare simulation results against analytical
expectations, CSV baselines, or other engineered references. Early discussions
considered several comparison strategies.

**Options Considered:**
1. **Analytical truth comparison** — Each fixture would carry an analytical
   solution or reference CSV. Comparison would measure deviation from truth.
2. **Engine-to-engine comparison** — At least two distinct backend runs are
   required. Comparison measures pairwise deviation between backends.
3. **Hybrid** — Some fixtures use analytical truth, others use engine-to-engine.

**Decision:** Comparison is always pairwise engine-to-engine. At least two
distinct backend runs are required. Baselines stored under
`models/fmu/<model>/references/` are used as fixture reference data, not as
comparison targets in the pipeline.

**Rationale:** Engine-to-engine comparison detects behavioral differences in
the orchestration layer without requiring analytical truth for every fixture.
It keeps the comparison pipeline symmetric and avoids maintaining
engine-specific pass/fail criteria for each model. Adding analytical truth
would require per-fixture mathematical analysis that is out of scope for a curated reference collection.

**Consequences:** A single-backend run cannot be compared. Adding a new backend
requires at least one other backend run for the comparison to produce results.
Absolute correctness checks against analytical solutions are out of scope.

**Trace:** Satisfies the "Engine comparison results are the primary quality gate"
commitment in [docs/01-intent/intent.md](../01-intent/intent.md).

*This decision was migrated from design decision #2 in the
[design decisions log](../03-decisions/design-decisions-log.md).*

---

### PD-002: Simulation Registry Is the Single Source of Truth for Case/Backend Selection

**Context:** The run matrix could be derived from directory scanning of built
SSPs, from `experiments.xml` content, or from a registry file.

**Options Considered:**
1. **Directory scanning** — Walk `artifacts/models/` to discover built SSPs and
   derive the run matrix from directory structure.
2. **`experiments.xml` parsing** — Read each built SSP's `experiments.xml` to
   determine simulation cases and backends.
3. **Explicit registry file** — A single JSON file lists every model/case/backend
   combination explicitly.

**Decision:** `artifacts/simulation_registry.json` is the exclusive source of
truth for which model/case/backend combinations are active.

**Rationale:** A single explicit registry avoids hidden defaults, makes the
active test matrix visible without running any code, and allows selective
enablement/disablement of cases without modifying model sources or build
scripts.

**Consequences:** Adding a new model or case requires a registry update.
Removing a case requires only a registry change (no rebuild needed as long
as the SSP root already exists).

**Trace:** Satisfies the "build, simulate, and compare workflow is driven by
shared entry points" commitment in
[docs/01-intent/intent.md](../01-intent/intent.md). PD-002 was migrated from
design decision #6 in the design decisions log
([docs/03-decisions/design-decisions-log.md](../03-decisions/design-decisions-log.md)).

---

### PD-003: Supported Simulation Backends

**Context:** The repository needs to decide which co-simulation engines to
support as backends for the simulation and comparison pipeline.

**Options Considered:**
1. **Single backend** — Support only one engine (e.g., OMSimulator) and compare
   against stored reference trajectories.
2. **Three-backend set** — Support OMSimulator, ssp4sim, and FMPy as the initial
   backend set, enabling pairwise engine-to-engine comparison.
3. **Open-ended** — Support any backend that implements the adapter contract,
   without an explicit committed set.

**Decision:** The repository commits to supporting three backends as the initial
set: **ssp4sim**, **OMSimulator**, and **FMPy**. Additional backends may be
added later via the adapter mechanism, but the three-backend set is the
committed minimum for pairwise comparison.

**Rationale:** Three backends provide meaningful pairwise comparison coverage
(six unique pairs) while keeping the adapter maintenance burden manageable.
The set includes one primary engine (OMSimulator), one reference implementation
(ssp4sim), and one Python-based engine (FMPy) covering different execution
models.

**Consequences:** Each backend requires an adapter module, a maintained
installation, and CI coverage. Adding a fourth backend increases the pairwise
comparison count quadratically. Removing a backend reduces comparison coverage
and may require updating the committed set.

**Trace:** Satisfies the "Engine comparison results are the primary quality gate"
commitment in [docs/01-intent/intent.md](../01-intent/intent.md). The current backend set
is documented in
[docs/05-verification/co_simulation_test_strategy.md](../05-verification/co_simulation_test_strategy.md).

---

## Document Purpose

This document records product-level decisions that translate the repository's
intent (stated in [docs/01-intent/intent.md](../01-intent/intent.md)) into durable product
promises. These decisions sit between Intent and System Architecture in the
documentation chain. They are broader in scope than technical decisions (ADRs)
and more concrete than the product commitments in the intent document.

Future product-level decisions should be added here using the same structure:
Context, Options Considered, Decision, Rationale, Consequences, Trace.
