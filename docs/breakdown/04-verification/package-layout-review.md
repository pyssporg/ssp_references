---
id: EVAL-013
type: eval
title: Package layout review across the vendored libraries
summary: Flatness measurements for the six vendored packages, the two that were restructured into domain packages, and why the other four keep their layout.
date: 2026-10-28
status: current
---

# Package layout review across the vendored libraries

"Root" counts `.py` files directly in `src/<package>/`, excluding `__init__.py`.

| Package | Modules | LOC | Root before | Root after | Verdict |
|---|---:|---:|---:|---:|---|
| pyssp_sysml2 | 26 | 8.6k | 19 | 2 | restructured |
| pyssp_standard | 100 | 8.0k | 11 | 1 | restructured |
| pyssp_simulate | 13 | 2.3k | 7 | 7 | already segmented |
| pyssp_vv | 19 | 2.0k | 2 | 2 | already segmented |
| pyssp_workflow | 19 | 1.4k | 4 | 4 | already segmented |
| sequence_extensions | 27 | 4.9k | 1 | 1 | already segmented |

`pyssp_vv` and `sequence_extensions` already use one subpackage per concern
(`policy`/`measure`/`judge`/`evidence`; `ext`/`graph`/`flow`/`flow_runner`).
`pyssp_simulate` and `pyssp_workflow` already split their backends and
`authoring`/`study`/`nodes`; a further split moves no concept.

## pyssp_sysml2

Before: 19 of 23 modules at the root, 90 % of package LOC there, eight modules
over 400 lines; the parser adapter, dialect, and generators were indistinguishable.

```
src/pyssp_sysml2/
├── __init__.py, cli.py
├── core/        control.py paths.py fmi_helpers.py
├── model/       model.py loader.py exporter.py      (was sysml_model/)
├── parameters/  dialect.py synthesis.py variation.py
├── metadata/    fmu_metadata.py ssp_metadata.py roles.py
├── artifacts/   ssd.py ssv.py ssm.py ssp.py fmi.py study.py
└── sysml/       generate.py (was sysml.py) sync.py
```

`model` is the SysML v2 adapter, `sysml` is SysML generation and sync,
`artifacts` is SSP/FMI generation, `parameters` is the dialect and variation
resolution, `metadata` is typed metadata and role markers, `core` is constants
and helpers. `__init__` exports the same nine generators; the CLI entry point is
unchanged. Moved paths: `.ssd`/`.ssv`/`.ssm`/`.ssp`/`.fmi`/`.study` →
`.artifacts.*`, `.sysml` → `.sysml.generate`, `.sync` → `.sysml.sync`,
`.sysml_model` → `.model`; README, examples, tests, and seven docs pages moved
with them.

## pyssp_standard

Before: eleven unrelated modules at the root; the version stacks were already correct.

```
src/pyssp_standard/
├── __init__.py
├── facades/   ssp.py ssd.py ssv.py ssm.py fmu.py md.py ls_ref.py srmd.py ssb.py
├── contracts/ tree.py parameters.py
├── common/{archive,document}, common/*.py
├── standard/, tools/, schema/
```

`facades` are the entry points a consumer opens; `contracts` are the
version-neutral protocols; neither reaches into the other's internals.
`tests/tools/test_public_surface.py` now resolves `contracts/tree.py` and
`contracts/parameters.py` and still forbids them importing `standard.*`.

**Packaging defect found and fixed.** `common/`, `standard/`, and
`standard/common/` had no `__init__.py`, and `[tool.setuptools.packages.find]`
uses `find_packages`, which skips such directories. The wheel shipped two
packages and none of the `common/` or `standard/` code; editable installs hid it
because the source path was on `sys.path`. The missing files took the wheel from
2 to 30 packages (99 modules; 143 members with XSDs).

## Gates added

`tests/test_module_layout.py` in both projects, at `static` level:

| Rule | Fault it catches |
|---|---|
| root allowlist (`__init__.py`, plus `cli.py` in sysml2) | the root grows flat again |
| top-level directory allowlist | an unexplained new package |
| `__init__.py` in every directory | the wheel silently drops code |
| module size ratchet, 600 lines with reasoned exceptions | growth of the oversized modules |
| only `model/loader.py` may import `sysmlpy` | the parser leaking into generators |

Red evidence, each reverted: a stray root module, a missing `__init__.py`, a
700-line dummy module, and `import sysmlpy` outside the loader all fail.

Not done: splitting the four modules over 600 lines needs a semantic seam per
file, not a folder move; the ratchet records the debt. Splitting
`sequence_extensions/flow/` would only rename imports. Counts: pyssp_sysml2
252 → 258, pyssp_standard 467 → 473, the other four unchanged. All suites green
twice from a clean `--basetemp`; `ruff` clean; `pb check --strict` passes.
