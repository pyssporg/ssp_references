#!/usr/bin/env python3

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from pyssp_standard import FMU, SSP
from pyssp_standard.common_content_ssc import (
    TypeBoolean,
    TypeEnumeration,
    TypeInteger,
    TypeReal,
    TypeString,
)
from pyssp_standard.ssd import Component, Connection, Connector, SSD, System


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODELS_DIR = REPO_ROOT / "models"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Package a single FMU into an SSP using pyssp_standard."
    )
    parser.add_argument("fmu", type=Path, help="Path to the FMU file to package.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output .ssp path. Defaults to models/reference_fmus/<fmu-stem>/<fmu-stem>.ssp.",
    )
    parser.add_argument(
        "--system-name",
        help="Override the SSP system name. Defaults to the FMU model name.",
    )
    parser.add_argument(
        "--component-name",
        help="Override the component name inside the SSP. Defaults to the FMU model name.",
    )
    return parser.parse_args()


def clone_type(type_):
    if isinstance(type_, TypeReal):
        return TypeReal(
            unit=type_.unit,
            min=type_.min,
            max=type_.max,
            start=type_.start,
        )
    if isinstance(type_, TypeInteger):
        return TypeInteger()
    if isinstance(type_, TypeBoolean):
        return TypeBoolean()
    if isinstance(type_, TypeString):
        return TypeString()
    if isinstance(type_, TypeEnumeration):
        if not type_.name:
            raise ValueError("Enumeration connector is missing a declared type name")
        return TypeEnumeration(type_.name)
    raise TypeError(f"Unsupported FMU variable type: {type(type_).__name__}")


def read_enumeration_type_names(fmu_path: Path) -> dict[str, str]:
    with zipfile.ZipFile(fmu_path, "r") as archive:
        root = ET.fromstring(archive.read("modelDescription.xml"))

    type_names: dict[str, str] = {}
    model_variables = root.find("ModelVariables")
    if model_variables is None:
        return type_names

    for scalar_variable in model_variables.findall("ScalarVariable"):
        name = scalar_variable.attrib.get("name")
        if not name:
            continue
        enumeration = scalar_variable.find("Enumeration")
        if enumeration is None:
            continue
        declared_type = enumeration.attrib.get("declaredType")
        if declared_type:
            type_names[name] = declared_type
    return type_names


def clone_variable_type(variable, enumeration_type_names: dict[str, str]):
    type_ = variable.type_
    if isinstance(type_, TypeEnumeration) and not type_.name:
        enum_name = enumeration_type_names.get(variable.name)
        if enum_name:
            return TypeEnumeration(enum_name)
    return clone_type(type_)


def add_system_mapping(
    system: System,
    component: Component,
    causality: str,
    variables,
    enumeration_type_names: dict[str, str],
) -> None:
    if causality == "output":
        system_kind = "output"
    elif causality == "input":
        system_kind = "input"
    elif causality == "parameter":
        system_kind = "parameter"
    else:
        raise ValueError(f"Unsupported causality for packaging: {causality}")

    for variable in variables:
        component.connectors.append(
            Connector(
                name=variable.name,
                kind=system_kind,
                type_=clone_variable_type(variable, enumeration_type_names),
            )
        )
        system.connectors.append(
            Connector(
                name=variable.name,
                kind=system_kind,
                type_=clone_variable_type(variable, enumeration_type_names),
            )
        )
        if causality == "output":
            system.connections.append(
                Connection(
                    start_element=component.name,
                    start_connector=variable.name,
                    end_connector=variable.name,
                )
            )
        else:
            system.connections.append(
                Connection(
                    start_connector=variable.name,
                    end_element=component.name,
                    end_connector=variable.name,
                )
            )


def build_ssd(ssd: SSD, component_name: str, resource_name: str, fmu_path: Path) -> None:
    with FMU(fmu_path, mode="r") as fmu:
        model_description = fmu.model_description
    enumeration_type_names = read_enumeration_type_names(fmu_path)

    system = System(name=ssd.name)
    component = Component()
    component.name = component_name
    component.source = f"resources/{resource_name}"

    add_system_mapping(
        system,
        component,
        "parameter",
        model_description.parameters,
        enumeration_type_names,
    )
    add_system_mapping(
        system,
        component,
        "input",
        model_description.inputs,
        enumeration_type_names,
    )
    add_system_mapping(
        system,
        component,
        "output",
        model_description.outputs,
        enumeration_type_names,
    )

    system.elements.append(component)
    ssd.system = system


def package_fmu(fmu_path: Path, output_path: Path, system_name: str, component_name: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()

    with SSP(output_path, mode="w") as ssp:
        ssp.add_resource(fmu_path)
        with ssp.system_structure as ssd:
            ssd.name = system_name
            ssd.version = "1.0"
            build_ssd(
                ssd=ssd,
                component_name=component_name,
                resource_name=fmu_path.name,
                fmu_path=fmu_path,
            )


def main() -> int:
    args = parse_args()
    fmu_path = args.fmu.resolve()
    if not fmu_path.is_file():
        raise FileNotFoundError(f"FMU not found: {fmu_path}")
    if fmu_path.suffix.lower() != ".fmu":
        raise ValueError(f"Expected an .fmu file, got: {fmu_path.name}")

    with FMU(fmu_path, mode="r") as fmu:
        model_name = fmu.model_description.model_name or fmu_path.stem

    output_path = (
        args.output.resolve()
        if args.output
        else DEFAULT_MODELS_DIR / fmu_path.stem / f"{fmu_path.stem}.ssp"
    )
    system_name = args.system_name or model_name
    component_name = args.component_name or model_name

    package_fmu(fmu_path, output_path, system_name, component_name)
    print(f"Created SSP: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
