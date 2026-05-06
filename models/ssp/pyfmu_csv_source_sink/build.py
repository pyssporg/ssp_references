#!/usr/bin/env python3

from __future__ import annotations

import sys
import tempfile
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "3rd_party" / "pyssp_standard"))
sys.path.insert(0, str(REPO_ROOT / "3rd_party" / "pyfmu_csv" / "python"))

from pyfmu_csv.packaging import package_fmu_from_csv
from pyssp_standard import LSRefExperiments, SSP
from pyssp_standard.common.archive import package_archive, unpack_archive
from pyssp_standard.standard.ls_ref.model import LSRefExperiment
from pyssp_standard.ssd import Connection, DefaultExperiment
from utils.model import ModelMetaData


def create_ssp(model: ModelMetaData, temp_dir: Path, exp: LSRefExperiment) -> None:
    source_csv = MODEL_DIR / "input" / "signals.csv"
    source_fmu = temp_dir / "CsvSource.fmu"
    sink_fmu = temp_dir / "Gain.fmu"
    ssp_path = temp_dir / "model.ssp"

    package_fmu_from_csv(source_csv, source_fmu, "CsvSource")
    package_archive(model.paths.shared_fmu_dir("Modelica.Blocks.Math.Gain"), sink_fmu)

    with SSP(ssp_path, mode="w") as ssp:
        with ssp.system_structure() as ssd:
            ssd.xml.default_experiment = DefaultExperiment(start_time=0.0, stop_time=1.0)

        ssp.add_fmu("source", source_fmu, resource_name="CsvSource.fmu", implementation="CoSimulation")
        ssp.add_fmu("sink", sink_fmu, resource_name="Gain.fmu", implementation="CoSimulation")

        with ssp.system_structure() as ssd:
            ssd.extend_system_parameterset({"sink.k": 1.0})
            system = ssd.xml.system
            if system is None:
                raise RuntimeError("SystemStructure.ssd did not contain a system")
            system.connections.append(
                Connection(start_element="source", start_connector="y", end_element="sink", end_connector="u")
            )

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

    with tempfile.TemporaryDirectory(prefix="pyfmu_csv_source_sink_") as temp_dir:
        with LSRefExperiments(EXPERIMENTS_PATH) as experiments:
            for exp in experiments.xml.experiments:
                create_ssp(model, Path(temp_dir), exp)

    print(f"Built {model.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
