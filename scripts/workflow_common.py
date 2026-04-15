#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path



REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from workflow_lib import (
    build_fmu_from_directory,
    copy_file,
    copy_source_results,
    copy_tree,
    package_single_fmu_as_ssp,
    package_ssp_from_directory,
    require_single_source,
    unpack_archive_to_runtime_layout,
    ModelMetaData
)





def acquire(model : ModelMetaData) -> None:
    for source_path in model.source_ssp + model.source_fmu + model.source_results:
        if not source_path.exists():
            raise FileNotFoundError(f"Source path not found: {source_path}")


def build(model : ModelMetaData) -> None:
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


def package(model : ModelMetaData) -> None:
    if model.source_fmu:
        package_single_fmu_as_ssp(
            fmu_path=model.paths.fmu_path(),
            ssp_path=model.paths.ssp_path,
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


def unpack(model : ModelMetaData) -> None:
    unpack_archive_to_runtime_layout(model.paths.ssp_path, model.paths.unpacked_ssp_dir)


def copy_results(model : ModelMetaData) -> None:
    if not model.source_results:
        return
    copy_source_results(model.dir, model.source_results)


def setup_directory(model_dir: Path) -> None:

    print(f"Setup of {model_dir} starting")

    model = ModelMetaData(model_dir)

    acquire(model)
    build(model)
    package(model)
    unpack(model)
    copy_results(model)
    print(f"Setup of {model.name} complete")

