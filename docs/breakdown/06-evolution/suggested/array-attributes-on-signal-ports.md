---
id: IMP-111
type: imp
title: Array attributes on signal ports
summary: Expand a fixed-length array attribute on a non-flat signal port to one SSD connector per element in pyssp_sysml, matching pyfmi_sysml2's FMI variable expansion and index base.
date: 2026-11-19
status: suggested
---

# Array attributes on signal ports

`pyssp_sysml` records attribute multiplicity but drops it when exporting SSD
connectors; `pyfmi_sysml2` expands the same attribute into scalar FMI
variables, so one port produces two different interfaces.

## Objective And End State

A fixed-length array attribute on a non-flat signal port becomes one connector
per element, and a connection between two such ports one connection per
element, with names both exporters agree on.

- `attribute X : Real[3];` yields `consumerFeed.X[1..3]` and three FMI
  `ScalarVariable`s; `pyssp_flat_connector` keeps one connector per port.
- `*`, `0..*`, and unequal ranges fail through `fixed_count`; scalars and
  parameter interfaces keep current behaviour.
- Parity test: SSD connector set equals FMI variable set for one port.

## Evidence

- `pycps_sysml/model/model.py:92` stores `Attribute.multiplicity`.
- `pyssp_sysml/artifacts/ssd.py:205-217` emits one connector per attribute
  and never reads multiplicity; `:400-402` promises 1-based data-port indices.
- Installed 0.5.0: `attribute X : Real[3]` emits `consumerFeed.X` only.
- `pyfmi_sysml2/interface.py:197-213,293-295` and `Field.members` (`:104-128`)
  expand to `name.X[i]` with configurable `base_index`.
- Parameters already expand (`declarations.py:115-167`, `ssv.py:72-78`).

## Rationale

- Removes the quoted `'X[1]'` workaround in `ravs_v1` and `ravs_v2`.
- FMI 2.0 has no array variable, so SSD and FMI names must match or the SSP
  cannot bind the FMU; neither exporter detects the mismatch before simulation.
- Recommendation: thread one shared `base_index` through signal expansion and
  record it in the fixture contract. Fixed 1-based ports or keeping quoted
  members are the alternatives.

## Owner And Blocker

`pyssp_sysml` owns the SSD expansion; `pyfmi_sysml2` owns the index convention
and the parity test; `pycps_sysml` needs no change. Blocker: an agreed
base-index rule. Cross-repo order: `pyssp_sysml` expansion, `pyfmi_sysml2`
parity/default, then the `ssp_references` fixture pin.

## Traceability

- Fixtures: `models/ssp/ravs_v1`, `models/ssp/ravs_v2`; related `IMP-110`.
- Sources: `github.com/pyssporg/{pyssp_sysml2,pyfmi_sysml2,pycps_sysml2}`.
