from __future__ import annotations

import shutil
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
