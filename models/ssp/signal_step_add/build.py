#!/usr/bin/env python3

from __future__ import annotations

import os
import sys
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(os.environ.get("SSP_REFERENCES_REPO_ROOT", Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "3rd_party" / "pyssp_standard"))

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

    step_a_path = model.paths.fmus_dir / "StepA.fmu"
    step_b_path = model.paths.fmus_dir / "StepB.fmu"
    add_path = model.paths.fmus_dir / "Add.fmu"
    package_archive(model.paths.shared_fmu_dir("Modelica.Blocks.Sources.Step"), step_a_path)
    package_archive(model.paths.shared_fmu_dir("Modelica.Blocks.Sources.Step"), step_b_path)
    package_archive(model.paths.shared_fmu_dir("Modelica.Blocks.Math.Add"), add_path)

    with SSP(output_path, mode="w") as ssp:
        with ssp.system_structure() as ssd:
            ssd.xml.default_experiment = DefaultExperiment(start_time=0.0, stop_time=1.0)

        ssp.add_fmu("step_a", step_a_path, resource_name="StepA.fmu", implementation="CoSimulation")
        ssp.add_fmu("step_b", step_b_path, resource_name="StepB.fmu", implementation="CoSimulation")
        ssp.add_fmu("add", add_path, resource_name="Add.fmu", implementation="CoSimulation")

        with ssp.system_structure() as ssd:
            ssd.extend_system_parameterset(
                {
                    "step_a.height": 1.5,
                    "step_a.offset": 0.5,
                    "step_a.startTime": 0.25,
                    "step_b.height": -0.5,
                    "step_b.offset": 1.0,
                    "step_b.startTime": 0.5,
                    "add.k1": 1.0,
                    "add.k2": 1.0,
                }
            )

            system = ssd.xml.system
            system.connections.extend(
                [
                    Connection(start_element="step_a", start_connector="y", end_element="add", end_connector="u1"),
                    Connection(start_element="step_b", start_connector="y", end_element="add", end_connector="u2"),
                    Connection(start_element="step_a", start_connector="y", end_connector="step_a_y"),
                    Connection(start_element="step_b", start_connector="y", end_connector="step_b_y"),
                    Connection(start_element="add", start_connector="y", end_connector="sum_y"),
                ]
            )

    unpack_archive(model.paths.ssp_path, model.paths.unpacked_ssp_dir, recursive_fmus=True, overwrite=True)
    print(f"Built {model.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
