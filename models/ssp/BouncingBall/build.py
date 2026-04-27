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
from pyssp_standard.fmu import FMU
from workflow.model import ModelMetaData


def main() -> int:
    model = ModelMetaData(MODEL_DIR)
    model.paths.fmus_dir.mkdir(parents=True, exist_ok=True)
    for source_path in model.source_results:
        if not source_path.exists():
            raise FileNotFoundError(f"Source path not found: {source_path}")

    fmu_path = model.paths.fmus_dir / "BouncingBall.fmu"
    package_archive(model.paths.shared_fmu_dir("BouncingBall"), fmu_path)

    with FMU(fmu_path, mode="r") as fmu:
        fmu.package_as_ssp(model.paths.ssp_path, system_name=model.name, component_name="fmu", implementation="CoSimulation")

    unpack_archive(model.paths.ssp_path, model.paths.unpacked_ssp_dir, recursive_fmus=True, overwrite=True)
    print(f"Built {model.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
