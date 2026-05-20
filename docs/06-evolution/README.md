# Evolution Layer

This directory sits at the **Evolution** layer in the documentation chain.
Per KM-005, the evolution layer describes how the product and system are
expected to change over time.

## Layer Purpose

The evolution layer captures deferred, scheduled, or strategic work — items
that are not implemented yet but are tracked to prevent them from being
forgotten or bundled into unrelated work.

## Typical Artifacts

```
roadmap.md   — outlines planned future work and sequencing
backlog/     — captures deferred or unscheduled work items (primary artifact)
risks.md     — records known risks, tradeoffs, and open concerns
changelog.md — summarizes notable changes over time
```

## Current State

The primary artifact is the [backlog directory](./backlog/), which contains:

- **Active candidates** (`IMP-CAND-*.md`): proposed improvement candidates
  from the continuous improvement workflow, not yet approved for implementation.
- **Complete items** (`backlog/complete/IMP-*.md`): completed improvement items
  moved here for historical reference.
- **`review-plan.md`**: the review and acceptance plan for the improvement
  backlog.

## Backward Trace

This evolution layer sits at the end of the documentation chain and serves the
entire repository by making deferred work explicit. No artifact should link
forward to evolution items — evolution items trace backward to the layer where
the pain or gap was identified.

## Layer Questions

- What is planned for the next development cycle?
- What risks or tradeoffs are known but not yet addressed?
- What changes have been made to the repository structure and workflow?
- What future capabilities or architectural changes are anticipated?