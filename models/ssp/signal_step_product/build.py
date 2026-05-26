#!/usr/bin/env python3

from __future__ import annotations

import sys
import tempfile
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "3rd_party" / "pyssp_standard"))

from pyssp_standard import LSRefExperiments, SSP
from pyssp_standard.common.archive import unpack_archive
from pyssp_standard.standard.ls_ref.model import LSRefExperiment
from pyssp_standard.ssd import Connection, DefaultExperiment
from pyssp_standard.ssv import SSV
from pyssp_standard.ssm import SSM
from utils.fmu import strip_model_exchange
from utils.model import ModelMetaData


def create_ssp(model: ModelMetaData, temp_dir: Path, exp: LSRefExperiment) -> None:
    ssp_path = temp_dir / "model.ssp"
    ssp_path.unlink(missing_ok=True)

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

    with SSP(ssp_path, mode="w") as ssp:        

        with ssp.system_structure() as ssd:
            ssd.xml.default_experiment = DefaultExperiment(start_time=0.0, stop_time=1.0)

        copied_resource_name = ssp.add_fmu(
            "step",
            model.paths.shared_fmu_dir("Modelica.Blocks.Sources.Step"),
            resource_name="Step.fmu",
            implementation="CoSimulation",
        )
        strip_model_exchange(ssp.runtime.resolve(f"resources/{copied_resource_name}"))
        copied_resource_name = ssp.add_fmu(
            "sine",
            model.paths.shared_fmu_dir("Modelica.Blocks.Sources.Sine"),
            resource_name="Sine.fmu",
            implementation="CoSimulation",
        )
        strip_model_exchange(ssp.runtime.resolve(f"resources/{copied_resource_name}"))
        copied_resource_name = ssp.add_fmu(
            "product",
            model.paths.shared_fmu_dir("Modelica.Blocks.Math.Product"),
            resource_name="Product.fmu",
            implementation="CoSimulation",
        )
        strip_model_exchange(ssp.runtime.resolve(f"resources/{copied_resource_name}"))
        ssp.add_external_parameterset(parameters_path, mapping_path)

        with ssp.system_structure() as ssd:
            system = ssd.xml.system
            system.connections.extend(
                [
                    Connection(start_element="step", start_connector="y", end_element="product", end_connector="u1"),
                    Connection(start_element="sine", start_connector="y", end_element="product", end_connector="u2"),
                ]
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

    with tempfile.TemporaryDirectory(prefix="signal_step_product_") as temp_dir:
        with LSRefExperiments(EXPERIMENTS_PATH) as experiments:
            for exp in experiments.xml.experiments:
                create_ssp(model, Path(temp_dir), exp)

    print(f"Built {model.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
