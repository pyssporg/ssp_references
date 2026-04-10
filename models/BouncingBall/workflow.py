#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = MODEL_DIR.parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from workflow_lib import build_fmu_from_directory, model_paths, package_single_fmu_as_ssp, unpack_archive_to_runtime_layout


MODEL_NAME = "BouncingBall"
SOURCE_DIR = REPO_ROOT / "3rd_party" / "OMSimulator" / "testsuite" / "resources" / MODEL_NAME
PATHS = model_paths(MODEL_DIR, MODEL_NAME)


def acquire() -> None:
    if not SOURCE_DIR.is_dir():
        raise FileNotFoundError(f"Source directory not found: {SOURCE_DIR}")


def build() -> None:
    build_fmu_from_directory(SOURCE_DIR, PATHS.fmu_path())


def package() -> None:
    package_single_fmu_as_ssp(
        fmu_path=PATHS.fmu_path(),
        ssp_path=PATHS.ssp_path,
        system_name=MODEL_NAME,
        component_name=MODEL_NAME,
    )


def unpack() -> None:
    unpack_archive_to_runtime_layout(PATHS.ssp_path, PATHS.unpacked_ssp_dir)


def main() -> int:
    acquire()
    build()
    package()
    unpack()
    print(f"Populated {MODEL_NAME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
