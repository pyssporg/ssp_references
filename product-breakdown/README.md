# Product Breakdown

This directory is the documentation backbone of the `ssp_references`
repository. It organizes intent, product decisions, architecture,
implementation, verification, operation, and evolution into traceable layers.

## Layer Structure

```text
product-breakdown/
  README.md            ← you are here
  decision-log.md      — all decisions indexed by ID
  naming.md            — prefix and filename conventions
  traceability-map.md  — cross-layer trace chain

  00-intent/           — purpose, commitments, non-goals
  01-product/          — product decisions (what we promise)
  02-architecture/     — system architecture and ADRs
  03-implementation/   — build/simulation workflow guidance
  04-verification/     — test strategy and fixture mapping
  05-operation/        — operational guidance (currently empty)
  06-evolution/        — backlog, roadmap, improvement candidates
```

Each layer may contain a local `decisions/` subdirectory holding the
decision records that most directly affect that layer.

## Layer Questions

| Layer | Main Question | Entry Point |
|-------|--------------|-------------|
| `00-intent/` | Why does this repository exist? | [`00-intent/intent.md`](./00-intent/intent.md) |
| `01-product/` | What should it promise? | [`01-product/README.md`](./01-product/README.md) |
| `02-architecture/` | How is it structurally organized? | [`02-architecture/architecture.md`](./02-architecture/architecture.md) |
| `03-implementation/` | How is it built? | [`03-implementation/FIXTURE-template.md`](./03-implementation/FIXTURE-template.md) |
| `04-verification/` | How do we know it works? | [`04-verification/README.md`](./04-verification/README.md) |
| `05-operation/` | How is it run and supported? | [`05-operation/README.md`](./05-operation/README.md) |
| `06-evolution/` | How should it change over time? | [`06-evolution/README.md`](./06-evolution/README.md) |

## Cross-Cutting Indexes

| File | Purpose |
|------|---------|
| [`decision-log.md`](./decision-log.md) | Index of all PDs, ADRs, and DDs with layer, status, and location |
| [`naming.md`](./naming.md) | Stable ID prefixes and filename conventions |
| [`traceability-map.md`](./traceability-map.md) | Cross-layer trace chain from intent through verification |

## Quick Navigation

| If you want to... | Start here |
|------------------|-----------|
| Understand the repository's purpose | [`00-intent/intent.md`](./00-intent/intent.md) |
| See what the repository promises | [`01-product/README.md`](./01-product/README.md) |
| Learn the pipeline architecture | [`02-architecture/architecture.md`](./02-architecture/architecture.md) |
| Add a new model fixture | [`03-implementation/FIXTURE-template.md`](./03-implementation/FIXTURE-template.md) |
| Understand how models are tested | [`04-verification/co_simulation_test_strategy.md`](./04-verification/co_simulation_test_strategy.md) |
| See what improvements are planned | [`06-evolution/backlog/`](./06-evolution/backlog/) |

## Core Rule

A decision belongs in the layer where its consequences are most directly
felt — not in a central decisions directory. The root-level
[`decision-log.md`](./decision-log.md) is an index only; full rationale
lives in the layer-local `decisions/` subdirectories.

## Agent Usage

1. Identify the relevant layer before reading broadly.
2. Load that layer's entry point (listed above).
3. If adding a decision, place it in the layer where its consequences are felt.
4. Update local artifacts first, then update the cross-cutting indexes.
5. Keep traces backward (never link down to implementation/verification
   from higher layers).