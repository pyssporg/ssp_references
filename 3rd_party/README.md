# Third-Party Submodules

The `pyssp_*` libraries and `sequence_extensions` are tracked as git submodules
so the repository and its tooling can be developed together.

| Path | Upstream | Role |
| --- | --- | --- |
| `pyssp_standard/` | `git@github.com:pyssporg/pyssp_standard.git` | SSP XML model and archive APIs used by the build stage |
| `pyssp_simulate/` | `git@github.com:pyssporg/pyssp_simulate.git` | Simulation substrate used by the simulate stage |
| `pyssp_sysml2/` | `git@github.com:pyssporg/pyssp_sysml2.git` | External SysML/SSD round-trip tool |
| `sequence_extensions/` | `git@github.com:jkCXf9X4/sequence_extensions.git` | Campaign flow engine |
| `pyssp_vv/` | `git@github.com:pyssporg/pyssp_vv.git` | V&V capability: measurement policies, criteria, judgment, evidence |
| `pyssp_workflow/` | `git@github.com:pyssporg/pyssp_workflow.git` | Composable build/run/compare/verify workflows as nodes; not wired into the pipeline yet |

## Initialize

```bash
git submodule update --init --recursive
```

## Install for development

`requirements.txt`, `requirements-sysml.txt`, and `requirements-campaign.txt`
install the relevant submodules as editable packages. Do not replace those
paths with released wheels while the local patches are still required.

## Local patches

The submodule working trees may carry uncommitted changes that this repository
depends on. They are intentionally kept visible rather than committed to a
local branch that cannot be fetched by a fresh clone.

Check before updating or resetting:

```bash
git submodule status
for d in 3rd_party/pyssp_standard 3rd_party/pyssp_simulate \
        3rd_party/pyssp_sysml2 3rd_party/sequence_extensions \
        3rd_party/pyssp_vv 3rd_party/pyssp_workflow; do
  echo "=== $d"
  git -C "$d" status --short
done
```

When updating a submodule, review its local diff first, then run the relevant
tests in `ssp_references` and in the submodule before recording the new
gitlink.

## Upstream URLs

The submodule URLs use SSH. On a machine without GitHub SSH access, rewrite
them to HTTPS locally:

```bash
git submodule set-url 3rd_party/pyssp_simulate https://github.com/pyssporg/pyssp_simulate.git
```
