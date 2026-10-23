# Third-Party Submodules

Only one submodule is linked here: `pyssp_workflow`. It owns the development
tree for the rest of the ecosystem, so the capability checkouts live under
`3rd_party/pyssp_workflow/3rd_party/`.

| Path | Upstream | Role |
| --- | --- | --- |
| `pyssp_workflow/` | `pyssporg/pyssp_workflow` | Composition layer and development tree |

Nested under `pyssp_workflow/3rd_party/`:

| Path | Upstream | Role |
| --- | --- | --- |
| `pyssp_standard/` | `pyssporg/experimental_pyssp_standard` | SSP XML model and archive APIs used by the build stage |
| `pyssp_simulate/` | `pyssporg/pyssp_simulate` | Simulation substrate used by the simulate stage |
| `pyssp_sysml2/` | `pyssporg/pyssp_sysml2` | SysML authoring, study generation, and SSD round-trip tool |
| `pyssp_vv/` | `pyssporg/pyssp_vv` | V&V capability: measurement, judgment, evidence |
| `sequence_extensions/` | `jkCXf9X4/sequence_extensions` | Campaign flow engine |

## Initialize

```bash
git submodule update --init --recursive
```

The recursive flag is required: `pyssp_workflow` pins its own dependencies.

## Install for development

`requirements.txt`, `requirements-sysml.txt`, and `requirements-campaign.txt`
install the relevant checkouts as editable packages. The paths run through
`3rd_party/pyssp_workflow/3rd_party/`. The installs stay editable because the
pinned commits are the development state, not a released version.

## Pinning and updates

Each capability checkout is pinned by the commit recorded in its parent
repository's gitlink. The `pyssp_workflow` gitlink in this repository is the
single version record for the whole tree.

- All six checkouts are clean: `pyssp_workflow`, `pyssp_standard`,
  `pyssp_simulate`, `pyssp_sysml2`, `pyssp_vv`, and `sequence_extensions`.
- This repository carries no patch that waits on a local working tree.
- The multi-line string handling (`\n`, `\r`, `\t` decode on read, re-escape on
  export) and the study `doc` to `study.json` `description` path are committed
  upstream in `pyssp_sysml2` and `pyssp_workflow`.
- Update order: land the change upstream, bump the capability gitlink in
  `pyssp_workflow`, then bump the `pyssp_workflow` gitlink here.

The build and simulate stages now consume generic code from upstream
`pyssp_workflow`, `pyssp_simulate`, and `pyssp_vv`; this repository keeps
artifact layout, registry, gate policy, signal invariants, and fixture data.

`pyssp_sysml2`'s nested `3rd_party/pyssp_standard` submodule follows the
experimental fork too, so the SysML tool is developed against the same
refactored API the build stage uses. The checkout under
`pyssp_workflow/3rd_party/pyssp_standard` is the only editable copy; the nested
one is a pinned dependency and stays at the commit `pyssp_sysml2` records.

Check before updating or resetting:

```bash
git -C 3rd_party/pyssp_workflow status --short
git -C 3rd_party/pyssp_workflow submodule foreach --recursive 'echo "=== $displaypath"; git status --short'
```

When updating one, run the relevant tests in `ssp_references` and in the owning
repository, then record the new gitlink in `pyssp_workflow`.

## Upstream URLs

`3rd_party/pyssp_workflow` uses HTTPS so a fresh clone needs no SSH key. To use
SSH locally, rewrite the URL without editing `.gitmodules`:

```bash
git submodule set-url 3rd_party/pyssp_workflow git@github.com:pyssporg/pyssp_workflow.git
```
