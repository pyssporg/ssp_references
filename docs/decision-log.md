# Decision Log

This is the root-level index of all durable decisions in the repository.
Per KM-005, decisions are stored in the layer where their consequences are
most directly felt. This file is only an index — it does not contain decision
context, alternatives, consequences, or verification detail.

## Product Decisions

Product decisions translate repository intent into durable promises. They
live in [docs/01-product-decisions/](./01-product-decisions/).

| ID | Title | Layer | Status | Location |
| --- | --- | --- | --- | --- |
| PD-003 | Supported Simulation Backends | Product | Accepted | [01-product-decisions/PD-003-supported-backends.md](./01-product-decisions/PD-003-supported-backends.md) |
| PD-001 | Comparison Methodology — Engine-to-Engine Only | Product | Accepted | [01-product-decisions/PD-001-comparison-engine-to-engine.md](./01-product-decisions/PD-001-comparison-engine-to-engine.md) |
| PD-002 | Simulation Registry Is the Single Source of Truth | Product | Accepted | [01-product-decisions/PD-002-simulation-registry-source-of-truth.md](./01-product-decisions/PD-002-simulation-registry-source-of-truth.md) |

## Architecture Decision Records

ADRs document significant architectural choices and live in
[docs/03-technical-decisions/](./03-technical-decisions/).

| ID | Title | Layer | Status | Location |
| --- | --- | --- | --- | --- |
| ADR-001 | Three-Stage Pipeline Architecture | Architecture | Accepted | [03-technical-decisions/ADR-001.md](./03-technical-decisions/ADR-001.md) |
| ADR-002 | Fixture Hierarchy | Architecture | Accepted | [03-technical-decisions/ADR-002.md](./03-technical-decisions/ADR-002.md) |
| ADR-003 | Runtime Configuration Belongs to the Simulation Registry | Technical | Accepted | [03-technical-decisions/ADR-003.md](./03-technical-decisions/ADR-003.md) |

## Design Decisions

DDs document smaller implementation choices and live beside the ADRs in
[docs/03-technical-decisions/](./03-technical-decisions/).

| ID | Title | Layer | Status | Location |
| --- | --- | --- | --- | --- |
| DD-001 | Simulation Settings Belong to the Runtime Layer | Technical | Accepted | [03-technical-decisions/DD-001-simulation-settings-runtime-layer.md](./03-technical-decisions/DD-001-simulation-settings-runtime-layer.md) |
| DD-002 | Runtime Artifacts Stay Under `artifacts/` | Technical | Accepted | [03-technical-decisions/DD-002-runtime-artifacts-under-artifacts.md](./03-technical-decisions/DD-002-runtime-artifacts-under-artifacts.md) |
| DD-003 | `build.py` Remains Build-Only | Technical | Accepted | [03-technical-decisions/DD-003-build-py-remains-build-only.md](./03-technical-decisions/DD-003-build-py-remains-build-only.md) |
| DD-004 | Signal-Propagation Fixtures Use Deterministic Algebraic FMU Blocks | Technical | Accepted | [03-technical-decisions/DD-004-signal-propagation-deterministic-blocks.md](./03-technical-decisions/DD-004-signal-propagation-deterministic-blocks.md) |
| DD-005 | Simulation Registry Technical Mechanism | Technical | Accepted | [03-technical-decisions/DD-005-simulation-registry-technical.md](./03-technical-decisions/DD-005-simulation-registry-technical.md) |

## Maintenance Rule

When a decision file is added, renamed, superseded, or deprecated, update this
index in the same change. Keep entries short — full rationale belongs in the
decision files themselves.

## New Decision Template

Use the template at `.opencode/templates/product-breakdown/templates/decision-template.md`
for new durable decisions.