---
id: EVAL-014
type: eval
title: SysML standard parser gate
summary: An independent standards-derived parser must accept every authored fixture.
date: 2026-11-05
status: current
---

# SysML standard parser gate

`tests/test_sysml_standard.py` loads every authored fixture's `architecture/*.sysml`
files in one `sysmlpy.load_files` call and runs
`sysmlpy.analyze(..., library=[PysspCore, ScalarValues])`. `sysmlpy` 0.96.4 generates
its grammar from the OMG SysML v2 2026-05 specification, so a fixture that parses and
resolves there is portable beyond this repository's own dialect parser. The gate proves
portability, not engine correctness. It asserts zero analyzer errors, not zero warnings:
`IMPLICIT_LIBRARY_IMPORT` fires for `Real` even with `private import ScalarValues::*;`,
and `style_checks=False` removes naming warnings.

Scope: 29 fixtures and 93 `.sysml` files carry an `architecture/` directory. The 12
prepared Modelica fixtures under `models/fmu/` hold only an `fmu/` body and author no
SysML; they are outside this gate. `models/ssp/GainOffset` reaches `Generator` through
the FMU root, so the gate mirrors `build_fixture(includes=...)` and adds
`models/fmu/GainOffset/architecture` as a second `load_files` input. Alone the SSP root
reports `UNDEFINED_SYMBOL` for `Generator`; with the include it reports nothing. The
include is the fix and no allowlist entry covers that split.

`sysmlpy` resolves library symbols globally: dropping `private import PysspCore::*;`
still analyzes cleanly and only the warning changes. The gate therefore also checks that
a fixture using a `PysspCore` or `ScalarValues` symbol declares the matching import; a
deleted import fails that check even though the analyzer stays silent. The check is
package-level because multi-file fixtures redeclare one package that `load_files`
merges into one namespace. The allowlist is keyed by fixture and code and pins an exact
count: a new code, a new fixture, or one extra occurrence turns the gate red instead of
being absorbed. Every entry names the dialect limitation behind it.

| Fixture | Code | Count | Limitation |
| --- | --- | --- | --- |
| `variation_attribute_set` | `UNRESOLVED_EXPRESSION_IDENTIFIER` | 2 | variant feature inside an attribute default expression |
| `variation_conditional_excludes` | `UNRESOLVED_EXPRESSION_IDENTIFIER` | 7 | variant features and constraint `in` parameters in guards |
| `variation_conditional_requires` | `UNRESOLVED_EXPRESSION_IDENTIFIER` | 3 | constraint guard over variation bindings |
| `variation_nested` | `INCOMPATIBLE_FEATURE_CHAIN` | 1 | variant of a `variation part def` used as a type |
| `variation_nested` | `UNDEFINED_SYMBOL` | 2 | the same nested variant chain and its redefined `inner_stage` |

An unexpected finding reports the fixture, the resolved `file:line`, the code, the
element kind and name, and the analyzer message; a count mismatch also reports found
against expected per code. The analyzer attaches no source position, so the location is
resolved textually against the fixture's own files; an anonymous usage named by a UUID
is located through its nearest named ancestor. `sysmlpy.semantic.LibrarySymbolIndex`
caches one index per process from the first `analyze(..., library=...)` call. A call
without `library=` poisons the cache for the rest of the process. Every analyze call in
the gate passes both roots; keep it that way when adding a call.
