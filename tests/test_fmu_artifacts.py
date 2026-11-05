"""Contract: the GainOffset FMU definition and its build artifacts agree.

``models/fmu/GainOffset`` keeps only the authored inputs (``src/GainOffset.c``
and ``FIXTURE.md``); it carries no committed definition. The committed
``artifacts/build/GainOffset/Generator.fmu`` archive *is* the definition: it
ships ``modelDescription.xml``, the generated C interface headers, and the
compiled binary. Four independently produced pieces must describe the same
interface: ``modelDescription.xml`` (pyfmi_sysml2 model description), the C
header (pyfmi_sysml2 C interface), the compiled binary (fixture-local gcc), and
the packaged archive (pyfmi_sysml2 packaging). Each one can drift on its own: a
stale header after a SysML rename, a binary compiled before the header changed,
an archive that kept the previous ``.so``, or a model description whose
``ModelStructure`` no longer lists the outputs.

These tests read only committed files -- the archive and the tracked binary --
and judge the pieces the FMI validator does not cover (value-reference scoping,
binary symbols, archive layout).
"""

from __future__ import annotations

import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import pyfmi_sysml2

REPO_ROOT = Path(__file__).resolve().parents[1]
#: Committed archive and tracked binary.
ARTIFACTS = REPO_ROOT / "artifacts" / "build" / "GainOffset"
ARCHIVE = ARTIFACTS / "Generator.fmu"
#: Archive members carrying the definition and the generated header.
DESCRIPTION_MEMBER = "modelDescription.xml"
HEADER_MEMBER = "sources/GainOffset_Generator.h"

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


def _members() -> list[str]:
    with zipfile.ZipFile(ARCHIVE) as bundle:
        return bundle.namelist()


def _member_bytes(name: str) -> bytes:
    with zipfile.ZipFile(ARCHIVE) as bundle:
        assert name in bundle.namelist(), f"{ARCHIVE}: missing {name}"
        return bundle.read(name)


def _description_root() -> ET.Element:
    return ET.fromstring(_member_bytes(DESCRIPTION_MEMBER))


def _header_text() -> str:
    return _member_bytes(HEADER_MEMBER).decode("utf-8")


def _scalar_variables() -> list[dict[str, str]]:
    root = _description_root()
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
    root = _description_root()
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
    text = _header_text()
    return {
        name: int(value)
        for name, value in _ENUMERATOR.findall(text)
    }


def _header_vr_count() -> int:
    matches = _VR_COUNT.search(_header_text())
    assert matches is not None, f"{HEADER_MEMBER}: no VrCount enumerator"
    return int(matches.group(1))


def _header_vr_map() -> dict[str, tuple[str, bool]]:
    """Return ``enumerator -> (data type, writable)`` from the VR map."""
    return {
        name: (data_type, writable == "true")
        for name, data_type, writable in _VR_MAP_ENTRY.findall(_header_text())
    }


def _model_identifier() -> str:
    root = _description_root()
    return next(
        element.attrib["modelIdentifier"]
        for element in root
        if _local(element.tag) == "CoSimulation"
    )


def test_model_description_declares_one_cosimulation_interface() -> None:
    """Drift caught: a second interface, or an archive named for another model."""
    root = _description_root()
    assert root.attrib["fmiVersion"] == "2.0"
    interfaces = [
        element for element in root if _local(element.tag) == "CoSimulation"
    ]
    assert len(interfaces) == 1
    assert interfaces[0].attrib["modelIdentifier"] == ARCHIVE.stem


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
    model_identifier = _model_identifier()
    binary = ARTIFACTS / f"{model_identifier}.so"
    symbols = subprocess.run(
        ["nm", "-D", "--defined-only", str(binary)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    for entry_point in ("fmi2Instantiate", "fmi2DoStep", "fmi2GetReal", "fmi2SetReal"):
        assert re.search(rf"\bT {entry_point}$", symbols, re.MULTILINE), entry_point


def test_archive_root_holds_the_model_description() -> None:
    """Drift caught: the definition moved out of the archive root."""
    names = _members()
    assert len(names) == len(set(names)), names
    assert DESCRIPTION_MEMBER in names
    assert all("/" in name for name in names if name != DESCRIPTION_MEMBER), names
    assert not any(
        name.startswith("/") or ".." in Path(name).parts for name in names
    ), names


def test_archive_headers_live_under_sources() -> None:
    """Drift caught: a header outside sources/, or a dropped FMI header."""
    names = set(_members())
    headers = [name for name in _members() if name.endswith(".h")]
    assert HEADER_MEMBER in headers
    for header in headers:
        assert header.startswith("sources/"), header
        assert "/" not in header.removeprefix("sources/"), header
    for public in pyfmi_sysml2.fmi2_headers():
        member = f"sources/{public.name}"
        assert member in names, public
        assert _member_bytes(member) == public.read_bytes(), public


def test_archive_binary_matches_the_tracked_binary() -> None:
    """Drift caught: the archive kept a stale binary, or the binary lost its bit."""
    model_identifier = _model_identifier()
    member = f"binaries/linux64/{model_identifier}.so"
    assert member in _members()
    binary = ARTIFACTS / f"{model_identifier}.so"
    assert binary.is_file(), binary
    assert _member_bytes(member) == binary.read_bytes()
    assert binary.stat().st_mode & 0o111
