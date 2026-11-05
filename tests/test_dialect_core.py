"""Contract: no fixture redeclares a dialect core definition.

``pycps_sysml2.core_definitions()`` ships ``SspModel``, ``Analysis``,
``ParameterInterface``, ``ParameterSet``, ``FmuMetadata``, ``SspMetadata``, and
``Experiment``. Fixtures import them through the dialect library; a local copy
shadows the packaged definition and drifts from the roles the library assigns
to it.
"""

from __future__ import annotations

import re
from pathlib import Path

import pycps_sysml2
from pycps_sysml2.metadata import validate_role_markers
from pycps_sysml2.parameters import validate_marker_definitions

REPO_ROOT = Path(__file__).resolve().parents[1]

#: Every authored architecture in the repository, FMU and system alike.
SYSML_GLOBS = (
    "models/ssp/*/architecture/*.sysml",
    "models/fmu/*/architecture/*.sysml",
)

#: Core definitions from ``pycps_sysml2.core_definitions()`` and the declaration
#: prefix that would reintroduce each one locally.
CORE_DEFINITION_PREFIXES = {
    "SspModel": "part def SspModel",
    "Analysis": "part def Analysis",
    "Experiment": "attribute def Experiment",
    "ParameterInterface": "port def ParameterInterface",
    "FmuMetadata": "attribute def FmuMetadata",
    "SspMetadata": "attribute def SspMetadata",
    "ParameterSet": "attribute def ParameterSet",
}

CORE_DEFINITION_PATTERNS = {
    name: re.compile(rf"^\s*{re.escape(prefix)}\b", re.MULTILINE)
    for name, prefix in CORE_DEFINITION_PREFIXES.items()
}


def _physical_sysml_files() -> list[Path]:
    """Every architecture source once, with symlinked copies resolved away."""
    return sorted(
        {
            path.resolve()
            for pattern in SYSML_GLOBS
            for path in REPO_ROOT.glob(pattern)
        }
    )


def test_no_fixture_declares_a_dialect_core_definition() -> None:
    """Drift caught: a fixture vendors a core definition the dialect owns."""
    files = _physical_sysml_files()
    assert files, "no SysML architecture files found"

    violations = [
        f"{path}: redeclares core definition {name} ({prefix!r})"
        for path in files
        for name, prefix in CORE_DEFINITION_PREFIXES.items()
        if CORE_DEFINITION_PATTERNS[name].search(path.read_text(encoding="utf-8"))
    ]
    assert violations == [], "\n".join(violations)


def test_fixture_resolves_core_markers_through_the_include_path() -> None:
    """Drift caught: the repo's core-include path stops resolving the markers."""
    architecture = pycps_sysml2.load(
        REPO_ROOT / "models" / "ssp" / "GainOffset" / "architecture",
        pycps_sysml2.core_definitions(),
    )

    assert architecture.included_definitions == set(CORE_DEFINITION_PREFIXES)
    validate_role_markers(architecture)
    validate_marker_definitions(architecture)
