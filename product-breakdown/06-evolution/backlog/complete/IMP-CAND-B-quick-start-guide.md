# IMP-CAND-B: Quick-Start Developer Onboarding Guide

## Status

Proposed

## Layer

Implementation (03) — developer experience

## Theme

Developer onboarding friction reduction

## Evidence

- README.md (root) lacks step-by-step setup sequence
- AGENTS.md references venv but doesn't document creation
- requirements.txt pins `linux_x86_64` wheels with no platform guidance
- No test command documented despite `tests/test_workflow.py` existing
- No troubleshooting section for common issues

## Current Pain Or Risk

A new developer can clone the repo but cannot run the full pipeline in under 5 minutes because: (1) no step-by-step setup sequence, (2) venv creation not documented, (3) no "first run" walkthrough that chains build → simulate → compare, (4) no test command documented, (5) no troubleshooting for platform-specific dependency issues.

## Proposed Improvement

Add a "Quick Start" section to the root README.md with: (1) `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`, (2) `python3 scripts/build_models.py run-all`, (3) `python3 scripts/run_simulations.py ...` with a specific example, (4) `python3 scripts/run_comparisons.py ...`, (5) `pytest` test command, (6) Troubleshooting subsection covering platform constraints, OMSimulator installation, FMU rebuilding.

## Expected Benefit

First-time-to-pipeline-result drops from ~15 minutes of trial-and-error to ~3 minutes of following instructions.

## Risk And Blast Radius

Low. Only the root README.md is modified. No code changes.

## Suggested Priority

High

## Task Contract Seed

Add a Quick Start section to the root README.md with: venv creation, pip install, build-all, simulate one model with one backend, compare with one other backend, run tests, and a troubleshooting table for common platform/dependency issues. Do not modify other sections.

## Out Of Scope

Modifying scripts or build files. Adding automation scripts. Restructuring the README.

## Traceability

- Intent: Repository should be reproducible and accessible to new developers
- Product: PD-003 (supported backends) — quick start should use a backend listed in PD-003
- Architecture: Pipeline stages must match `architecture.md` invariants
- Implementation: Follows the build → simulate → compare chain
- Verification: Test command references `tests/test_workflow.py`