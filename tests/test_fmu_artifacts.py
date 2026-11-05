"""Contract: the GainOffset FMU's four artifacts agree on one variable set.

The FMU for ``models/fmu/GainOffset`` is generated here from SysML, so four
independently produced files must describe the same interface:
``modelDescription.xml`` (pyfmi_sysml2 model description), the C header
(pyfmi_sysml2 C interface), the compiled binary (fixture-local gcc), and the
staged FMU tree (pyfmi_sysml2 packaging). Each one can drift on its own: a
stale header after a SysML rename, a binary compiled before the header changed,
a packaged tree that kept the previous ``.so``, or a model description whose
``ModelStructure`` no longer lists the outputs.

These tests read the committed fixture, not the build directory, and judge the
pieces the FMI validator does not cover (value-reference scoping, binary
symbols, archive layout).
"""

from __future__ import annotations

import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "models" / "fmu" / "GainOffset"
FMU = FIXTURE / "fmu"
MODEL_DESCRIPTION = FMU / "modelDescription.xml"
HEADER = FMU / "sources" / "GainOffset_Generator.h"

#: C data type constants emitted by pyfmi_sysml2 -> FMI scalar type element.
FMI_TYPE_BY_DATATYPE = {
    "GAINOFFSET_DATA_REAL": "Real",
    "GAINOFFSET_DATA_INTEGER": "Integer",
    "GAINOFFSET_DATA_BOOLEAN": "Boolean",
    "GAINOFFSET_DATA_STRING": "String",
}

_ENUMERATOR = re.compile(r"^\s*(GAINOFFSET_GENERATOR_VR_[A-Z0-9_]+)\s*=\s*(\d+)", re.MULTILINE)
_VR_COUNT = re.compile(r"GainOffset_Generator_VrCount\s*=\s*(\d+)")
_VR_MAP_ENTRY = re.compile(
    r"vr_map\[(GAINOFFSET_GENERATOR_VR_[A-Z0-9_]+)\]\s*=\s*"
    r"\{[^,]+,\s*(GAINOFFSET_DATA_[A-Z]+),\s*(true|false)\}"
)


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _scalar_variables() -> list[dict[str, str]]:
    root = ET.parse(MODEL_DESCRIPTION).getroot()
    variables: list[dict[str, str]] = []
    for element in root.iter():
        if _local(element.tag) != "ScalarVariable":
            continue
        children = [child for child in element]
        assert len(children) == 1, element.attrib
        variables.append(
            {
                **element.attrib,
                "type": _local(children[0].tag),
            }
        )
    return variables


def _model_structure_indices(section: str) -> list[int]:
    root = ET.parse(MODEL_DESCRIPTION).getroot()
    indices: list[int] = []
    for element in root.iter():
        if _local(element.tag) == section:
            indices = [
                int(unknown.attrib["index"])
                for unknown in element
                if _local(unknown.tag) == "Unknown"
            ]
    return indices


def _header_enumerators() -> dict[str, int]:
    text = HEADER.read_text(encoding="utf-8")
    return {
        name: int(value)
        for name, value in _ENUMERATOR.findall(text)
    }


def _header_vr_count() -> int:
    matches = _VR_COUNT.search(HEADER.read_text(encoding="utf-8"))
    assert matches is not None, f"{HEADER}: no VrCount enumerator"
    return int(matches.group(1))


def _header_vr_map() -> dict[str, tuple[str, bool]]:
    """Return ``enumerator -> (data type, writable)`` from the VR map."""
    return {
        name: (data_type, writable == "true")
        for name, data_type, writable in _VR_MAP_ENTRY.findall(
            HEADER.read_text(encoding="utf-8")
        )
    }


def test_model_description_declares_one_cosimulation_interface() -> None:
    """Drift caught: a second interface, or a Model Exchange-only binary."""
    root = ET.parse(MODEL_DESCRIPTION).getroot()
    assert root.attrib["fmiVersion"] == "2.0"
    interfaces = [
        element for element in root if _local(element.tag) == "CoSimulation"
    ]
    assert len(interfaces) == 1
    model_identifier = interfaces[0].attrib["modelIdentifier"]
    binary = FMU / "binaries" / "linux64" / f"{model_identifier}.so"
    assert binary.is_file(), binary


def test_value_references_are_unique_and_contiguous() -> None:
    """Drift caught: a renamed variable that kept another's value reference."""
    variables = _scalar_variables()
    names = [variable["name"] for variable in variables]
    references = [int(variable["valueReference"]) for variable in variables]
    assert len(set(names)) == len(names)
    assert len(set(references)) == len(references)
    assert sorted(references) == list(range(len(references)))


def test_generated_header_and_model_description_share_the_variable_set() -> None:
    """Drift caught: SysML changed, the header was not regenerated."""
    enumerators = _header_enumerators()
    variables = _scalar_variables()
    assert sorted(enumerators.values()) == sorted(
        int(variable["valueReference"]) for variable in variables
    )
    assert _header_vr_count() == len(variables)


def test_header_vr_map_matches_types_and_causality() -> None:
    """Drift caught: an output made writable, or a Real declared as Integer."""
    variables = {
        int(variable["valueReference"]): variable for variable in _scalar_variables()
    }
    enumerators = _header_enumerators()
    vr_map = _header_vr_map()
    assert set(vr_map) == set(enumerators)
    for enumerator, (data_type, writable) in vr_map.items():
        variable = variables[enumerators[enumerator]]
        assert FMI_TYPE_BY_DATATYPE[data_type] == variable["type"], variable
        if variable.get("causality") == "output":
            assert not writable, variable
        if writable:
            assert variable.get("causality") == "parameter", variable


def test_model_structure_lists_exactly_the_outputs() -> None:
    """Drift caught: an output missing from ModelStructure, so engines skip it."""
    variables = _scalar_variables()
    outputs = sorted(
        index + 1
        for index, variable in enumerate(variables)
        if variable.get("causality") == "output"
    )
    assert outputs, "the fixture declares no output"
    assert sorted(_model_structure_indices("Outputs")) == outputs
    assert sorted(set(_model_structure_indices("InitialUnknowns"))) == sorted(
        _model_structure_indices("InitialUnknowns")
    )


def test_binary_exports_the_fmi_entry_points() -> None:
    """Drift caught: a packaged stub or a binary built from the wrong source."""
    root = ET.parse(MODEL_DESCRIPTION).getroot()
    model_identifier = next(
        element.attrib["modelIdentifier"]
        for element in root
        if _local(element.tag) == "CoSimulation"
    )
    binary = FMU / "binaries" / "linux64" / f"{model_identifier}.so"
    symbols = subprocess.run(
        ["nm", "-D", "--defined-only", str(binary)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    for entry_point in ("fmi2Instantiate", "fmi2DoStep", "fmi2GetReal", "fmi2SetReal"):
        assert re.search(rf"\bT {entry_point}$", symbols, re.MULTILINE), entry_point


def test_staged_fmu_keeps_the_root_layout() -> None:
    """Drift caught: modelDescription moved out of the root, headers dropped."""
    root = ET.parse(MODEL_DESCRIPTION).getroot()
    assert MODEL_DESCRIPTION.parent == FMU
    assert (FMU / "sources" / "GainOffset_Generator.h").is_file()
    model_identifier = next(
        element.attrib["modelIdentifier"]
        for element in root
        if _local(element.tag) == "CoSimulation"
    )
    assert (FMU / "binaries" / "linux64" / f"{model_identifier}.so").stat().st_mode & 0o111
