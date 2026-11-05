"""Every fixture must parse as valid SysML v2 under an independent parser.

``sysmlpy 0.96.4`` is the oracle: its grammar is generated from the OMG SysML v2
2026-05 specification, so a fixture that parses and resolves here is portable
beyond this repository's own dialect parser. The ``PysspCore`` and ``ScalarValues``
libraries are the real library files, never hardcoded site-packages paths.

Two properties are gated:

* **Resolution.** Every fixture's ``architecture/*.sysml`` files load in one
  ``load_files`` call and analyze without findings, except the dialect idioms in
  ``ALLOWLIST``. A missing import is *not* visible to this analyzer: sysmlpy
  indexes library symbols as globally resolvable, so dropping ``private import
  PysspCore::*;`` still analyzes cleanly. ``UNRESOLVED_IMPORT`` only fires when
  the import target itself is absent, which catches a wrong library root.
* **Declaration.** A fixture that uses a ``PysspCore`` or ``ScalarValues``
  symbol declares the matching import in its package. This is what makes a
  deleted ``private import PysspCore::*;`` fail. The check is package-level
  because the multi-file fixtures redeclare one package, which ``load_files``
  merges into one namespace.

``IMPLICIT_LIBRARY_IMPORT`` is ignored, not allowlisted: sysmlpy emits it for
``Real`` even when ``private import ScalarValues::*;`` is present, and
``style_checks=False`` removes the naming warnings. Every other finding must be
explained by ``ALLOWLIST`` or the test fails.

Library caching hazard: ``sysmlpy.semantic.LibrarySymbolIndex`` builds one global
index per process from the first ``analyze(..., library=...)`` call, and a call
without ``library=`` poisons it for the rest of the process. Every analyze call
in this file passes ``Libraries``; keep it that way.
"""

from __future__ import annotations

import functools
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import pycps_sysml2
import pytest
import sysmlpy

REPO_ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = REPO_ROOT / "models"

CORE_LIBRARY = pycps_sysml2.core_definitions().parent
KERNEL_LIBRARY = Path(sysmlpy.__file__).resolve().parent / "library" / "kernel"
LIBRARIES = (CORE_LIBRARY, KERNEL_LIBRARY)

# ``models/ssp/GainOffset/build.py`` reaches the FMU definitions through
# ``build_fixture(includes=...)`` on the canonical FMU architecture directory
# instead of copying or linking them. The parser gate mirrors that include.
CROSS_ROOT_INPUTS: dict[str, tuple[str, ...]] = {
    "models/ssp/GainOffset": ("models/fmu/GainOffset/architecture",),
}

# sysmlpy limitation: the warning fires for ``Real`` even when the fixture
# imports ``ScalarValues::*``. The gate asserts findings, not warnings.
IGNORED_CODES = frozenset({"IMPLICIT_LIBRARY_IMPORT"})

# (fixture, code) -> (exact expected count, why the deviation is legitimate).
# One entry per dialect idiom, not one per occurrence: the count is pinned so a
# new occurrence turns the gate red instead of being absorbed.
ALLOWLIST: dict[tuple[str, str], tuple[int, str]] = {
    ("models/ssp/variation_attribute_set", "UNRESOLVED_EXPRESSION_IDENTIFIER"): (
        2,
        "selection by feature value: ``ScenarioChoice::nominalK3`` is a variant "
        "of a ``variation attribute def``; sysmlpy resolves the declaration but "
        "not the variant feature inside an attribute default expression",
    ),
    ("models/ssp/variation_conditional_excludes", "UNRESOLVED_EXPRESSION_IDENTIFIER"): (
        7,
        "selection by feature value in attribute defaults plus constraint guards: "
        "sysmlpy does not resolve variant features (``SourceChoice::sineImplementation``) "
        "or the constraint's own ``in`` parameters (``chosenSource``) in expressions",
    ),
    ("models/ssp/variation_conditional_requires", "UNRESOLVED_EXPRESSION_IDENTIFIER"): (
        3,
        "constraint guard over variation bindings: the ``in`` parameters "
        "(``chosenSource``/``chosenGain``) and the variant feature "
        "(``SourceChoice::sineImplementation``) are unresolved in the expression",
    ),
    ("models/ssp/variation_nested", "INCOMPATIBLE_FEATURE_CHAIN"): (
        1,
        "nested variant chain: ``part nestedGainPath :> PathChoice::nestedPath`` "
        "names a variant of a ``variation part def`` as a type; sysmlpy reads it "
        "as a feature chain on the enclosing system",
    ),
    ("models/ssp/variation_nested", "UNDEFINED_SYMBOL"): (
        2,
        "same nested variant chain, reported as an undefined symbol for "
        "``PathChoice::nestedPath`` and for the redefined ``inner_stage`` inside "
        "that specialized usage",
    ),
}

_IMPORT_RE = re.compile(
    r"^\s*(?:private\s+)?import\s+([A-Za-z_]\w*)\s*::\s*([A-Za-z_]\w*|\*)\s*;",
    re.MULTILINE,
)
_TOKEN_RE = re.compile(r"[A-Za-z_]\w*")
_UUID_RE = re.compile(r"^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$")


@dataclass(frozen=True)
class Observation:
    """One analyzer finding, reduced to what the gate and its report need."""

    code: str
    reference: str
    element_kind: str
    element_name: str
    owner_name: str
    message: str


def _without_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return re.sub(r"//[^\n]*", "", text)


def _declared_symbols(path: Path, pattern: str) -> frozenset[str]:
    return frozenset(re.findall(pattern, _without_comments(path.read_text(encoding="utf-8"))))


# Derived from the library files themselves: a new core definition is covered
# without editing this test.
LIBRARY_SYMBOLS: dict[str, frozenset[str]] = {
    "PysspCore": frozenset().union(
        *(
            _declared_symbols(path, r"\bdef\s+([A-Za-z_]\w*)")
            for path in sorted(CORE_LIBRARY.glob("*.sysml"))
        )
    ),
    "ScalarValues": _declared_symbols(
        KERNEL_LIBRARY / "ScalarValues.kerml", r"\bdatatype\s+([A-Za-z_]\w*)"
    ),
}

FIXTURE_DIRS: tuple[Path, ...] = tuple(
    sorted({path.parent.parent for path in MODELS_DIR.glob("**/architecture/*.sysml")})
)
FIXTURE_IDS = [path.relative_to(REPO_ROOT).as_posix() for path in FIXTURE_DIRS]


def _source_files(fixture_rel: str) -> list[Path]:
    """The fixture's own architecture files, without the cross-root include."""
    return sorted((REPO_ROOT / fixture_rel / "architecture").glob("*.sysml"))


def _inputs(fixture_rel: str) -> list[Path]:
    files = _source_files(fixture_rel)
    for include in CROSS_ROOT_INPUTS.get(fixture_rel, ()):
        files.extend(sorted((REPO_ROOT / include).glob("*.sysml")))
    return files


def _nearest_named_parent(element: object) -> str:
    """The closest named ancestor, so an anonymous usage still points home."""
    parent = getattr(element, "parent", None)
    while parent is not None:
        name = getattr(parent, "name", "") or ""
        if name and not _UUID_RE.match(name):
            return name
        parent = getattr(parent, "parent", None)
    return ""


def _observe(fixture_rel: str) -> tuple[Observation, ...]:
    model = sysmlpy.load_files(_inputs(fixture_rel))
    result = sysmlpy.analyze(model, library=LIBRARIES, style_checks=False)
    return tuple(
        Observation(
            code=issue.code,
            reference=issue.reference,
            element_kind=type(issue.element).__name__,
            element_name=getattr(issue.element, "name", "") or "",
            owner_name=_nearest_named_parent(issue.element),
            message=issue.message,
        )
        for issue in result
        if issue.code not in IGNORED_CODES
    )


# One analysis pass per process; the suite-level tests and the per-fixture test
# share it. sysmlpy issue objects carry no source position, so the report is
# resolved textually against the fixture's own files.
@functools.lru_cache(maxsize=None)
def _observed(fixture_rel: str) -> tuple[Observation, ...]:
    return _observe(fixture_rel)


def _first_line(path: Path, needle: str) -> int | None:
    pattern = re.compile(rf"\b{re.escape(needle)}\b")
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if pattern.search(line):
            return lineno
    return None


def _location(fixture_rel: str, observation: Observation) -> str:
    reference = observation.reference.rsplit("::", 1)[-1]

    # A named element locates itself. An anonymous usage (sysmlpy names it with
    # a UUID) locates its reference inside the file that declares its owner.
    if observation.element_name and not _UUID_RE.match(observation.element_name):
        needles = [observation.element_name]
    else:
        needles = [reference] if reference else []
        for path in _source_files(fixture_rel):
            owner_line = _first_line(path, observation.owner_name) if observation.owner_name else None
            if owner_line is not None and reference:
                line = _first_line(path, reference)
                if line is not None:
                    return f"{path.relative_to(REPO_ROOT).as_posix()}:{line}"

    for needle in needles:
        for path in _source_files(fixture_rel):
            line = _first_line(path, needle)
            if line is not None:
                return f"{path.relative_to(REPO_ROOT).as_posix()}:{line}"
    return f"{fixture_rel}/architecture:?"


def _report(fixture_rel: str, observations: tuple[Observation, ...]) -> str:
    lines = [f"{fixture_rel}: unexpected sysmlpy findings"]
    for observation in sorted(
        observations,
        key=lambda item: (_location(fixture_rel, item), item.code, item.message),
    ):
        lines.append(
            f"  {_location(fixture_rel, observation)}  [{observation.code}]  "
            f"{observation.element_kind} '{observation.element_name}': "
            f"{observation.message}"
        )
    return "\n".join(lines)


def _allowed_counts(fixture_rel: str) -> dict[str, int]:
    return {
        code: count
        for (fixture, code), (count, _why) in ALLOWLIST.items()
        if fixture == fixture_rel
    }


def _missing_library_imports(files: list[Path]) -> dict[str, list[str]]:
    """Library symbols used by *files* that no file imports."""
    missing: dict[str, list[str]] = {}
    for library, symbols in LIBRARY_SYMBOLS.items():
        declared: set[str] = set()
        used: set[str] = set()
        for path in files:
            text = _without_comments(path.read_text(encoding="utf-8"))
            for imported_library, member in _IMPORT_RE.findall(text):
                if imported_library == library:
                    declared.add(member)
            used.update(token for token in _TOKEN_RE.findall(text) if token in symbols)
        if "*" in declared:
            continue
        absent = sorted(used - declared)
        if absent:
            missing[library] = absent
    return missing


@pytest.mark.parametrize("fixture_rel", FIXTURE_IDS)
def test_fixture_analyzes_without_new_findings(fixture_rel: str) -> None:
    observations = _observed(fixture_rel)
    unresolved = [item for item in observations if item.code == "UNRESOLVED_IMPORT"]
    assert not unresolved, (
        f"{fixture_rel}: an import target does not exist; check the library roots "
        f"and the import name\n" + _report(fixture_rel, tuple(unresolved))
    )

    expected = _allowed_counts(fixture_rel)
    counts = Counter(item.code for item in observations)
    mismatched = {
        code: (found, expected.get(code, 0))
        for code, found in counts.items()
        if found != expected.get(code, 0)
    }
    if not mismatched:
        return
    detail = ", ".join(
        f"{code}: {found} finding(s), allowlist expects {wanted}"
        for code, (found, wanted) in sorted(mismatched.items())
    )
    raise AssertionError(_report(fixture_rel, observations) + f"\n  counts: {detail}")


@pytest.mark.parametrize("fixture_rel", FIXTURE_IDS)
def test_fixture_declares_the_library_imports_it_uses(fixture_rel: str) -> None:
    missing = _missing_library_imports(_inputs(fixture_rel))
    assert not missing, "\n".join(
        f"{fixture_rel}: uses {library} symbols {symbols} but no file declares "
        f"'private import {library}::*;' (or an explicit member import)"
        for library, symbols in sorted(missing.items())
    )


def test_missing_import_is_red(tmp_path: Path) -> None:
    """The declaration check, not the analyzer, catches a deleted import."""
    source = REPO_ROOT / "models/fmu/GainOffset/architecture/GainOffset.sysml"
    stripped = re.sub(
        r"^\s*private import PysspCore::\*;[ \t]*\n",
        "",
        source.read_text(encoding="utf-8"),
        flags=re.MULTILINE,
    )
    assert "PysspCore" not in stripped
    copy = tmp_path / source.name
    copy.write_text(stripped, encoding="utf-8")

    missing = _missing_library_imports([copy])

    assert "PysspCore" in missing
    assert "FmuModel" in missing["PysspCore"]


def test_cross_root_include_resolves_generator() -> None:
    """``Generator`` lives in the FMU root; the include removes the finding."""
    fixture_rel = "models/ssp/GainOffset"
    alone = sysmlpy.analyze(
        sysmlpy.load_files(_source_files(fixture_rel)),
        library=LIBRARIES,
        style_checks=False,
    )
    assert [(issue.code, issue.reference) for issue in alone.errors] == [
        ("UNDEFINED_SYMBOL", "Generator")
    ]

    assert [item for item in _observed(fixture_rel) if item.code == "UNDEFINED_SYMBOL"] == []


def test_allowlist_has_no_stale_entries() -> None:
    live = {
        (fixture_rel, observation.code)
        for fixture_rel in FIXTURE_IDS
        for observation in _observed(fixture_rel)
    }
    stale = sorted(set(ALLOWLIST) - live)
    assert not stale, "allowlist entries that no longer match a finding: " + ", ".join(
        f"{fixture} / {code}" for fixture, code in stale
    )
