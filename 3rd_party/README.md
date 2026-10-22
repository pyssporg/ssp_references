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
`3rd_party/pyssp_workflow/3rd_party/`. Do not replace them with released wheels
while the local patches are still required.

## Local patches

The submodule working trees may carry uncommitted changes that this repository
depends on. Keeping them visible is deliberate.

One patch is deliberate and long-lived: `pyssp_sysml2`'s nested
`3rd_party/pyssp_standard` submodule points at the experimental fork and checks
out its refactored revision, so the SysML tool sees the same library the build
stage uses. It is a working-tree change because the URL line belongs to
`pyssp_sysml2`, whose own upstream pin is still the release line.

Check before updating or resetting:

```bash
git -C 3rd_party/pyssp_workflow status --short
git -C 3rd_party/pyssp_workflow submodule foreach --recursive 'echo "=== $displaypath"; git status --short'
```

When updating one, review its local diff first, then run the relevant tests in
`ssp_references` and in the owning repository before recording the new gitlink
in `pyssp_workflow`.

## Upstream URLs

`3rd_party/pyssp_workflow` uses HTTPS so a fresh clone needs no SSH key. To use
SSH locally, rewrite the URL without editing `.gitmodules`:

```bash
git submodule set-url 3rd_party/pyssp_workflow git@github.com:pyssporg/pyssp_workflow.git
```
