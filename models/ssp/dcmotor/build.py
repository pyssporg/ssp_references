#!/usr/bin/env python3

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "3rd_party" / "pyssp_standard"))

from pyssp_standard import FMU, LSRefExperiments, SSP
from pyssp_standard.common.archive import package_archive, unpack_archive
from pyssp_standard.standard.ls_ref.model import LSRefExperiment
from pyssp_standard.standard.ssp1.codec.ssd_codec import Ssp1SsdCodec
from pyssp_standard.standard.ssp1.operations.ssd_flatten import flatten_ssd
from utils.model import ModelMetaData


def _strip_source_fmus(resources_dir: Path) -> None:
    for resource_name in ("edrive_mass", "emachine_model", "stimuli_model"):
        resource_dir = resources_dir / resource_name
        if not resource_dir.is_dir():
            raise FileNotFoundError(f"Missing FMU directory: {resource_dir}")
        with FMU(resource_dir, mode="a") as fmu:
            with fmu.model_description as model_description:
                model_description.strip_model_exchange()


def create_ssp(
    model: ModelMetaData,
    temp_dir: Path,
    exp: LSRefExperiment,
    *,
    flattened: bool = False,
) -> None:
    if not model.paths.source_ssp_dir.is_dir():
        raise FileNotFoundError(f"Local SSP directory not found: {model.paths.source_ssp_dir}")

    ssp_copy = temp_dir / "ssp"
    shutil.copytree(model.paths.source_ssp_dir, ssp_copy)
    _strip_source_fmus(ssp_copy / "resources")

    ssp_path = temp_dir / "model.ssp"
    package_archive(ssp_copy, ssp_path, nested_fmus=True)

    with SSP(ssp_path, mode="a") as ssp:
        for resource in [*exp.stimuli, *exp.references]:
            ssp.add_resource(MODEL_DIR / resource.source)
            if resource.mapping is not None:
                ssp.add_resource(MODEL_DIR / resource.mapping)

        with ssp.ls_ref_experiments() as experiments:
            experiments.add_experiment(exp)

        if flattened:
            with ssp.system_structure() as ssd:
                codec = Ssp1SsdCodec()
                flat = flatten_ssd(ssd.xml)
                flat.version = "1.0"
                ssd.from_xml(codec.serialize(flat))

    unpack_archive(ssp_path, model.paths.build_dir / exp.name, recursive_fmus=True, overwrite=True)


EXPERIMENTS_PATH = MODEL_DIR / "experiments.xml"


def main() -> int:
    model = ModelMetaData(MODEL_DIR)
    model.reset_build_dir()

    LSRefExperiments.check_document_compliance(EXPERIMENTS_PATH)

    with tempfile.TemporaryDirectory(prefix="dcmotor_") as temp_dir:
        with LSRefExperiments(EXPERIMENTS_PATH) as experiments:
            for exp in experiments.xml.experiments:
                create_ssp(model, Path(temp_dir), exp, flattened=True)

    print(f"Built {model.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
