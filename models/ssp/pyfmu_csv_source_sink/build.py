#!/usr/bin/env python3
"""Build pyfmu_csv_source_sink and its baseline study.

The SysML authors the composition, the ``System`` scenario, and the baseline
experiment. The CsvSource FMU is generated from ``input/signals.csv`` and
attached to the exported SSP.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from pyfmu_csv.packaging import package_fmu_from_csv
from pyssp_standard import SSP

from utils.authoring import build_model, build_study
from utils.model import ModelMetaData

MODEL_NAME = "pyfmu_csv_source_sink"
MODEL_COMPOSITION = "System"
STUDY_COMPOSITION = "baseline"
SOURCE_CSV = MODEL_DIR / "input" / "signals.csv"


def _attach_source_fmu(model_build_dir: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="pyfmu_csv_source_sink_") as temp_dir:
        fmu_path = Path(temp_dir) / "CsvSource.fmu"
        package_fmu_from_csv(SOURCE_CSV, fmu_path, "CsvSource")
        with SSP(model_build_dir, mode="a") as ssp:
            ssp.attach_fmu("source", fmu_path)


def main() -> int:
    model = ModelMetaData(MODEL_DIR)
    model.reset_build_dir()

    study_dir = REPO_ROOT / "artifacts" / "studies" / MODEL_NAME / STUDY_COMPOSITION
    model_build_dir = model.paths.build_dir / STUDY_COMPOSITION / "model"

    build_study(
        MODEL_DIR / "architecture",
        study_dir,
        STUDY_COMPOSITION,
        MODEL_NAME,
    )
    build_model(
        MODEL_DIR / "architecture",
        model_build_dir,
        MODEL_COMPOSITION,
        REPO_ROOT,
    )
    _attach_source_fmu(model_build_dir)

    print(f"Built {MODEL_NAME}: {model_build_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
