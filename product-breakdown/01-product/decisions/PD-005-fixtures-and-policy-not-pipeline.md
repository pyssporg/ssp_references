# PD-005: The Reference Repository Owns Fixtures and Policy Data, Not Pipeline Implementations

**Status:** Accepted
**Layer:** product-decision

---

## Context

`ssp_references` currently carries roughly 3,000 lines of pipeline code in
`scripts/workflow/` and `scripts/utils/`: simulation dispatch, runtime SSP
handling, result normalization, comparison metrics, gating, reference
comparison, plotting, layout, manifests, and campaign orchestration. Much of
that duplicates capabilities that now live in sibling repositories:

- `pyssp_standard` — SSP assembly and XML model APIs.
- `pyssp_simulate` — simulation execution and runtime SSP preparation.
- `pyssp_vv` — measurement, judgment, policy, and evidence.
- `pyssp_sysml2` — SysML authoring and SSD/SSV/SSM/SSP derivation.
- `sequence_extensions` — flow nodes, retries, timeouts, and parallelism.
- `pyssp_workflow` — composition of the above into build/run/compare/verify
  flows.

Continuing to maintain local equivalents keeps the fixture repository tied to
one implementation and hides upstream gaps behind private code.

## Options Considered

1. **Keep the local pipeline** — Preserve the current code and treat the
   sibling repositories as optional references.
2. **Move all generic behavior into `pyssp_workflow` and the capability
   repositories** — Keep only fixture sources, registry policy, and documented
   engine shims locally.
3. **Replace everything with upstream code at once** — Remove local stage
   contracts and artifacts immediately.

## Decision

Option 2, staged.

- `pyssp_workflow` owns generic composition: build, simulate, measure, judge,
  evidence, and report nodes plus their plain functions.
- `pyssp_standard`, `pyssp_simulate`, `pyssp_vv`, and `pyssp_sysml2` own the
  domain algorithms and artifact formats.
- `ssp_references` keeps:
  - fixture definitions and SysML model/study sources;
  - `artifacts/simulation_registry.json` policy data;
  - documented engine-gap shims that cannot yet move upstream;
  - thin command-line entry points that select registry data and submit nodes.
- Builds and simulations are submitted as `sequence_extensions` nodes so models,
  studies, and backends can run in parallel.
- No measurement, judgment, or verdict logic remains in `ssp_references` beyond
  the policy values stored in the registry.

## Rationale

The repository's value is the curated fixture corpus and the V&V evidence it
produces, not a private simulation framework. A single generic workflow layer
also makes upstream gaps visible and testable in the capability repository that
owns them.

## Consequences

- The custom comparison, gate, reference, and simulation layers are replaced by
  `pyssp_vv` / `pyssp_simulate` calls over time.
- `pyssp_vv` introduces an `invalid` verdict in addition to `pass` and `fail`.
  Campaign exit codes and manifests must distinguish "not fit to judge" from
  "failed".
- Model-specific signal invariants become registry or SysML data, not hard-coded
  Python.
- Engine shims remain local only while an upstream gap is open, and must
  reference the gap explicitly.
- The migration is sequenced in
  [ADR-008](../../02-architecture/decisions/ADR-008.md); it does not change the
  Build → Simulate → Compare stage contract.

## Trace

Satisfies the "not a general-purpose simulation framework" boundary in
[00-intent/intent.md](../../00-intent/intent.md). Refines
[ADR-005](../../02-architecture/decisions/ADR-005.md) and
[ADR-006](../../02-architecture/decisions/ADR-006.md); ownership details are in
[ADR-008](../../02-architecture/decisions/ADR-008.md).
