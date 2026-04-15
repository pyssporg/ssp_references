from __future__ import annotations

import shutil
import zipfile
from pathlib import Path


RUNTIME_PRUNE_DIRS = {
    "documentation",
    "sources",
}


def default_output_dir(archive_path: Path) -> Path:
    return archive_path.parent / archive_path.stem


def prune_runtime_irrelevant_dirs(root: Path) -> None:
    for path in sorted(root.rglob("*")):
        if not path.is_dir():
            continue
        if path.name in RUNTIME_PRUNE_DIRS:
            shutil.rmtree(path)


def unpack_zip(archive_path: Path, output_dir: Path) -> None:
    with zipfile.ZipFile(archive_path, "r") as archive:
        archive.extractall(output_dir)


def unpack_fmu_dir(fmu_archive: Path, output_dir: Path, prune: bool) -> None:
    unpack_zip(fmu_archive, output_dir)
    if prune:
        prune_runtime_irrelevant_dirs(output_dir)


def unpack_nested_fmus(ssp_root: Path, prune: bool) -> None:
    for fmu_archive in sorted(ssp_root.rglob("*.fmu")):
        if not fmu_archive.is_file():
            continue
        unpack_dir = fmu_archive
        temp_unpack_dir = fmu_archive.parent / f"{fmu_archive.name}.tmp-unpack"
        unpack_fmu_dir(fmu_archive, temp_unpack_dir, prune=prune)
        fmu_archive.unlink()
        temp_unpack_dir.rename(unpack_dir.parent / unpack_dir.stem)


def unpack_archive(
    archive_path: Path,
    output_dir: Path,
    prune: bool,
    recursive_fmus: bool,
) -> None:
    suffix = archive_path.suffix.lower()
    if suffix not in {".fmu", ".ssp"}:
        raise ValueError(f"Expected a .fmu or .ssp archive, got: {archive_path.name}")

    if output_dir.exists():
        raise FileExistsError(f"Output path already exists: {output_dir}")

    output_dir.mkdir(parents=True, exist_ok=False)

    if suffix == ".fmu":
        unpack_fmu_dir(archive_path, output_dir, prune=prune)
        return

    unpack_zip(archive_path, output_dir)
    if recursive_fmus:
        unpack_nested_fmus(output_dir, prune=prune)
