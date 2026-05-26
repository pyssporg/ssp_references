#!/usr/bin/env python3

from __future__ import annotations

import sys
import tempfile
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "3rd_party" / "pyssp_standard"))

from pyssp_standard import LSRefExperiments, SSP
from pyssp_standard.common.archive import unpack_archive
from pyssp_standard.standard.ls_ref.model import LSRefExperiment
from utils.fmu import strip_model_exchange
from utils.model import ModelMetaData


def create_ssp(model: ModelMetaData, temp_dir: Path, exp: LSRefExperiment) -> None:
    ssp_path = temp_dir / "model.ssp"
    ssp_path.unlink(missing_ok=True)

    with SSP(ssp_path, mode="a") as ssp:
        copied_resource_name = ssp.add_fmu(
            "fmu",
            model.paths.shared_fmu_dir("BouncingBall"),
            resource_name="BouncingBall.fmu",
            implementation="CoSimulation",
        )
        strip_model_exchange(ssp.runtime.resolve(f"resources/{copied_resource_name}"))
        for resource in [*exp.stimuli, *exp.references]:
            ssp.add_resource(MODEL_DIR / resource.source)
            if resource.mapping is not None:
                ssp.add_resource(MODEL_DIR / resource.mapping)

        with ssp.ls_ref_experiments() as experiments:
            experiments.add_experiment(exp)

    unpack_archive(ssp_path, model.paths.build_dir / exp.name, recursive_fmus=True, overwrite=True)


EXPERIMENTS_PATH = MODEL_DIR / "experiments.xml"


def main() -> int:
    model = ModelMetaData(MODEL_DIR)
    model.reset_build_dir()

    LSRefExperiments.check_document_compliance(EXPERIMENTS_PATH)

    with tempfile.TemporaryDirectory(prefix="bouncingball_") as temp_dir:
        with LSRefExperiments(EXPERIMENTS_PATH) as experiments:
            for exp in experiments.xml.experiments:
                create_ssp(model, Path(temp_dir), exp)

    print(f"Built {model.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
