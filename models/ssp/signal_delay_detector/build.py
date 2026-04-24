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
from workflow.model import ModelMetaData
from workflow.packaging import FIXED_GENERATION_DATE_AND_TIME


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
    add_path = model.paths.fmus_dir / "Add.fmu"
    package_archive(model.paths.shared_fmu_dir("Modelica.Blocks.Sources.Step"), step_path)
    package_archive(model.paths.shared_fmu_dir("Modelica.Blocks.Math.Gain"), gain_a_path)
    package_archive(model.paths.shared_fmu_dir("Modelica.Blocks.Math.Gain"), gain_b_path)
    package_archive(model.paths.shared_fmu_dir("Modelica.Blocks.Math.Add"), add_path)
    with SSP(output_path, mode="w") as ssp:
        with ssp.system_structure() as ssd:
            ssd.xml.name = model.name
            ssd.xml.version = "1.0"
            ssd.xml.metadata.generation_date_and_time = FIXED_GENERATION_DATE_AND_TIME
            ssd.xml.system = System(name=model.name)
            ssd.xml.default_experiment = DefaultExperiment(start_time=0.0, stop_time=1.0)

        ssp.add_fmu("step", step_path, resource_name="Step.fmu", implementation="CoSimulation")
        ssp.add_fmu("gain_a", gain_a_path, resource_name="GainA.fmu", implementation="CoSimulation")
        ssp.add_fmu("gain_b", gain_b_path, resource_name="GainB.fmu", implementation="CoSimulation")
        ssp.add_fmu("add", add_path, resource_name="Add.fmu", implementation="CoSimulation")

        with ssp.system_structure() as ssd:
            ssd.extend_parameterset(
                {
                    "step": {"height": 1.0, "offset": 0.0, "startTime": 0.25},
                    "gain_a": {"k": 1.0},
                    "gain_b": {"k": 1.0},
                    "add": {"k1": 1.0, "k2": -1.0},
                }
            )

            system = ssd.xml.system
            if system is None:
                raise RuntimeError(f"System structure was not initialized for {model.name}")

            for signal_name in ["step_y", "chain_y", "sum_y"]:
                system.connectors.append(Connector(name=signal_name, kind="output", type_name="Real"))

            system.connections.extend(
                [
                    Connection(start_element="step", start_connector="y", end_element="gain_a", end_connector="u"),
                    Connection(start_element="gain_a", start_connector="y", end_element="gain_b", end_connector="u"),
                    Connection(start_element="gain_b", start_connector="y", end_element="add", end_connector="u1"),
                    Connection(start_element="step", start_connector="y", end_element="add", end_connector="u2"),
                    Connection(start_element="step", start_connector="y", end_connector="step_y"),
                    Connection(start_element="gain_b", start_connector="y", end_connector="chain_y"),
                    Connection(start_element="add", start_connector="y", end_connector="sum_y"),
                ]
            )

    unpack_archive(model.paths.ssp_path, model.paths.unpacked_ssp_dir, recursive_fmus=True, overwrite=True)
    print(f"Built {model.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
