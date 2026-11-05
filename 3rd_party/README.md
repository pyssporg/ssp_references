# Third-Party Submodules

Three submodules are linked here. `pyssp_workflow` is the development tree for
the pyssp capability layer. `pycps_sysml2` (SysML dialect) and `pyfmi_sysml2`
(FMI artifact generation) were split out of the SysML stack and are linked at
this level, not nested under `pyssp_workflow`.

| Submodule | Upstream | Role |
| --- | --- | --- |
| `pyssp_workflow/` | `pyssporg/pyssp_workflow` | Composition layer and development tree for the pyssp capabilities |
| `pycps_sysml2/` | `pyssporg/pycps_sysml2` | SysML v2 parser, IR, variation/selection, and marker accessors; emits no artifact |
| `pyfmi_sysml2/` | `pyssporg/pyfmi_sysml2` | FMI 2.0 CoSimulation artifacts (`modelDescription.xml`, C headers, `.fmu`) from the SysML dialect |

Nested under `pyssp_workflow/3rd_party/`:

| Path | Upstream | Role |
| --- | --- | --- |
| `experimental_pyssp_standard/` | `pyssporg/experimental_pyssp_standard` | Experimental fork of `pyssporg/pyssp_standard`; SSP XML model and archive APIs used by the build stage |
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

The recursive flag is required: `pyssp_workflow` pins its own dependencies.

## Install for development

The default `requirements.txt` install takes the eight vendored distributions
from their GitHub release assets. Each wheel's metadata names its sibling
dependencies the same way, so the version graph travels inside the wheels.

`requirements-dev.txt`, `requirements-sysml.txt`, and `requirements-campaign.txt`
add the relevant checkouts as editable packages on top of that default. The
pyssp capability paths run through `3rd_party/pyssp_workflow/3rd_party/`; the
SysML dialect and FMI artifact libraries resolve through their repo-level
submodules. Editable installs are the development state, because the pinned
commits are not released versions; pip still resolves the release URLs named by
the wheel metadata.

## Pinning and updates

Each submodule is pinned by the commit recorded in this repository's gitlink.
The `pyssp_workflow` gitlink is the version record for the whole capability
tree; the two SysML/FMI gitlinks pin the released v0.1.0 libraries.

- The pyssp checkouts are clean: `pyssp_workflow`, `experimental_pyssp_standard`,
  `pyssp_simulate`, `pyssp_sysml2`, `pyssp_vv`, and `sequence_extensions`.
- The SysML stack submodules are clean at their `main` commits.
- This repository carries no patch that waits on a local working tree.
- The multi-line string handling (`\n`, `\r`, `\t` decode on read, re-escape on
  export) and the study `doc` to `study.json` `description` path are committed
  upstream in `pyssp_sysml2` and `pyssp_workflow`.
- Update order: land the change upstream, bump the capability gitlink in
  `pyssp_workflow`, then bump the `pyssp_workflow` gitlink here. The SysML
  dialect and FMI library upstreams are bumped directly in this repository.

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
git -C 3rd_party/pycps_sysml2 status --short
git -C 3rd_party/pyfmi_sysml2 status --short
```

When updating one, run the relevant tests in `ssp_references` and in the owning
repository, then record the new gitlink.

## Upstream URLs

`3rd_party/pyssp_workflow`, `3rd_party/pycps_sysml2`, and
`3rd_party/pyfmi_sysml2` use HTTPS so a fresh clone needs no SSH key. To use
SSH locally, rewrite a URL without editing `.gitmodules`:

```bash
git submodule set-url 3rd_party/pyssp_workflow git@github.com:pyssporg/pyssp_workflow.git
git submodule set-url 3rd_party/pycps_sysml2 git@github.com:pyssporg/pycps_sysml2.git
git submodule set-url 3rd_party/pyfmi_sysml2 git@github.com:pyssporg/pyfmi_sysml2.git
```
