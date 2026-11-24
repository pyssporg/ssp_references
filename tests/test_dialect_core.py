"""Contract: no fixture redeclares a dialect core definition.

``pycps_sysml.core_definitions()`` ships the core role vocabulary. Fixtures
import it through the dialect library; a local copy shadows the packaged
definition and drifts from the roles the library assigns to it. The system
fixture additionally includes the canonical FMU architecture instead of copying
it, so the FMU definitions arrive through the include and are not the system
root's own. Definition storage is package scoped: the core lives in its own
package, so its included keys are ``<core package>::<name>``, while the FMU
architecture shares the system's package and its definitions stay bare.
"""

from __future__ import annotations

import re
from pathlib import Path

import pycps_sysml
from pycps_sysml.metadata import is_fmu_model, is_ssp_model, validate_role_markers
from pycps_sysml.parameters import validate_marker_definitions

REPO_ROOT = Path(__file__).resolve().parents[1]
GAINOFFSET_ARCHITECTURE = REPO_ROOT / "models" / "ssp" / "GainOffset" / "architecture"
GAINOFFSET_FMU_ARCHITECTURE = (
    REPO_ROOT / "models" / "fmu" / "GainOffset" / "architecture"
)

#: Every authored architecture in the repository, FMU and system alike.
SYSML_GLOBS = (
    "models/ssp/*/architecture/*.sysml",
    "models/fmu/*/architecture/*.sysml",
    "examples/*/architecture/*.sysml",
)


def _core_definition_prefixes() -> dict[str, str]:
    """Every definition the packaged core declares, and its declaration prefix.

    Derived from ``pycps_sysml.core_definitions()`` rather than restated here so
    a vocabulary change is covered without editing this test.
    """
    text = pycps_sysml.core_definitions().read_text(encoding="utf-8")
    declarations = re.findall(
        r"^\s*(part def|attribute def|port def)\s+([A-Za-z_]\w*)",
        text,
        re.MULTILINE,
    )
    return {name: f"{kind} {name}" for kind, name in declarations}


#: Core definitions and the declaration prefix that would reintroduce one locally.
CORE_DEFINITION_PREFIXES = _core_definition_prefixes()

#: Definitions the GainOffset system root receives from the canonical FMU
#: architecture include rather than declaring itself. The FMU architecture
#: shares the system's package, so its keys stay bare.
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


def _core_definition_package() -> str:
    """The package the packaged core definitions declare themselves in."""
    match = re.search(
        r"^\s*package\s+(\w+)",
        pycps_sysml.core_definitions().read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    assert match is not None, "packaged core definitions declare no package"
    return match.group(1)


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


def test_every_fmu_component_specializes_fmu_model() -> None:
    """Drift caught: an FMU component carries fmu_meta but stays implicit."""
    implicit = []
    for directory in sorted({path.parent for path in _physical_sysml_files()}):
        architecture = pycps_sysml.load(directory, pycps_sysml.core_definitions())
        implicit.extend(
            f"{directory}: 'part def {definition.name}' carries fmu_meta but "
            "does not specialize FmuModel"
            for definition in architecture.part_definitions.values()
            if "fmu_meta" in definition.attributes
            and definition.name != "FmuModel"
            and not is_fmu_model(architecture, definition)
        )
    assert implicit == [], "\n".join(implicit)


def test_fixture_resolves_core_markers_through_the_include_path() -> None:
    """Drift caught: the include path stops resolving the core or FMU definitions."""
    architecture = pycps_sysml.load(
        GAINOFFSET_ARCHITECTURE,
        pycps_sysml.core_definitions(),
        GAINOFFSET_FMU_ARCHITECTURE,
    )

    assert architecture.included_definitions == FMU_INCLUDED_DEFINITIONS | {
        # Package qualification is storage-only: a definition of the model's own
        # package stays bare, a foreign package is keyed "<package>::<name>".
        f"{_core_definition_package()}::{name}"
        for name in CORE_DEFINITION_PREFIXES
    }
    # The keys are storage-only, so the fixture still resolves both markers
    # through the include path to its own compositions.
    assert is_ssp_model(architecture, architecture.get_part_def("System"))
    assert is_fmu_model(architecture, architecture.get_part_def("Generator"))
    validate_role_markers(architecture)
    validate_marker_definitions(architecture)
