#!/usr/bin/env python3
"""Round-trip an SSD through the ``pyssp`` CLI and report structural loss.

This script is intentionally artifact-only: it reads an SSD, invokes an
external ``pyssp`` executable to generate SysML and to regenerate the SSD, and
then compares the two XML documents. It does not import ``pyssp_sysml2`` or
``pyssp_standard``, so the SysML tool can live in a different environment or
track a different upstream revision.

Example:

    python3 scripts/check_sysml_roundtrip.py \
        artifacts/models/signal_step_gain/baseline/SystemStructure.ssd \
        --output /tmp/sysml_roundtrip

    # Use a tool environment with its own pyssp_sysml2/pyssp_standard versions
    python3 scripts/check_sysml_roundtrip.py ... \
        --pyssp /path/to/sysml-venv/bin/pyssp
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def _tag(element: ET.Element) -> str:
    return element.tag.rsplit("}", 1)[-1]


def summarize_ssd(path: Path) -> dict[str, object]:
    root = ET.parse(path).getroot()
    system = next((element for element in root.iter() if _tag(element) == "System"), None)
    components = {}
    connectors = {}
    connections = []
    bindings = []
    if system is not None:
        for element in system:
            if _tag(element) == "Elements":
                for component in element:
                    name = component.attrib.get("name", "")
                    components[name] = component.attrib.get("source")
                    for connector in component:
                        if _tag(connector) == "Connectors":
                            for item in connector:
                                connectors[(name, item.attrib.get("name", ""))] = item.attrib.get("kind")
            elif _tag(element) == "Connections":
                for connection in element:
                    connections.append(
                        (
                            connection.attrib.get("startElement"),
                            connection.attrib.get("startConnector"),
                            connection.attrib.get("endElement"),
                            connection.attrib.get("endConnector"),
                        )
                    )
            elif _tag(element) == "ParameterBindings":
                for binding in element:
                    if _tag(binding) == "ParameterBinding":
                        bindings.append(binding.attrib.get("source"))
    default_experiment = next(
        (element.attrib for element in root.iter() if _tag(element) == "DefaultExperiment"),
        {},
    )
    return {
        "system": system.attrib.get("name") if system is not None else None,
        "components": components,
        "connectors": connectors,
        "connections": sorted(connections),
        "parameter_bindings": bindings,
        "default_experiment": default_experiment,
    }


def differences(before: dict[str, object], after: dict[str, object]) -> list[str]:
    messages = []
    for key in ("system", "components", "connectors", "connections", "parameter_bindings", "default_experiment"):
        if before[key] != after[key]:
            messages.append(f"{key}: {before[key]!r} -> {after[key]!r}")
    return messages


def _default_pyssp_command() -> str:
    if "PYSSP" in os.environ:
        return os.environ["PYSSP"]
    sibling = Path(sys.executable).with_name("pyssp")
    return str(sibling) if sibling.is_file() else "pyssp"


def _run_pyssp(command: str, arguments: list[str]) -> None:
    executable = shutil.which(command) if os.sep not in command else command
    if executable is None:
        raise SystemExit(
            f"pyssp executable not found: {command!r}. Install pyssp_sysml2 in the "
            "SysML tool environment or pass --pyssp /path/to/venv/bin/pyssp."
        )
    result = subprocess.run([executable, *arguments])
    if result.returncode != 0:
        raise SystemExit(
            f"pyssp {' '.join(arguments[:2])} failed with exit code {result.returncode}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ssd", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--composition")
    parser.add_argument(
        "--pyssp",
        default=_default_pyssp_command(),
        help="pyssp executable to invoke (default: $PYSSP or 'pyssp').",
    )
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    architecture = output / "architecture.sysml"
    regenerated = output / "SystemStructure.ssd"

    composition = args.composition or summarize_ssd(args.ssd)["system"]
    if not composition:
        raise SystemExit("Composition name must be provided or present on the SSD system")

    _run_pyssp(
        args.pyssp,
        [
            "generate",
            "sysml",
            "--ssd",
            str(args.ssd),
            "--composition",
            composition,
            "--output",
            str(architecture),
        ],
    )
    _run_pyssp(
        args.pyssp,
        [
            "generate",
            "ssd",
            "--architecture",
            str(output),
            "--composition",
            composition,
            "--output",
            str(regenerated),
        ],
    )

    before = summarize_ssd(args.ssd)
    after = summarize_ssd(regenerated)
    messages = differences(before, after)

    print(f"architecture: {architecture}")
    print(f"regenerated:  {regenerated}")
    if not messages:
        print("round-trip: structurally equivalent")
        return 0

    print("round-trip loss:")
    for message in messages:
        print(f"  - {message}")
    return 1 if args.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())
