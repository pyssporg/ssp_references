"""Contract: no fixture redeclares a dialect core definition.

``pycps_sysml2.core_definitions()`` ships ``SspModel``, ``Analysis``,
``FmuModel``, ``ParameterInterface``, ``ParameterSet``, ``FmuMetadata``,
``SspMetadata``, and ``Experiment``. Fixtures import them through the dialect
library; a local copy shadows the packaged definition and drifts from the roles
the library assigns to it. The system fixture additionally includes the canonical
FMU architecture instead of copying it, so the FMU definitions arrive through the
include and are not the system root's own.
"""

from __future__ import annotations

import re
from pathlib import Path

import pycps_sysml2
from pycps_sysml2.metadata import validate_role_markers
from pycps_sysml2.parameters import validate_marker_definitions

REPO_ROOT = Path(__file__).resolve().parents[1]
GAINOFFSET_ARCHITECTURE = REPO_ROOT / "models" / "ssp" / "GainOffset" / "architecture"
GAINOFFSET_FMU_ARCHITECTURE = (
    REPO_ROOT / "models" / "fmu" / "GainOffset" / "architecture"
)

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
    "FmuModel": "part def FmuModel",
    "Experiment": "attribute def Experiment",
    "ParameterInterface": "port def ParameterInterface",
    "FmuMetadata": "attribute def FmuMetadata",
    "SspMetadata": "attribute def SspMetadata",
    "ParameterSet": "attribute def ParameterSet",
}

#: Definitions the GainOffset system root receives from the canonical FMU
#: architecture include rather than declaring itself.
FMU_INCLUDED_DEFINITIONS = {
    "Generator",
    "GeneratorParameters",
    "GeneratorFmu",
    "RealSignal",
}

CORE_DEFINITION_PATTERNS = {
    name: re.compile(rf"^\s*{re.escape(prefix)}\b", re.MULTILINE)
    for name, prefix in CORE_DEFINITION_PREFIXES.items()
}


def _physical_sysml_files() -> list[Path]:
    """Every architecture source once, deduplicated by resolved path."""
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
    """Drift caught: the include path stops resolving the core or FMU definitions."""
    architecture = pycps_sysml2.load(
        GAINOFFSET_ARCHITECTURE,
        pycps_sysml2.core_definitions(),
        GAINOFFSET_FMU_ARCHITECTURE,
    )

    assert architecture.included_definitions == (
        set(CORE_DEFINITION_PREFIXES) | FMU_INCLUDED_DEFINITIONS
    )
    validate_role_markers(architecture)
    validate_marker_definitions(architecture)
