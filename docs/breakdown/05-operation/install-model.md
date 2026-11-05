---
id: INFO-011
type: info
title: Install model
summary: Default install is direct GitHub release wheel URLs declared in requirements.txt and in each wheel's metadata; no local mirror.
date: 2026-11-04
status: current
---

# Install model

Default install fetches the eight vendored distributions as tagged GitHub release wheel assets; development layers editable checkouts on the same default.

- **Two families:** six pyssp capability libraries (`experimental-pyssp-standard`, `pyssp-workflow`, `pyssp-simulate`, `pyssp-sysml2`, `pyssp-vv`, `sequence-extensions-flow`) plus the two SysML libraries, dialect `pycps-sysml2` and FMI artifact `pyfmi-sysml2` (`INFO-012`).
- **Default:** `requirements.txt` pins each distribution as a PEP 508 direct reference to its release wheel URL; every wheel's metadata names its siblings the same way, so the version graph travels inside the wheels.
- **Prerequisite:** every distribution carries tag `v<version>` with its wheel attached; a missing tag or renamed asset makes the dependency unresolvable.
- **Dev opt-in:** `requirements-dev.txt` composes `-r requirements.txt` and replaces the wheel installs with `-e` checkouts; resolution still follows the metadata URLs.
- **No mirror:** the repository keeps no local wheelhouse, no offline install path, and no wheel-completeness gate; each package's own CI owns that gate (`OD-003`).
- **Failure mode:** PyPI rejects direct-URL dependencies (`OD-002`), so the distributions stay unpublished there.
- **Boundary unchanged:** install mode changes package identity only; stage contracts stay as stated (`INFO-003`) and flow as stated (`INFO-008`).
