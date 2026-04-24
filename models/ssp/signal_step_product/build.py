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
    sine_path = model.paths.fmus_dir / "Sine.fmu"
    product_path = model.paths.fmus_dir / "Product.fmu"

    package_archive(model.paths.shared_fmu_dir("Modelica.Blocks.Sources.Step"), step_path)
    package_archive(model.paths.shared_fmu_dir("Modelica.Blocks.Sources.Sine"), sine_path)
    package_archive(model.paths.shared_fmu_dir("Modelica.Blocks.Math.Product"), product_path)
    
    with SSP(output_path, mode="w") as ssp:
        with ssp.system_structure() as ssd:
            ssd.xml.name = model.name
            ssd.xml.version = "1.0"
            ssd.xml.metadata.generation_date_and_time = FIXED_GENERATION_DATE_AND_TIME
            ssd.xml.system = System(name=model.name)
            ssd.xml.default_experiment = DefaultExperiment(start_time=0.0, stop_time=1.0)

        ssp.add_fmu("step", step_path, resource_name="Step.fmu", implementation="CoSimulation")
        ssp.add_fmu("sine", sine_path, resource_name="Sine.fmu", implementation="CoSimulation")
        ssp.add_fmu("product", product_path, resource_name="Product.fmu", implementation="CoSimulation")

        with ssp.system_structure() as ssd:
            ssd.extend_parameterset(
                {
                    "step": {"height": 1.0, "offset": 0.0, "startTime": 0.25},
                    "sine": {"amplitude": 1.0, "f": 1.0, "offset": 0.0, "phase": 0.0, "startTime": 0.0},
                }
            )

            system = ssd.xml.system
            if system is None:
                raise RuntimeError(f"System structure was not initialized for {model.name}")

            for signal_name in ["step_y", "sine_y", "product_y"]:
                system.connectors.append(Connector(name=signal_name, kind="output", type_name="Real"))

            system.connections.extend(
                [
                    Connection(start_element="step", start_connector="y", end_element="product", end_connector="u1"),
                    Connection(start_element="sine", start_connector="y", end_element="product", end_connector="u2"),
                    Connection(start_element="step", start_connector="y", end_connector="step_y"),
                    Connection(start_element="sine", start_connector="y", end_connector="sine_y"),
                    Connection(start_element="product", start_connector="y", end_connector="product_y"),
                ]
            )

    unpack_archive(model.paths.ssp_path, model.paths.unpacked_ssp_dir, recursive_fmus=True, overwrite=True)
    print(f"Built {model.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
