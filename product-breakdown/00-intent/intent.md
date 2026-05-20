# Repository Intent

This document states the overarching purpose, commitments, and boundaries of this repository.
It sits at the top of the documentation chain as the stable north star for design decisions.

## Repository Purpose

This repository provides a curated, reproducible collection of SSP model fixtures
and the workflows to build, simulate, and compare them across co-simulation engines.
Its primary function is to validate engine behavior by running known models,
collecting simulation results, and comparing those results against trusted baselines
and cross-engine references. The repository serves as a shared reference for detecting
regressions, confirming compatibility, and diagnosing orchestration behavior — not as a
general-purpose simulation framework or a specification conformance suite.

## Product Commitments

- SSP fixtures are reproducible: each model carries a documented build contract and
  explicit provenance so that rebuilding produces an identical artifact.
- Engine comparison results are the primary quality gate: simulation output is judged
  against trusted baselines and cross-engine references, not by qualitative assessment.
- Fixture provenance is explicit: every model records its origin, authorship, and
  modification chain so that the lineage of any fixture can be traced.
- The build, simulate, and compare workflow is driven by shared entry points that
  enforce a consistent pipeline across all models.
- Result trajectories against baselines determine correctness: comparison metrics,
  not inspection or manual review, constitute the acceptance criteria.

## Non-Goals

- Validating engine correctness in an absolute or analytical sense. The repository
  detects behavioral differences and regressions relative to trusted references, but
  does not certify an engine as mathematically correct.
- Providing production-grade simulation infrastructure. The scripts are built for
  experimental validation and regression detection, not for production deployment,
  high-throughput batch simulation, or real-time execution.
- Serving as an authoritative SSP specification conformance suite. The fixtures cover
  a representative range of modeling patterns but do not exhaustively test every
  SSP 1.0 capability or edge case.

## Forward Trace

The product commitments in this document are translated into durable product
promises in the [Product Decisions](../01-product/README.md) artifact
(decisions about comparison methodology, backend support, and the simulation registry).
The stable boundaries that preserve these commitments are defined in the
[System Architecture](../02-architecture/architecture.md) document.