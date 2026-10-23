#!/usr/bin/env python3
"""Build pyfmu_csv_source_sink and its baseline study.

The SysML authors the composition. The CsvSource FMU is generated from
``input/signals.csv``, so the SSP is exported as a design structure first and
populated with that FMU before the artifact is unpacked.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from pyfmu_csv.packaging import package_fmu_from_csv
from pyssp_standard import LSRefExperiments, SSP

from utils.authoring import build_model
from utils.model import ModelMetaData

MODEL_NAME = "pyfmu_csv_source_sink"
MODEL_COMPOSITION = "System"
SOURCE_CSV = MODEL_DIR / "input" / "signals.csv"
EXPERIMENTS_PATH = MODEL_DIR / "experiments.xml"


def _populate_source_fmu(archive: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="pyfmu_csv_source_sink_") as temp_dir:
        fmu_path = Path(temp_dir) / "CsvSource.fmu"
        package_fmu_from_csv(SOURCE_CSV, fmu_path, "CsvSource")
        with SSP(archive, mode="a") as ssp:
            ssp.attach_fmu("source", fmu_path)


def _package(model_build_dir: Path) -> None:
    with SSP(model_build_dir, mode="a") as ssp:
        with ssp.system_structure() as ssd:
            ssd.extend_system_parameterset({"sink.k": 1.0})
        with LSRefExperiments(EXPERIMENTS_PATH, mode="r") as source:
            with ssp.ls_ref_experiments() as experiments:
                for experiment in source.xml.experiments:
                    experiments.add_experiment(experiment)


def main() -> int:
    model = ModelMetaData(MODEL_DIR)
    model.reset_build_dir()

    LSRefExperiments.check_document_compliance(EXPERIMENTS_PATH)
    model_build_dir = model.paths.build_dir / "baseline"

    build_model(
        MODEL_DIR / "architecture",
        model_build_dir,
        MODEL_COMPOSITION,
        REPO_ROOT,
        allow_missing_fmus=True,
        populate=_populate_source_fmu,
    )
    _package(model_build_dir)

    print(f"Built {model.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
