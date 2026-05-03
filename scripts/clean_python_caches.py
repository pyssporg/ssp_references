#!/usr/bin/env python3

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SKIP_DIRS = {"venv", ".venv"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Remove Python bytecode caches under the repository root."
    )
    parser.add_argument(
        "--include-venv",
        action="store_true",
        help="Also remove caches inside venv directories.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print paths that would be removed without deleting them.",
    )
    return parser.parse_args()


def iter_cache_paths(include_venv: bool) -> list[Path]:
    cache_paths: list[Path] = []
    skip_dirs = set() if include_venv else DEFAULT_SKIP_DIRS

    def is_skipped(path: Path) -> bool:
        relative_parts = path.relative_to(REPO_ROOT).parts
        return not include_venv and any(part in skip_dirs for part in relative_parts)

    for path in REPO_ROOT.rglob("__pycache__"):
        if not is_skipped(path):
            cache_paths.append(path)

    for suffix in (".pyc", ".pyo"):
        for path in REPO_ROOT.rglob(f"*{suffix}"):
            if is_skipped(path) or "__pycache__" in path.parts:
                continue
            cache_paths.append(path)

    cache_paths.sort(key=lambda item: (len(item.parts), str(item)))
    return cache_paths


def remove_cache_paths(cache_paths: list[Path], *, dry_run: bool) -> int:
    removed = 0
    for path in cache_paths:
        print(path.relative_to(REPO_ROOT))
        removed += 1
        if dry_run:
            continue
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
    return removed


def main() -> int:
    args = parse_args()
    cache_paths = iter_cache_paths(include_venv=args.include_venv)
    removed = remove_cache_paths(cache_paths, dry_run=args.dry_run)
    if args.dry_run:
        print(f"Would remove {removed} cache paths.")
    else:
        print(f"Removed {removed} cache paths.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
