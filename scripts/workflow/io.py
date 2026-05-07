from __future__ import annotations

import json
import os
from pathlib import Path

from utils.filesystem import ensure_parent


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def write_json(path: Path, data: dict) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def relative_path(base_dir: Path, path: Path) -> str:
    return Path(os.path.relpath(path, start=base_dir)).as_posix()


def resolve_path(base_dir: Path, value: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    return base_dir / candidate
