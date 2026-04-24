from __future__ import annotations

import tempfile
import zipfile
from contextlib import contextmanager
from pathlib import Path

from pyssp_standard import FMU, SSP
from pyssp_standard.ssd import Component, Connector, DefaultExperiment, System
from pyssp_standard.standard.ssp1.model.ssc_model import Ssp1DocumentMetadata
from pyssp_standard.standard.ssp1.model.ssd_model import Ssd1ParameterBinding
from pyssp_standard.standard.ssp1.model.ssv_model import Ssp1Parameter, Ssp1ParameterSet

FIXED_GENERATION_DATE_AND_TIME = "1970-01-01T00:00:00Z"
RUNTIME_PRUNE_DIRS = {"documentation", "sources"}


def build_component(
    component_name: str,
    resource_name: str,
    fmu_path: Path,
    *,
    component_type: str | None = "application/x-fmu-sharedlibrary",
    implementation: str | None = "ModelExchange",
) -> Component:
    with FMU(fmu_path, mode="r") as fmu:
        with fmu.model_description as md:
            variables = list(md.xml.parameters) + list(md.xml.inputs) + list(md.xml.outputs)

    component = Component(
        name=component_name,
        source=f"resources/{resource_name}",
        component_type=component_type,
        implementation=implementation,
    )

    for variable in variables:
        type_attributes = dict(variable.type_attributes)
        if variable.declared_type is not None:
            type_attributes["declaredType"] = variable.declared_type
        if variable.start is not None:
            type_attributes["start"] = variable.start
        component.connectors.append(
            Connector(
                name=variable.name,
                kind=variable.causality or "",
                type_name=variable.type_name,
                type_attributes=type_attributes,
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
    parameter_set = Ssp1ParameterSet(
        name=f"{component.name}_parameters",
        version="1.0",
        metadata=Ssp1DocumentMetadata(),
    )

    for parameter_name, value in values.items():
        if isinstance(value, bool):
            type_name = "Boolean"
            attributes = {"value": "true" if value else "false"}
        elif isinstance(value, int) and not isinstance(value, bool):
            type_name = "Integer"
            attributes = {"value": str(value)}
        elif isinstance(value, float):
            type_name = "Real"
            attributes = {"value": str(value)}
        else:
            type_name = "String"
            attributes = {"value": str(value)}

        parameter_set.parameters.append(
            Ssp1Parameter(
                name=parameter_name,
                type_name=type_name,
                attributes=attributes,
            )
        )

    component.parameter_bindings.append(Ssd1ParameterBinding(parameter_set=parameter_set))


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

    with SSP(output_path, mode="w") as ssp:
        for resource_name, resource_path in (resource_files or {}).items():
            ssp.runtime.add_file(resource_path, target_name=str(Path("resources") / resource_name))

        for resource_dir, source_dir in (resource_directories or {}).items():
            for path in sorted(source_dir.rglob("*")):
                if path.is_dir():
                    continue
                target_name = Path("resources") / resource_dir / path.relative_to(source_dir)
                ssp.runtime.add_file(path, target_name=str(target_name))

        with ssp.system_structure() as ssd:
            ssd.xml.name = system_name
            ssd.xml.version = "1.0"
            ssd.xml.metadata.generation_date_and_time = FIXED_GENERATION_DATE_AND_TIME
            system = System(name=system_name)
            build_system(system)
            ssd.xml.system = system
            if start_time is not None and stop_time is not None:
                ssd.xml.default_experiment = DefaultExperiment(
                    start_time=start_time,
                    stop_time=stop_time,
                )


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
        for path in sorted(temp_dir.rglob("*")):
            if path.is_dir() and path.name in RUNTIME_PRUNE_DIRS:
                for child in sorted(path.rglob("*"), reverse=True):
                    if child.is_file():
                        child.unlink()
                    elif child.is_dir():
                        child.rmdir()
                path.rmdir()
        fmu_archive.unlink()
        temp_dir.rename(fmu_archive.with_suffix(""))
