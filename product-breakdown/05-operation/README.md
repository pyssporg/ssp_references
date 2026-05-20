# Operation Layer

This directory sits at the **Operation** layer in the documentation chain.
Per KM-005, the operation layer describes how the system is deployed,
monitored, supported, and recovered.

## Layer Purpose

The operation layer captures runnable knowledge — what to do when the pipeline
fails, how to rebuild artifacts, how to monitor simulation runs, and how to
support consumers of this repository's fixtures and results.

## Typical Artifacts

The following artifacts are possible but currently empty:

```
runbook.md             — explains how to operate and recover the system
monitoring.md          — documents metrics, alerts, and dashboards
deployment-process.md  — describes release and deployment procedures
incident-response.md   — defines incident handling and escalation steps
support-model.md       — captures support responsibilities and expectations
```

## Current State

This layer is intentionally empty. The repository is experimental and does not
yet require formal runbooks, monitoring, or incident response procedures. As
the repository matures, operation artifacts should be added here.

## Backward Trace

This operation layer sits between the Verification layer
([04-verification/](../04-verification/)) and the Evolution layer
([06-evolution/](../06-evolution/)). It serves architecture and technical
decisions in [02-architecture/](../02-architecture/) and
[02-architecture/decisions/](../02-architecture/decisions/) by defining how
those decisions are sustained in practice.

## Layer Questions

- How is the pipeline deployed and invoked?
- How are failures detected, diagnosed, and recovered?
- What monitoring or alerting exists for simulation runs?
- What operational responsibilities exist for fixture maintainers?
- How are releases or fixture updates controlled?