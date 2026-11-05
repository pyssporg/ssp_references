# Third-Party Submodule

One submodule is linked here: `pyssp_workflow`, the composition package whose
base dependencies carry the whole pyssp and SysML stack. It nests seven
checkouts — the pyssp capability libraries, the SysML dialect (`pycps_sysml2`),
and the FMI artifact library (`pyfmi_sysml2`) — and imports none of them. The
SysML libraries are base dependencies, so a plain install carries them; there is
no SysML extra.

| Submodule | Upstream | Role |
| --- | --- | --- |
| `pyssp_workflow/` | `pyssporg/pyssp_workflow` | Composition layer for the pyssp capabilities; one pin carrying the whole stack as base dependencies |

Nested under `pyssp_workflow/3rd_party/`:

| Path | Upstream | Role |
| --- | --- | --- |
| `experimental_pyssp_standard/` | `pyssporg/experimental_pyssp_standard` | Experimental fork of `pyssporg/pyssp_standard`; SSP XML model and archive APIs used by the build stage |
| `pycps_sysml2/` | `pyssporg/pycps_sysml2` | SysML v2 parser, IR, variation/selection, and marker accessors; emits no artifact |
| `pyfmi_sysml2/` | `pyssporg/pyfmi_sysml2` | FMI 2.0 CoSimulation artifacts (`modelDescription.xml`, C headers, `.fmu`) from the SysML dialect |
| `pyssp_simulate/` | `pyssporg/pyssp_simulate` | Simulation substrate used by the simulate stage |
| `pyssp_sysml2/` | `pyssporg/pyssp_sysml2` | SysML authoring, study generation, and SSD round-trip tool; an implementer of `pycps_sysml2` |
| `pyssp_vv/` | `pyssporg/pyssp_vv` | V&V capability: measurement, judgment, evidence |
| `sequence_extensions/` | `jkCXf9X4/sequence_extensions` | Campaign flow engine |

`pycps_sysml2` reads SysML and emits no artifact. `pyssp_sysml2` (SSP) and
`pyfmi_sysml2` (FMI) are siblings that both consume it; `pyfmi_sysml2` never
depends on `pyssp_sysml2`.

## Initialize

```bash
git submodule update --init --recursive
```

The recursive flag is required: `pyssp_workflow` pins all seven nested
checkouts in its own `.gitmodules`.

## Install for development

The default `requirements.txt` install takes one plain `pyssp-workflow`
reference, from its GitHub release asset; its base dependencies pin the eight
pyssp and SysML distributions. Each wheel's metadata names its sibling
dependencies the same way, so the version graph travels inside the wheels.

`requirements-dev.txt`, `requirements-sysml.txt`, and `requirements-campaign.txt`
add the relevant checkouts as editable packages on top of that default. Every
editable path runs through `3rd_party/pyssp_workflow/3rd_party/`, including the
SysML dialect and FMI artifact libraries. Editable installs are the development
state, because the pinned commits are not released versions; pip still resolves
the release URLs named by the wheel metadata.

## Pinning and updates

Each submodule is pinned by the commit recorded in its owner's gitlink. This
repository records one gitlink, `pyssp_workflow`, and that commit is the version
record for the whole tree; the seven nested checkouts are pinned inside
`pyssp_workflow`.

- The pyssp checkouts are clean: `pyssp_workflow`, `experimental_pyssp_standard`,
  `pycps_sysml2`, `pyfmi_sysml2`, `pyssp_simulate`, `pyssp_sysml2`, `pyssp_vv`,
  and `sequence_extensions`.
- The SysML stack checkouts are clean at the commits `pyssp_workflow` records.
- This repository carries no patch that waits on a local working tree.
- The multi-line string handling (`\n`, `\r`, `\t` decode on read, re-escape on
  export) and the study `doc` to `study.json` `description` path are committed
  upstream in `pyssp_sysml2` and `pyssp_workflow`.
- Update order: land the change upstream, bump that checkout's gitlink in
  `pyssp_workflow`, then bump the `pyssp_workflow` gitlink here. A SysML
  library bump is therefore one entry in `pyssp_workflow`'s `.gitmodules` plus
  one commit there.

The build and simulate stages now consume generic code from upstream
`pyssp_workflow`, `pyssp_simulate`, and `pyssp_vv`; this repository keeps
artifact layout, registry, gate policy, signal invariants, and fixture data.

`pyssp_sysml2`'s nested `3rd_party/experimental_pyssp_standard` submodule
follows the experimental fork too, so the SysML tool is developed against the
same refactored API the build stage uses. The checkout under
`pyssp_workflow/3rd_party/experimental_pyssp_standard` is the only editable
copy; the nested one is a pinned dependency and stays at the commit
`pyssp_sysml2` records.

Check before updating or resetting:

```bash
git -C 3rd_party/pyssp_workflow status --short
git -C 3rd_party/pyssp_workflow submodule foreach --recursive 'echo "=== $displaypath"; git status --short'
```

When updating one, run the relevant tests in `ssp_references` and in the owning
repository, then record the new gitlink in `pyssp_workflow` and bump the
`pyssp_workflow` gitlink here.

## Upstream URLs

`3rd_party/pyssp_workflow` and the checkouts it nests use HTTPS so a fresh
clone needs no SSH key. To use SSH locally, rewrite a URL without editing files:

```bash
git submodule set-url 3rd_party/pyssp_workflow git@github.com:pyssporg/pyssp_workflow.git
git -C 3rd_party/pyssp_workflow submodule set-url 3rd_party/pycps_sysml2 git@github.com:pyssporg/pycps_sysml2.git
git -C 3rd_party/pyssp_workflow submodule set-url 3rd_party/pyfmi_sysml2 git@github.com:pyssporg/pyfmi_sysml2.git
```

A rewrite of a nested URL lives in `pyssp_workflow/.git/config`, not in the
`ssp_references` superproject.
