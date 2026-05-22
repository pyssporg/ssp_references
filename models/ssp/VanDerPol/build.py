# !/usr/bin/env python3

from __future__ import annotations

import tempfile
from pathlib import Path
import sys

from pyssp_standard import LSRefExperiments, SSP, get_repo_root
from pyssp_standard.common.archive import package_archive, unpack_archive
from pyssp_standard.fmu import FMU
from pyssp_standard.standard.ls_ref.model import (
    LSRefExperiment,
    LSRefExperimentResource,
)

MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = get_repo_root(file="__SSP_REF_ROOT__")
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "3rd_party" / "pyssp_standard"))

from utils.model import ModelMetaData


def create_ssp(model: ModelMetaData, temp_dir, exp: LSRefExperiment):
    fmu_path = temp_dir / "model.fmu"
    ssp_path = temp_dir / "model.ssp"
    package_archive(model.paths.shared_fmu_dir("VanDerPol"), fmu_path)

    with FMU(fmu_path, mode="a") as fmu:
        with fmu.model_description as md:
            md.strip_model_exchange()

    build_dir = model.paths.build_dir / exp.name

    with FMU(fmu_path, mode="r") as fmu:
        fmu.package_as_ssp(
            ssp_path,
            system_name=model.name,
            component_name="fmu",
            implementation="CoSimulation",
        )

    with SSP(ssp_path, mode="a") as ssp:
        for parameters in exp.parameters:
            ssp.add_external_parameterset(
                MODEL_DIR / parameters.source, MODEL_DIR / parameters.mapping
            )

        for resource in [*exp.stimuli, *exp.references]: 
            ssp.add_resource(MODEL_DIR / resource.source)
            if resource.mapping is not None:
                ssp.add_resource(MODEL_DIR / resource.mapping)

        with ssp.ls_ref_experiments() as experiments:
            experiments.add_experiment(exp)

    unpack_archive(ssp_path, build_dir, recursive_fmus=True, overwrite=True)


EXPERIMENTS_PATH = MODEL_DIR / "experiments.xml"


def main() -> int:
    model = ModelMetaData(MODEL_DIR)
    model.reset_build_dir()

    LSRefExperiments.check_document_compliance(EXPERIMENTS_PATH)

    with tempfile.TemporaryDirectory(prefix="vanderpol_") as temp_dir:
        with LSRefExperiments(EXPERIMENTS_PATH) as experiments:
            for exp in experiments.xml.experiments:
                create_ssp(model, Path(temp_dir), exp)

    print(f"Built {model.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
