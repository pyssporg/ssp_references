#!/usr/bin/env python3

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(os.environ.get("SSP_REFERENCES_REPO_ROOT", Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "3rd_party" / "pyssp_standard"))
sys.path.insert(0, str(REPO_ROOT / "3rd_party" / "pyfmu_csv" / "python"))

from pyfmu_csv.packaging import package_fmu_from_csv
from pyssp_standard import SSP
from pyssp_standard.common.archive import package_archive, unpack_archive
from pyssp_standard.ssd import Connection, DefaultExperiment
from workflow.model import ModelMetaData


def main() -> int:
    model = ModelMetaData(MODEL_DIR)
    output_path = model.paths.ssp_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    model.paths.fmus_dir.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()

    source_csv = MODEL_DIR / "input" / "signals.csv"
    source_fmu = model.paths.fmu_path("CsvSource")
    sink_fmu = model.paths.fmu_path("Gain")

    package_fmu_from_csv(source_csv, source_fmu, "CsvSource")
    package_archive(model.paths.shared_fmu_dir("Modelica.Blocks.Math.Gain"), sink_fmu)

    with SSP(output_path, mode="w") as ssp:
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

    unpack_archive(model.paths.ssp_path, model.paths.unpacked_ssp_dir, recursive_fmus=True, overwrite=True)
    shutil.copy2(source_csv, output_path.parent / "signals.csv")
    print(f"Built {model.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
