from __future__ import annotations

import shutil
import zipfile
from pathlib import Path


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def reset_dir(path: Path) -> None:
    remove_path(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_tree(source: Path, target: Path) -> None:
    if not source.is_dir():
        raise FileNotFoundError(f"Source directory not found: {source}")
    remove_path(target)
    ensure_parent(target)
    shutil.copytree(source, target)


def copy_file(source: Path, target: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(f"Source file not found: {source}")
    ensure_parent(target)
    shutil.copy2(source, target)


def copy_source_results(model_dir: Path, result_paths: list[Path]) -> None:
    target_dir = model_dir / "references"
    remove_path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    for result_path in result_paths:
        copy_file(result_path, target_dir / result_path.name)


def zip_directory(source_dir: Path, archive_path: Path) -> None:
    if not source_dir.is_dir():
        raise FileNotFoundError(f"Directory not found: {source_dir}")
    remove_path(archive_path)
    ensure_parent(archive_path)
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source_dir.rglob("*")):
            if path.is_dir():
                continue
            archive.write(path, path.relative_to(source_dir).as_posix())
