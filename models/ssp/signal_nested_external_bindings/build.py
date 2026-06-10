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

from pyssp_standard import LSRefExperiments, SSP
from pyssp_standard.common.archive import package_archive, unpack_archive
from pyssp_standard.standard.ls_ref.model import LSRefExperiment
from utils.fmu import strip_model_exchange
from utils.model import ModelMetaData


def _copy_shared_fmus(resources_dir: Path, model: ModelMetaData) -> None:
    """Copy shared FMU stubs into the build SSP resources directory."""
    fmus = [
        ("Step", "Modelica.Blocks.Sources.Step"),
        ("Sine", "Modelica.Blocks.Sources.Sine"),
    ]
    for dir_name, lib_name in fmus:
        src = model.paths.shared_fmu_dir(lib_name)
        dst = resources_dir / dir_name
        dst.mkdir(parents=True, exist_ok=True)
        for item in src.iterdir():
            if item.is_dir():
                shutil.copytree(item, dst / item.name, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dst / item.name)
        strip_model_exchange(dst)


def _resolve_fixture_resource(relative_path: str, model_dir: Path) -> Path:
    root_path = model_dir / relative_path
    if root_path.exists():
        return root_path

    ssp_path = model_dir / "ssp" / relative_path
    if ssp_path.exists():
        return ssp_path

    raise FileNotFoundError(f"Missing fixture resource: {relative_path}")


def create_ssp(model: ModelMetaData, temp_dir: Path, exp: LSRefExperiment) -> None:
    if not model.paths.source_ssp_dir.is_dir():
        raise FileNotFoundError(f"Local SSP directory not found: {model.paths.source_ssp_dir}")

    ssp_copy = temp_dir / "ssp"
    shutil.copytree(model.paths.source_ssp_dir, ssp_copy)

    # Add shared FMUs at build time (not inlined in source)
    _copy_shared_fmus(ssp_copy / "resources", model)

    ssp_path = temp_dir / "model.ssp"
    ssp_path.unlink(missing_ok=True)
    package_archive(ssp_copy, ssp_path, recursive=True)

    with SSP(ssp_path, mode="a") as ssp:
        for resource in [*exp.stimuli, *exp.references]:
            ssp.add_resource(_resolve_fixture_resource(resource.source, MODEL_DIR))
            if resource.mapping is not None:
                ssp.add_resource(_resolve_fixture_resource(resource.mapping, MODEL_DIR))

        with ssp.ls_ref_experiments() as experiments:
            experiments.add_experiment(exp)

    unpack_archive(ssp_path, model.paths.build_dir / exp.name, recursive_fmus=True, overwrite=True)


EXPERIMENTS_PATH = MODEL_DIR / "experiments.xml"


def main() -> int:
    model = ModelMetaData(MODEL_DIR)
    model.reset_build_dir()

    LSRefExperiments.check_document_compliance(EXPERIMENTS_PATH)

    with tempfile.TemporaryDirectory(prefix="signal_nested_external_bindings_") as temp_dir:
        with LSRefExperiments(EXPERIMENTS_PATH) as experiments:
            for exp in experiments.xml.experiments:
                create_ssp(model, Path(temp_dir), exp)

    print(f"Built {model.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
