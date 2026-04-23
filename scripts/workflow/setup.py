from __future__ import annotations

from pathlib import Path
from typing import Callable

from .archive import (
    build_fmu_from_directory,
    package_ssp_from_directory,
    unpack_archive_to_runtime_layout,
)
from .filesystem import copy_file, copy_source_results, copy_tree
from .model import ModelMetaData, require_single_source
from .packaging import materialize_fmu_archive, package_fmu_as_ssp
from .results import unpack_mat_results_in_directory

SSPBuilder = Callable[[ModelMetaData], None]


def acquire(model: ModelMetaData) -> None:
    for source_path in model.source_ssp + model.source_fmu + model.source_results:
        if not source_path.exists():
            raise FileNotFoundError(f"Source path not found: {source_path}")


def build(model: ModelMetaData) -> None:
    if not model.source_fmu:
        return
    source_path = require_single_source(model.source_fmu, "fmu")
    if source_path.is_dir():
        build_fmu_from_directory(source_path, model.paths.fmu_path())
        return
    if source_path.is_file() and source_path.suffix == ".fmu":
        copy_file(source_path, model.paths.fmu_path())
        return
    raise ValueError(f"Unsupported FMU source: {source_path}")


def package(model: ModelMetaData) -> None:
    if model.source_fmu:
        built_fmu_path = model.paths.fmu_path()
        if built_fmu_path.is_file():
            package_fmu_as_ssp(
                fmu_path=built_fmu_path,
                output_path=model.paths.ssp_path,
                system_name=model.name,
                component_name=model.name,
            )
            return

        source_path = require_single_source(model.source_fmu, "fmu")
        archive_name = f"{model.name}.fmu"
        with materialize_fmu_archive(source_path, archive_name) as fmu_path:
            package_fmu_as_ssp(
                fmu_path=fmu_path,
                output_path=model.paths.ssp_path,
                system_name=model.name,
                component_name=model.name,
            )
        return

    source_path = require_single_source(model.source_ssp, "ssp")
    if source_path.is_dir():
        copy_tree(source_path, model.paths.unpacked_ssp_dir)
        package_ssp_from_directory(model.paths.unpacked_ssp_dir, model.paths.ssp_path)
        return
    if source_path.is_file() and source_path.suffix == ".ssp":
        copy_file(source_path, model.paths.ssp_path)
        return
    raise ValueError(f"Unsupported SSP source: {source_path}")


def build_ssp_from_shared_fmu(
    model: ModelMetaData,
    *,
    fmu_model_name: str | None = None,
    component_name: str | None = None,
) -> None:
    actual_fmu_model_name = fmu_model_name or model.name
    fmu_source_dir = model.paths.shared_fmu_dir(actual_fmu_model_name)
    if not fmu_source_dir.is_dir():
        raise FileNotFoundError(f"Shared FMU directory not found: {fmu_source_dir}")

    resource_name = f"{actual_fmu_model_name}.fmu"
    with materialize_fmu_archive(fmu_source_dir, resource_name) as fmu_path:
        package_fmu_as_ssp(
            fmu_path=fmu_path,
            output_path=model.paths.ssp_path,
            system_name=model.name,
            component_name=component_name or model.name,
        )


def build_ssp_from_local_resources(model: ModelMetaData) -> None:
    local_ssp_dir = model.paths.unpacked_ssp_dir
    if not local_ssp_dir.is_dir():
        raise FileNotFoundError(f"Local SSP directory not found: {local_ssp_dir}")
    package_ssp_from_directory(local_ssp_dir, model.paths.ssp_path)


def unpack(model: ModelMetaData) -> None:
    unpack_archive_to_runtime_layout(model.paths.ssp_path, model.paths.unpacked_ssp_dir)


def copy_results(model: ModelMetaData) -> None:
    if not model.source_results:
        return
    copy_source_results(model.dir, model.source_results)
    unpack_mat_results_in_directory(model.paths.references_dir)


def setup_directory(model_dir: Path, *, ssp_builder: SSPBuilder | None = None) -> None:
    print(f"Setup of {model_dir} starting")

    model = ModelMetaData(model_dir)

    acquire(model)
    if ssp_builder is None:
        build(model)
        package(model)
    else:
        ssp_builder(model)
    unpack(model)
    copy_results(model)
    print(f"Setup of {model.name} complete")
