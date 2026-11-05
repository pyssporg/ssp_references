"""Contract: the GainOffset FMU definition and its build artifacts agree.

``models/fmu/GainOffset`` keeps the authored inputs (``src/GainOffset.c``,
``architecture/GainOffset.sysml``, and ``FIXTURE.md``); it carries no committed
definition. The committed ``artifacts/build/GainOffset/Generator.fmu`` archive
*is* the definition: it ships ``modelDescription.xml``, the generated C
interface headers, and the compiled binary. Four independently produced pieces
must describe the same interface: ``modelDescription.xml`` (pyfmi_sysml2 model
description), the C header (pyfmi_sysml2 C interface), the compiled binary
(fixture-local gcc), and the packaged archive (pyfmi_sysml2 packaging). Each one
can drift on its own: a stale header after a SysML rename, a binary compiled
before the header changed, an archive that kept the previous ``.so``, or a model
description whose ``ModelStructure`` no longer lists the outputs. The two layers
are split by ownership, not by projection: ``models/ssp/GainOffset/architecture``
holds only the system composition and reaches the canonical FMU definitions
through ``build_fixture(includes=...)``, so a copy or link there is a defect.

These tests read committed files -- the archive, the tracked binary, and the
authored sources -- and the loose build output the archive is packaged from, and
judge the pieces the FMI validator does not cover (value-reference scoping, binary
symbols, archive layout, the exported identity).
"""

from __future__ import annotations

import ast
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
#: Loose build output, read by the identity test before the archive is repackaged.
MODEL_DESCRIPTION = ARTIFACTS / "modelDescription.xml"
#: Archive members carrying the definition and the generated header.
DESCRIPTION_MEMBER = "modelDescription.xml"
HEADER_MEMBER = "sources/GainOffset_Generator.h"

#: Authored architecture: the FMU definition and the SSP system that reuses it.
FMU_ARCHITECTURE = REPO_ROOT / "models" / "fmu" / "GainOffset" / "architecture"
FMU_DEFINITION = FMU_ARCHITECTURE / "GainOffset.sysml"
SSP_ARCHITECTURE = REPO_ROOT / "models" / "ssp" / "GainOffset" / "architecture"
SSP_BUILD_SCRIPT = REPO_ROOT / "models" / "ssp" / "GainOffset" / "build.py"
SYSTEM_DEFINITION = SSP_ARCHITECTURE / "System.sysml"
#: The FMU source that must name the exported member, not the removed composition.
C_SOURCE = REPO_ROOT / "models" / "fmu" / "GainOffset" / "src" / "GainOffset.c"

#: The member ``part def`` the FMU exports, and the GUID pyfmi_sysml2 derives for
#: it: ``uuid5(NAMESPACE_URL, "pyssp_sysml2/Generator")``.
EXPORTED_MODEL = "Generator"
EXPORTED_GUID = "{eca0627b-dad2-5d71-90b2-e450ef615122}"

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


def _sysml_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _declares(text: str, declaration: str) -> bool:
    """Whether ``text`` declares exactly ``declaration``.

    Anchored and word-bounded, so ``part def Fmu`` cannot match the
    ``part def FmuModel`` specialization it was replaced by.
    """
    return re.search(rf"^\s*{re.escape(declaration)}\b", text, re.MULTILINE) is not None


def _path_segments(expression: ast.expr) -> tuple[str, ...]:
    """String segments of a left-associative ``/ "segment" / ...`` expression."""
    segments: list[str] = []
    node = expression
    while isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        if isinstance(node.right, ast.Constant) and isinstance(node.right.value, str):
            segments.append(node.right.value)
        node = node.left
    return tuple(reversed(segments))


def _include_roots(build_script: Path) -> set[Path]:
    """Directories a build script passes as ``includes=``, resolved from its anchors.

    ``build.py`` names its include through module constants (``REPO_ROOT /
    "models" / ...``), so the segments are re-anchored at every ancestor of the
    script's model directory; the canonical directory is what the caller asserts.
    """
    tree = ast.parse(build_script.read_text(encoding="utf-8"))
    definitions = {
        target.id: node.value
        for node in tree.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    anchors = tuple(
        anchor
        for anchor in (build_script.parent, *build_script.parent.parents)
        if anchor.is_relative_to(REPO_ROOT)
    )

    def segment_sets(
        expression: ast.expr, seen: frozenset[str] = frozenset()
    ) -> set[tuple[str, ...]]:
        if isinstance(expression, ast.Name):
            value = definitions.get(expression.id)
            if value is None or expression.id in seen:
                return set()
            return segment_sets(value, seen | {expression.id})
        segments = _path_segments(expression)
        if segments:
            return {segments}
        found: set[tuple[str, ...]] = set()
        for child in ast.iter_child_nodes(expression):
            found |= segment_sets(child, seen)
        return found

    return {
        anchor.joinpath(*segments).resolve()
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        for keyword in node.keywords
        if keyword.arg == "includes"
        for segments in segment_sets(keyword.value)
        for anchor in anchors
    }


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


def test_system_architecture_holds_only_the_composition() -> None:
    """Drift caught: the system fixture copies or links the FMU definition."""
    names = sorted(path.name for path in SSP_ARCHITECTURE.iterdir())
    assert names == ["System.sysml"], (
        f"{SSP_ARCHITECTURE}: expected only System.sysml, found {names}"
    )
    assert not SSP_ARCHITECTURE.is_symlink(), SSP_ARCHITECTURE
    assert not (SSP_ARCHITECTURE / FMU_DEFINITION.name).exists(), (
        "the SSP architecture carries a copy or link of the FMU definition; "
        "the build must include the canonical FMU architecture instead"
    )
    assert FMU_DEFINITION.is_file(), f"missing canonical FMU definition {FMU_DEFINITION}"
    assert not FMU_DEFINITION.is_symlink(), FMU_DEFINITION
    assert sorted(path.name for path in FMU_ARCHITECTURE.iterdir()) == [
        FMU_DEFINITION.name
    ]


def test_system_build_includes_the_canonical_fmu_architecture() -> None:
    """Drift caught: the SSP build stops importing the canonical FMU definitions."""
    roots = _include_roots(SSP_BUILD_SCRIPT)
    assert FMU_ARCHITECTURE.resolve() in roots, (
        f"{SSP_BUILD_SCRIPT}: build_fixture(includes=...) must name "
        f"{FMU_ARCHITECTURE}, found {sorted(roots)}"
    )
    assert SSP_ARCHITECTURE.resolve() not in roots, (
        f"{SSP_BUILD_SCRIPT}: includes the SSP architecture itself instead of "
        "the canonical FMU architecture"
    )


def test_fmu_architecture_declares_only_the_fmu_definitions() -> None:
    """Drift caught: the FMU layer grows system composition, or keeps ``Fmu``."""
    fmu_text = _sysml_text(FMU_DEFINITION)

    for declared in (
        "port def GeneratorParameters",
        "attribute def GeneratorFmu :> FmuMetadata",
        "part def Generator :> FmuModel",
    ):
        assert _declares(fmu_text, declared), (
            f"{FMU_DEFINITION.name}: missing declaration {declared!r}"
        )

    for leaked in (
        "part def Fmu",
        "part def SspModel",
        "part def System",
        "part def Analysis",
        "attribute def Experiment",
    ):
        assert not _declares(fmu_text, leaked), (
            f"{FMU_DEFINITION.name}: declares {leaked!r}, owned by the core "
            "dialect or the system layer"
        )


def test_system_architecture_declares_only_the_composition() -> None:
    """Drift caught: the system layer grows FMU definitions, or drops its markers."""
    system_text = _sysml_text(SYSTEM_DEFINITION)

    for declared in (
        "part def System :> SspModel",
        "part def baseline :> Analysis",
        "attribute def BaselineExperiment :> Experiment",
    ):
        assert _declares(system_text, declared), (
            f"{SYSTEM_DEFINITION.name}: missing declaration {declared!r}"
        )

    for leaked in (
        "part def Generator",
        "part def FmuModel",
        "port def GeneratorParameters",
        "attribute def GeneratorFmu",
    ):
        assert not _declares(system_text, leaked), (
            f"{SYSTEM_DEFINITION.name}: declares {leaked!r}, owned by the FMU "
            "architecture and reached through the include"
        )


def test_model_description_exports_the_member_model_identity() -> None:
    """Drift caught: the binding still names the deleted ``Fmu`` composition root."""
    assert MODEL_DESCRIPTION.is_file(), (
        f"{MODEL_DESCRIPTION}: missing build output; regenerate it with "
        "python3 scripts/build_models.py run GainOffset"
    )
    root = ET.fromstring(MODEL_DESCRIPTION.read_text(encoding="utf-8"))
    assert root.attrib["modelName"] == EXPORTED_MODEL, root.attrib["modelName"]
    assert root.attrib["guid"] == EXPORTED_GUID, root.attrib["guid"]
    interface = next(
        element for element in root if _local(element.tag) == "CoSimulation"
    )
    assert interface.attrib["modelIdentifier"] == EXPORTED_MODEL, (
        interface.attrib["modelIdentifier"]
    )


def test_c_source_names_the_exported_member_model() -> None:
    """Drift caught: the C source still reports the deleted composition root."""
    model_name = re.search(
        r'^\s*#define MODEL_NAME "([^"]*)"',
        C_SOURCE.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    assert model_name is not None, f"{C_SOURCE}: no MODEL_NAME define"
    assert model_name.group(1) == EXPORTED_MODEL, model_name.group(1)
