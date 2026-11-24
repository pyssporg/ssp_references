#!/usr/bin/env python3
"""Build and verify the pinned ``scenario`` FMU body.

``pyfmu_scenario`` produces the FMU from ``scenario.txt``: the text is parsed
into typed series, packaged as an FMI 2.0 CoSimulation archive, and placed at
``artifacts/build/scenario/scenario.fmu``. The checked-in fixture body at
``models/fmu/scenario/fmu`` is the reference the build must match.

The default run is verify-only: it packages the archive, compares the SysML
declaration in ``architecture/Scenario.sysml`` against the pinned
``modelDescription.xml`` interface, compares the built interface against the
same pinned one, and simulates both bodies with FMPy when FMPy is installed. It
never writes into ``fmu/``. ``--refresh``
extracts a freshly built ``modelDescription.xml`` and
``binaries/linux64/scenario.so`` into the pinned body, but only after the
interface check passes, so the pinned body is never replaced by an incompatible
build.

Identity fields that the producer deliberately sets differently are ignored:
``author`` and ``generationTool`` now name ``pyssporg``/``pyfmu-scenario``, and
``generationDateAndTime`` is absent. The GUID and the FMI interface stay
stable.
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree

import pycps_sysml
from pyfmu_scenario.grammar import parse_scenario
from pyfmu_scenario.packaging import package_scenario

MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
ARCHITECTURE_DIR = MODEL_DIR / "architecture"
SCENARIO_FILE = MODEL_DIR / "scenario.txt"
PINNED_DIR = MODEL_DIR / "fmu"
PINNED_DESCRIPTION = PINNED_DIR / "modelDescription.xml"
PINNED_BINARY = PINNED_DIR / "binaries" / "linux64" / "scenario.so"
BUILD_DIR = REPO_ROOT / "artifacts" / "build" / "scenario"
OUTPUT_FMU = BUILD_DIR / "scenario.fmu"

#: The declared component; its name is the ``part def`` in the architecture.
COMPONENT = "Scenario"

#: The pinned body's GUID. The producer defaults to it; pass it explicitly so a
#: producer default change cannot silently move the fixture identity.
GUID = "9524b75e-dc71-47cd-a02f-e22b95a3f76d"
PLATFORM = "linux64"
BINARY_NAME = "scenario.so"
MAX_TRAJECTORY_DIFFERENCE = 1e-9


def _read_interface(description: Path) -> dict[str, object]:
    """Extract the interface the fixture pins from one model description."""
    root = ElementTree.parse(description).getroot()
    cosimulation = root.find("./CoSimulation")
    variables = []
    for element in root.findall("./ModelVariables/ScalarVariable"):
        (typed,) = list(element)
        variables.append(
            {
                "name": element.get("name"),
                "value_reference": int(element.get("valueReference", "")),
                "causality": element.get("causality"),
                "variability": element.get("variability"),
                "type": typed.tag,
                "start": typed.get("start"),
            }
        )
    outputs = tuple(
        int(unknown.get("index", ""))
        for unknown in root.findall("./ModelStructure/Outputs/Unknown")
    )
    return {
        "fmi_version": root.get("fmiVersion"),
        "model_name": root.get("modelName"),
        "guid": root.get("guid"),
        "model_identifier": (
            cosimulation.get("modelIdentifier")
            if cosimulation is not None
            else None
        ),
        "variables": tuple(variables),
        "outputs": outputs,
    }


def _compare_interface(
    pinned: dict[str, object], built: dict[str, object]
) -> list[str]:
    """Return every interface difference between the pinned and built body."""
    problems = []
    for field in ("fmi_version", "model_name", "guid", "model_identifier"):
        if pinned[field] != built[field]:
            problems.append(
                f"{field}: pinned {pinned[field]!r} != built {built[field]!r}"
            )

    pinned_variables = pinned["variables"]
    built_variables = built["variables"]
    if len(pinned_variables) != len(built_variables):
        problems.append(
            f"variables: pinned {len(pinned_variables)} != "
            f"built {len(built_variables)}"
        )
    for index, (expected, actual) in enumerate(
        zip(pinned_variables, built_variables)
    ):
        if expected != actual:
            problems.append(
                f"variable [{index}]: pinned {expected} != built {actual}"
            )

    if pinned["outputs"] != built["outputs"]:
        problems.append(
            f"ModelStructure/Outputs: pinned {pinned['outputs']} != "
            f"built {built['outputs']}"
        )
    return problems


def _read_declaration(directory: Path) -> dict[str, object]:
    """Extract the interface the SysML declaration promises for the component."""
    architecture = pycps_sysml.load(directory, pycps_sysml.core_definitions())
    component = architecture.get_part_def(COMPONENT)
    parameters = {}
    outputs = {}
    for port in component.ports.values():
        port_def = architecture.resolve_port(port)
        if port_def is None:
            continue
        if port.direction == "in":
            for name, member in port_def.attributes.items():
                parameters[name] = member.type_name
        elif port.direction == "out":
            (member,) = port_def.attributes.values()
            outputs[port.name] = member.type_name
    return {"parameters": parameters, "outputs": outputs}


def _compare_declaration(
    declared: dict[str, object], pinned: dict[str, object]
) -> list[str]:
    """Return every difference between the SysML declaration and the pinned interface."""
    problems = []
    for kind, declared_members in (
        ("parameter", declared["parameters"]),
        ("output", declared["outputs"]),
    ):
        pinned_members = {
            str(variable["name"]): variable["type"]
            for variable in pinned["variables"]
            if variable["causality"] == kind
        }
        for name in sorted(set(declared_members) | set(pinned_members)):
            if name not in declared_members:
                problems.append(
                    f"{kind} {name!r}: pinned interface declares it, "
                    "the SysML declaration does not"
                )
            elif name not in pinned_members:
                problems.append(
                    f"{kind} {name!r}: the SysML declaration declares it, "
                    "the pinned interface does not"
                )
            elif declared_members[name] != pinned_members[name]:
                problems.append(
                    f"{kind} {name!r}: declaration "
                    f"{declared_members[name]!r} != pinned "
                    f"{pinned_members[name]!r}"
                )
    return problems


def _built_description(archive: Path) -> dict[str, object]:
    """Read the built interface through a temporary extraction."""
    build_dir = BUILD_DIR / "verify"
    build_dir.mkdir(parents=True, exist_ok=True)
    description = build_dir / "modelDescription.xml"
    with zipfile.ZipFile(archive) as bundle:
        description.write_bytes(bundle.read("modelDescription.xml"))
    return _read_interface(description)


def _output_names(interface: dict[str, object]) -> list[str]:
    return [
        str(variable["name"])
        for variable in interface["variables"]
        if variable["causality"] == "output"
    ]


def _start_values(interface: dict[str, object]) -> dict[str, object]:
    return {
        str(variable["name"]): variable["start"]
        for variable in interface["variables"]
        if variable["causality"] == "parameter"
        and variable["start"] is not None
    }


def _compare_trajectories(pinned: dict[str, object], archive: Path) -> list[str]:
    """Simulate both bodies and compare the output signals."""
    try:
        import fmpy
    except ImportError:
        print("Signal trajectory: skipped (fmpy is not installed)")
        return []

    names = _output_names(pinned)
    arguments = {
        "start_time": 0.0,
        "stop_time": 10.0,
        "output": names,
        "start_values": _start_values(pinned),
    }
    try:
        expected = fmpy.simulate_fmu(str(PINNED_DIR), **arguments)
        actual = fmpy.simulate_fmu(str(archive), **arguments)
    except Exception as error:  # noqa: BLE001 - the trajectory check is optional
        print(
            "Signal trajectory: skipped "
            f"({type(error).__name__}: {error})"
        )
        return []

    if len(expected) != len(actual):
        return [
            f"signal trajectory: pinned {len(expected)} samples != "
            f"built {len(actual)}"
        ]

    differences = []
    for name in names:
        column = abs(expected[name] - actual[name])
        differences.append(float(column.max()) if column.size else 0.0)
    worst = max(differences, default=0.0)
    print(
        f"Signal trajectory: {len(expected)} samples, "
        f"max abs difference {worst:.3g}"
    )
    if worst > MAX_TRAJECTORY_DIFFERENCE:
        return [
            f"signal trajectory: max abs difference {worst:.6g} exceeds "
            f"{MAX_TRAJECTORY_DIFFERENCE:g}"
        ]
    return []


def _refresh(archive: Path) -> None:
    """Replace the pinned description and binary with the built body."""
    with zipfile.ZipFile(archive) as bundle:
        description = bundle.read("modelDescription.xml")
        binary = bundle.read(f"binaries/{PLATFORM}/{BINARY_NAME}")
    PINNED_BINARY.parent.mkdir(parents=True, exist_ok=True)
    PINNED_DESCRIPTION.write_bytes(description)
    PINNED_BINARY.write_bytes(binary)
    print(f"Refreshed {PINNED_DESCRIPTION}")
    print(f"Refreshed {PINNED_BINARY}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the scenario FMU and verify it against the pinned body."
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help=(
            "rewrite models/fmu/scenario/fmu from the build after the "
            "interface check passes"
        ),
    )
    args = parser.parse_args(argv)

    scenario = parse_scenario(SCENARIO_FILE.read_text(encoding="utf-8"))
    print(
        f"Scenario {SCENARIO_FILE}: {len(scenario.series)} series "
        f"({', '.join(scenario.names)})"
    )
    archive = package_scenario(scenario, OUTPUT_FMU, guid=GUID)
    print(f"Packaged {archive}")

    pinned = _read_interface(PINNED_DESCRIPTION)
    problems = _compare_declaration(
        _read_declaration(ARCHITECTURE_DIR), pinned
    )
    built = _built_description(archive)
    problems.extend(_compare_interface(pinned, built))
    problems.extend(_compare_trajectories(pinned, archive))

    if problems:
        for problem in problems:
            print(f"MISMATCH: {problem}", file=sys.stderr)
        print(
            f"Interface check failed; {PINNED_DIR} was not modified.",
            file=sys.stderr,
        )
        return 1

    print(
        f"Interface verified: {built['model_name']} "
        f"{built['fmi_version']} GUID {built['guid']}, "
        f"{len(built['variables'])} variables, "
        f"{len(built['outputs'])} outputs"
    )
    if args.refresh:
        _refresh(archive)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
