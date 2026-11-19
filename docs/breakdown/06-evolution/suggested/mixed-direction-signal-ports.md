---
id: IMP-112
type: imp
title: Mixed-direction signal ports
summary: Carry direction per port-definition member so one signal port exposes its input and output connectors under one FMU name prefix, in pyssp_sysml2 and pyfmi_sysml2.
date: 2026-11-19
status: suggested
---

# Mixed-direction signal ports

A fluid link carries feed and return members with opposite causality under one
FMU prefix (`consumerFeed.p` in, `consumerFeed.m` out), but one port usage has
one direction, so only half of the prefix can be grouped.

## Objective And End State

A port-definition member may declare `in` or `out`; unmarked members inherit
the usage direction, so one usage yields per-member connector kinds under one
prefix.

- `inout port consumerFeed : FluidState;` with `in p/h/X[3]` and `out m/hn`
  yields mixed kinds under `consumerFeed.`.
- One connection between mixed ports expands one connection per member.
- `inout`/undirected usages with unmarked members keep the `inout -> input`
  FMI fallback; parameter interfaces stay directionless.
- Output connector names and kinds equal today's artifacts.

## Evidence

- `PortUsage.direction` carries `inout` and `None`
  (`pycps_sysml2/model/model.py:135-149`, `parser.py:295-303`).
- `PortDefinition` stores only attributes; `_port_definition` reads only
  `element.attributes` (`model.py:339-343`, `loader.py:406-417`).
- SSD export passes the usage direction to `to_fmi_direction_definition`,
  which accepts only `in` or `out` (`ssd.py:215`, `fmi_helpers.py:74-79`).
- Tested: `inout port` on a ravs_v2 copy fails with
  `[error] Direction conversion is unknown`.
- `pyfmi_sysml2` derives one causality per usage and maps `inout` to `input`
  (`interface.py:95-103`).

## Rationale

- SSD connectors are per member with their own kind, so the artifact already
  supports a mixed port; FMI 2.0 has no bidirectional scalar, so per-member
  causality is the right mapping.
- It removes the XOR per prefix that forces the other direction to stay flat.
- Fixtures need three port usages per prefix today (`ravs_v1`, `ravs_v2`).

## Owner And Blocker

`pycps_sysml2` captures member direction; `pyssp_sysml2` emits per-member
kinds; `pyfmi_sysml2` derives per-member causality; fixtures pin the result.
Blocker: the member-direction rule and its precedence over the usage
direction. Cross-repo order: `pycps_sysml2`, `pyssp_sysml2`,
`pyfmi_sysml2`, then the `ssp_references` pin.

## Traceability

- Fixtures: `models/ssp/ravs_v1`, `models/ssp/ravs_v2`; related `IMP-111`; sources `github.com/pyssporg/{pycps_sysml2,pyssp_sysml2,pyfmi_sysml2}`.
