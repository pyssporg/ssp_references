from __future__ import annotations

import os
from pathlib import Path


REPO_ROOT_ENV_VAR = "SSP_REFERENCES_REPO_ROOT"


def is_repo_root(path: Path) -> bool:
    return (
        (path / ".git").exists()
        and (path / "models").is_dir()
    )


def get_repo_root() -> Path:
    env_value = os.environ.get(REPO_ROOT_ENV_VAR)
    if env_value:
        return Path(env_value)

    script_path = Path(__file__).resolve()
    for candidate in [script_path.parent, *script_path.parents]:
        if is_repo_root(candidate):
            return candidate

    raise RuntimeError(f"Unable to determine repository root from {script_path}")


REPO_ROOT = get_repo_root()
MODELS_DIR = REPO_ROOT / "models"
