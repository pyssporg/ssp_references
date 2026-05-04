#!/usr/bin/env python3

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(os.environ.get("SSP_REFERENCES_REPO_ROOT", Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "3rd_party" / "pyssp_standard"))

from pyssp_standard import SSP
from pyssp_standard.common.archive import package_archive, unpack_archive
from pyssp_standard.ssm import SSM
from pyssp_standard.ssd import Connection, DefaultExperiment
from pyssp_standard.ssv import SSV
from utils.model import ModelMetaData


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

    with tempfile.TemporaryDirectory(prefix="signal_step_product_", dir=model.paths.build_dir) as temp_dir:
        parameters_path = Path(temp_dir) / "signal_step_product_parameters.ssv"
        mapping_path = Path(temp_dir) / "signal_step_product_mapping.ssm"

        with SSV(parameters_path, "w") as ssv:
            ssv.xml.name = "StepProductParameters"
            ssv.xml.add_parameter(parname="step_height", ptype="Real", value=1.0)
            ssv.xml.add_parameter(parname="step_offset", ptype="Real", value=0.0)
            ssv.xml.add_parameter(parname="step_startTime", ptype="Real", value=0.25)
            ssv.xml.add_parameter(parname="sine_amplitude", ptype="Real", value=1.0)
            ssv.xml.add_parameter(parname="sine_f", ptype="Real", value=1.0)
            ssv.xml.add_parameter(parname="sine_offset", ptype="Real", value=0.0)
            ssv.xml.add_parameter(parname="sine_phase", ptype="Real", value=0.0)
            ssv.xml.add_parameter(parname="sine_startTime", ptype="Real", value=0.0)

        with SSM(mapping_path, "w") as ssm:
            ssm.xml.add_mapping("step_height", "step.height")
            ssm.xml.add_mapping("step_offset", "step.offset")
            ssm.xml.add_mapping("step_startTime", "step.startTime")
            ssm.xml.add_mapping("sine_amplitude", "sine.amplitude")
            ssm.xml.add_mapping("sine_f", "sine.f")
            ssm.xml.add_mapping("sine_offset", "sine.offset")
            ssm.xml.add_mapping("sine_phase", "sine.phase")
            ssm.xml.add_mapping("sine_startTime", "sine.startTime")

        with SSP(output_path, mode="w") as ssp:
            with ssp.system_structure() as ssd:
                ssd.xml.default_experiment = DefaultExperiment(start_time=0.0, stop_time=1.0)

            ssp.add_fmu("step", step_path, resource_name="Step.fmu", implementation="CoSimulation")
            ssp.add_fmu("sine", sine_path, resource_name="Sine.fmu", implementation="CoSimulation")
            ssp.add_fmu("product", product_path, resource_name="Product.fmu", implementation="CoSimulation")
            ssp.add_external_parameterset(parameters_path, mapping_path)

            with ssp.system_structure() as ssd:
                system = ssd.xml.system
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
