#!/usr/bin/env python3

from __future__ import annotations

import os
import sys
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(os.environ.get("SSP_REFERENCES_REPO_ROOT", Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "3rd_party" / "pyssp_standard"))

from pyssp_standard.common.archive import package_archive, unpack_archive
from utils.model import ModelMetaData


def main() -> int:
    model = ModelMetaData(MODEL_DIR)
    if not model.paths.source_ssp_dir.is_dir():
        raise FileNotFoundError(f"Local SSP directory not found: {model.paths.source_ssp_dir}")

    package_archive(model.paths.source_ssp_dir, model.paths.ssp_path, nested_fmus=True)
    unpack_archive(model.paths.ssp_path, model.paths.unpacked_ssp_dir, recursive_fmus=True, overwrite=True)
    print(f"Built {model.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
