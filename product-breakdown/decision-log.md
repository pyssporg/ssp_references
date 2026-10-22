# Decision Log

This is the root-level index of all durable decisions in the repository.
Per KM-005, decisions are stored in the layer where their consequences are
most directly felt. This file is only an index — it does not contain decision
context, alternatives, consequences, or verification detail.

## Product Decisions

Product decisions translate repository intent into durable promises. They
live in [01-product/](./01-product/).

| ID | Title | Layer | Status | Location |
| --- | --- | --- | --- | --- |
| PD-003 | Supported Simulation Backends | Product | Accepted | [01-product/decisions/PD-003-supported-backends.md](./01-product/decisions/PD-003-supported-backends.md) |
| PD-001 | Comparison Methodology — Engine-to-Engine Only | Product | Accepted | [01-product/decisions/PD-001-comparison-engine-to-engine.md](./01-product/decisions/PD-001-comparison-engine-to-engine.md) |
| PD-002 | Simulation Registry Is the Single Source of Truth | Product | Accepted | [01-product/decisions/PD-002-simulation-registry-source-of-truth.md](./01-product/decisions/PD-002-simulation-registry-source-of-truth.md) |
| PD-004 | SysML `SspModel` Definitions and Parameter Sets Are the Authoring Source | Product | Accepted | [01-product/decisions/PD-004-sysml-sspmodel-authoring.md](./01-product/decisions/PD-004-sysml-sspmodel-authoring.md) |
| PD-005 | The Reference Repository Owns Fixtures and Policy Data, Not Pipeline Implementations | Product | Accepted | [01-product/decisions/PD-005-fixtures-and-policy-not-pipeline.md](./01-product/decisions/PD-005-fixtures-and-policy-not-pipeline.md) |
| PD-006 | Studies Consume Exported SSPs and Are Never Exported | Product | Accepted | [01-product/decisions/PD-006-studies-consume-exported-ssps.md](./01-product/decisions/PD-006-studies-consume-exported-ssps.md) |

## Architecture Decision Records

ADRs document significant architectural choices and live in
[02-architecture/decisions/](./02-architecture/decisions/).

| ID | Title | Layer | Status | Location |
| --- | --- | --- | --- | --- |
| ADR-001 | Three-Stage Pipeline Architecture | Architecture | Accepted | [02-architecture/decisions/ADR-001.md](./02-architecture/decisions/ADR-001.md) |
| ADR-002 | Fixture Hierarchy | Architecture | Accepted | [02-architecture/decisions/ADR-002.md](./02-architecture/decisions/ADR-002.md) |
| ADR-003 | Runtime Configuration Belongs to the Simulation Registry | Technical | Accepted | [02-architecture/decisions/ADR-003.md](./02-architecture/decisions/ADR-003.md) |
| ADR-004 | Use-Case Coverage Taxonomy as the Primary Coverage Lens | Technical | Accepted | [02-architecture/decisions/ADR-004.md](./02-architecture/decisions/ADR-004.md) |
| ADR-005 | Adopt the pyssp Ecosystem Behind Existing Stage Boundaries | Architecture | Accepted (amended 2026-10-22) | [02-architecture/decisions/ADR-005.md](./02-architecture/decisions/ADR-005.md) |
| ADR-006 | Exchange Standardized Artifacts at Tool Boundaries | Architecture | Accepted | [02-architecture/decisions/ADR-006.md](./02-architecture/decisions/ADR-006.md) |
| ADR-007 | Authoring SysML at the Build Boundary | Architecture | Accepted | [02-architecture/decisions/ADR-007.md](./02-architecture/decisions/ADR-007.md) |
| ADR-008 | Workflow Capability Ownership and Node Boundaries | Architecture | Accepted | [02-architecture/decisions/ADR-008.md](./02-architecture/decisions/ADR-008.md) |
| ADR-009 | `SspModel` and `Study` Marker Specialization | Architecture | Accepted | [02-architecture/decisions/ADR-009.md](./02-architecture/decisions/ADR-009.md) |
| ADR-010 | Runtime Scenario and Experiment Application to Exported SSPs | Architecture | Accepted | [02-architecture/decisions/ADR-010.md](./02-architecture/decisions/ADR-010.md) |

## Design Decisions

DDs document smaller implementation choices and live beside the ADRs in
[03-implementation/decisions/](./03-implementation/decisions/).

| ID | Title | Layer | Status | Location |
| --- | --- | --- | --- | --- |
| DD-001 | Simulation Settings Belong to the Runtime Layer | Technical | Accepted | [03-implementation/decisions/DD-001-simulation-settings-runtime-layer.md](./03-implementation/decisions/DD-001-simulation-settings-runtime-layer.md) |
| DD-002 | Runtime Artifacts Stay Under `artifacts/` | Technical | Accepted | [03-implementation/decisions/DD-002-runtime-artifacts-under-artifacts.md](./03-implementation/decisions/DD-002-runtime-artifacts-under-artifacts.md) |
| DD-003 | `build.py` Remains Build-Only | Technical | Accepted | [03-implementation/decisions/DD-003-build-py-remains-build-only.md](./03-implementation/decisions/DD-003-build-py-remains-build-only.md) |
| DD-004 | Signal-Propagation Fixtures Use Deterministic Algebraic FMU Blocks | Technical | Accepted | [03-implementation/decisions/DD-004-signal-propagation-deterministic-blocks.md](./03-implementation/decisions/DD-004-signal-propagation-deterministic-blocks.md) |
| DD-005 | Simulation Registry Technical Mechanism | Technical | Accepted | [03-implementation/decisions/DD-005-simulation-registry-technical.md](./03-implementation/decisions/DD-005-simulation-registry-technical.md) |
| DD-006 | Time-Shift-Tolerant VV Metrics | Technical | Accepted | [03-implementation/decisions/DD-006-time-shift-tolerant-vv-metrics.md](./03-implementation/decisions/DD-006-time-shift-tolerant-vv-metrics.md) |
| DD-007 | `signal_step_gain` Model Export | Technical | Accepted | [03-implementation/decisions/DD-007-signal-step-gain-model-export.md](./03-implementation/decisions/DD-007-signal-step-gain-model-export.md) |
| DD-008 | Study Scenario Generation and SSM Prefix Stripping | Technical | Accepted | [03-implementation/decisions/DD-008-study-scenario-generation.md](./03-implementation/decisions/DD-008-study-scenario-generation.md) |
| DD-009 | Runtime Scenario Injection and Registry Build/Case Split | Technical | Accepted | [03-implementation/decisions/DD-009-runtime-scenario-injection.md](./03-implementation/decisions/DD-009-runtime-scenario-injection.md) |

## Maintenance Rule

When a decision file is added, renamed, superseded, or deprecated, update this
index in the same change. Keep entries short — full rationale belongs in the
decision files themselves.

## New Decision Template

Use the template at `.opencode/templates/product-breakdown/templates/decision-template.md`
for new durable decisions.