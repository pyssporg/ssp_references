from __future__ import annotations

from pathlib import Path

from package_fmu_as_ssp import package_fmu
from unpack_model_archive import unpack_archive

from .filesystem import remove_path, zip_directory


def build_fmu_from_directory(source_dir: Path, fmu_path: Path) -> None:
    zip_directory(source_dir, fmu_path)


def package_ssp_from_directory(source_dir: Path, ssp_path: Path) -> None:
    zip_directory(source_dir, ssp_path)


def package_single_fmu_as_ssp(
    fmu_path: Path,
    ssp_path: Path,
    system_name: str,
    component_name: str,
) -> None:
    package_fmu(
        fmu_path=fmu_path,
        output_path=ssp_path,
        system_name=system_name,
        component_name=component_name,
    )


def unpack_archive_to_runtime_layout(archive_path: Path, output_dir: Path) -> None:
    remove_path(output_dir)
    unpack_archive(
        archive_path=archive_path,
        output_dir=output_dir,
        prune=True,
        recursive_fmus=True,
    )
