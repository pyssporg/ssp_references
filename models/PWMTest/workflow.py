#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = MODEL_DIR.parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from workflow_lib import copy_tree, model_paths, package_ssp_from_directory, unpack_archive_to_runtime_layout


MODEL_NAME = "PWMTest"
SOURCE_DIR = REPO_ROOT / "3rd_party" / "OMSimulator" / "testsuite" / "resources" / "pwmtest"
PATHS = model_paths(MODEL_DIR, MODEL_NAME)


def acquire() -> None:
    copy_tree(SOURCE_DIR, PATHS.unpacked_ssp_dir)


def build() -> None:
    return None


def package() -> None:
    package_ssp_from_directory(PATHS.unpacked_ssp_dir, PATHS.ssp_path)


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
