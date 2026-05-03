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
from pyssp_standard.ssd import Connection, Connector, DefaultExperiment, System
from utils.model import FIXED_GENERATION_DATE_AND_TIME, ModelMetaData


def main() -> int:
    model = ModelMetaData(MODEL_DIR)
    output_path = model.paths.ssp_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    model.paths.fmus_dir.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()

    step_path = model.paths.fmus_dir / "Step.fmu"
    gain_a_path = model.paths.fmus_dir / "GainA.fmu"
    gain_b_path = model.paths.fmus_dir / "GainB.fmu"
    package_archive(model.paths.shared_fmu_dir("Modelica.Blocks.Sources.Step"), step_path)
    package_archive(model.paths.shared_fmu_dir("Modelica.Blocks.Math.Gain"), gain_a_path)
    package_archive(model.paths.shared_fmu_dir("Modelica.Blocks.Math.Gain"), gain_b_path)
    with SSP(output_path, mode="w") as ssp:
        with ssp.system_structure() as ssd:
            ssd.xml.default_experiment = DefaultExperiment(start_time=0.0, stop_time=1.0)

        ssp.add_fmu("step", step_path, resource_name="Step.fmu", implementation="CoSimulation")
        ssp.add_fmu("gain_a", gain_a_path, resource_name="GainA.fmu", implementation="CoSimulation")
        ssp.add_fmu("gain_b", gain_b_path, resource_name="GainB.fmu", implementation="CoSimulation")

        with ssp.system_structure() as ssd:
            ssd.extend_system_parameterset(
                {
                    "step.height": 2.0,
                    "step.offset": -1.0,
                    "step.startTime": 0.25,
                    "gain_a.k": 2.0,
                    "gain_b.k": -1.0,
                }
            )

            system = ssd.xml.system
            system.connections.extend(
                [
                    Connection(start_element="step", start_connector="y", end_element="gain_a", end_connector="u"),
                    Connection(start_element="step", start_connector="y", end_element="gain_b", end_connector="u"),
                    Connection(start_element="step", start_connector="y", end_connector="source_y"),
                    Connection(start_element="gain_a", start_connector="y", end_connector="gain_a_y"),
                    Connection(start_element="gain_b", start_connector="y", end_connector="gain_b_y"),
                ]
            )

    unpack_archive(model.paths.ssp_path, model.paths.unpacked_ssp_dir, recursive_fmus=True, overwrite=True)
    print(f"Built {model.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
