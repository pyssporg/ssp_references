from __future__ import annotations

import tempfile
import zipfile
from contextlib import contextmanager
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
from pyssp_standard.ssd import Component, Connection, Connector, DefaultExperiment, SSD, System
from lxml import etree as LET
from lxml.etree import QName

FIXED_GENERATION_DATE_AND_TIME = "1970-01-01T00:00:00Z"
RUNTIME_PRUNE_DIRS = {"documentation", "sources"}


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
    component.component_type = "application/x-fmu-sharedlibrary"
    component.implementation = "ModelExchange"

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


def build_component(
    component_name: str,
    resource_name: str,
    fmu_path: Path,
    *,
    component_type: str | None = "application/x-fmu-sharedlibrary",
    implementation: str | None = "ModelExchange",
) -> Component:
    with FMU(fmu_path, mode="r") as fmu:
        model_description = fmu.model_description
    enumeration_type_names = read_enumeration_type_names(fmu_path)

    component = Component()
    component.name = component_name
    component.source = f"resources/{resource_name}"
    component.component_type = component_type
    component.implementation = implementation

    for connector_kind, variables in (
        ("parameter", model_description.parameters),
        ("input", model_description.inputs),
        ("output", model_description.outputs),
    ):
        for variable in variables:
            component.connectors.append(
                Connector(
                    name=variable.name,
                    kind=connector_kind,
                    type_=clone_variable_type(variable, enumeration_type_names),
                )
            )

    return component


def add_component_to_system(
    system: System,
    component_name: str,
    resource_name: str,
    fmu_path: Path,
    *,
    component_type: str | None = "application/x-fmu-sharedlibrary",
    implementation: str | None = "ModelExchange",
) -> Component:
    component = build_component(
        component_name,
        resource_name,
        fmu_path,
        component_type=component_type,
        implementation=implementation,
    )
    system.elements.append(component)
    return component


def set_component_parameter_values(component: Component, values: dict[str, float | int | bool | str]) -> None:
    parameter_bindings = LET.Element(QName(Component.namespaces["ssd"], "ParameterBindings"))
    parameter_binding = LET.SubElement(parameter_bindings, QName(Component.namespaces["ssd"], "ParameterBinding"))
    parameter_values = LET.SubElement(parameter_binding, QName(Component.namespaces["ssd"], "ParameterValues"))
    parameter_set = LET.SubElement(
        parameter_values,
        QName(Component.namespaces["ssv"], "ParameterSet"),
        attrib={"version": "1.0", "name": f"{component.name}_parameters"},
        nsmap={key: Component.namespaces[key] for key in ("ssv", "ssc")},
    )
    parameters = LET.SubElement(parameter_set, QName(Component.namespaces["ssv"], "Parameters"))

    for parameter_name, value in values.items():
        parameter = LET.SubElement(parameters, QName(Component.namespaces["ssv"], "Parameter"), attrib={"name": parameter_name})
        if isinstance(value, bool):
            parameter_type = "Boolean"
            serialized_value = "true" if value else "false"
        elif isinstance(value, int) and not isinstance(value, bool):
            parameter_type = "Integer"
            serialized_value = str(value)
        elif isinstance(value, float):
            parameter_type = "Real"
            serialized_value = str(value)
        else:
            parameter_type = "String"
            serialized_value = str(value)

        LET.SubElement(
            parameter,
            QName(Component.namespaces["ssv"], parameter_type),
            attrib={"value": serialized_value},
        )

    component.parameter_bindings = parameter_bindings


@contextmanager
def materialize_fmu_archive(source_path: Path, archive_name: str):
    if source_path.is_file():
        yield source_path
        return

    with tempfile.TemporaryDirectory() as temp_dir:
        archive_path = Path(temp_dir) / archive_name
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(source_path.rglob("*")):
                if path.is_dir():
                    continue
                archive.write(path, arcname=path.relative_to(source_path))
        yield archive_path


def package_ssp(
    output_path: Path,
    system_name: str,
    build_system,
    *,
    start_time: float | None = None,
    stop_time: float | None = None,
    resource_files: dict[str, Path] | None = None,
    resource_directories: dict[str, Path] | None = None,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()

    resource_files = resource_files or {}
    resource_directories = resource_directories or {}

    with SSP(output_path, mode="w") as ssp:
        for resource_name, resource_path in resource_files.items():
            resource_target = Path("resources") / resource_name
            ssp.add_file(resource_path, str(resource_target.parent))
            if resource_path.name != resource_name:
                ssp.get_file_temp_path(resource_target.parent / resource_path.name).replace(
                    ssp.get_file_temp_path(resource_target)
                )

        for resource_dir, source_dir in resource_directories.items():
            for path in sorted(source_dir.rglob("*")):
                if path.is_dir():
                    continue
                archive_parent = Path("resources") / resource_dir / path.relative_to(source_dir).parent
                ssp.add_file(path, str(archive_parent))

        with ssp.system_structure as ssd:
            ssd.name = system_name
            ssd.version = "1.0"
            ssd.top_level_metadata.generationDateAndTime = FIXED_GENERATION_DATE_AND_TIME
            system = System(name=system_name)
            build_system(system)
            ssd.system = system
            if start_time is not None and stop_time is not None:
                experiment = DefaultExperiment()
                experiment.start_time = start_time
                experiment.stop_time = stop_time
                ssd.default_experiment = experiment


def package_directory_as_archive(source_dir: Path, archive_path: Path) -> None:
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    if archive_path.exists():
        archive_path.unlink()
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source_dir.rglob("*")):
            if path.is_dir():
                continue
            archive.write(path, path.relative_to(source_dir).as_posix())


def prune_runtime_irrelevant_dirs(root: Path) -> None:
    for path in sorted(root.rglob("*")):
        if path.is_dir() and path.name in RUNTIME_PRUNE_DIRS:
            for child in sorted(path.rglob("*"), reverse=True):
                if child.is_file():
                    child.unlink()
                elif child.is_dir():
                    child.rmdir()
            path.rmdir()


def unpack_archive_to_runtime_layout(archive_path: Path, output_dir: Path) -> None:
    if output_dir.exists():
        for child in sorted(output_dir.rglob("*"), reverse=True):
            if child.is_file():
                child.unlink()
            elif child.is_dir():
                child.rmdir()
        output_dir.rmdir()

    output_dir.mkdir(parents=True, exist_ok=False)
    with zipfile.ZipFile(archive_path, "r") as archive:
        archive.extractall(output_dir)

    for fmu_archive in sorted(output_dir.rglob("*.fmu")):
        if not fmu_archive.is_file():
            continue
        temp_dir = fmu_archive.parent / f"{fmu_archive.name}.tmp"
        temp_dir.mkdir(parents=True, exist_ok=False)
        with zipfile.ZipFile(fmu_archive, "r") as archive:
            archive.extractall(temp_dir)
        prune_runtime_irrelevant_dirs(temp_dir)
        fmu_archive.unlink()
        temp_dir.rename(fmu_archive.with_suffix(""))


def package_fmu_as_ssp(
    fmu_path: Path,
    output_path: Path,
    system_name: str,
    component_name: str,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()

    with SSP(output_path, mode="w") as ssp:
        ssp.add_resource(fmu_path)
        with ssp.system_structure as ssd:
            ssd.name = system_name
            ssd.version = "1.0"
            # Keep generated SSP metadata stable across repeated workflow runs.
            ssd.top_level_metadata.generationDateAndTime = FIXED_GENERATION_DATE_AND_TIME
            build_ssd(
                ssd=ssd,
                component_name=component_name,
                resource_name=fmu_path.name,
                fmu_path=fmu_path,
            )


def infer_fmu_model_name(fmu_path: Path) -> str:
    with FMU(fmu_path, mode="r") as fmu:
        return fmu.model_description.model_name or fmu_path.stem
