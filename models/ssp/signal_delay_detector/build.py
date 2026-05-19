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
from pyssp_standard.common.archive import package_archive, unpack_archive
from pyssp_standard.standard.ls_ref.model import LSRefExperiment
from pyssp_standard.ssd import Connection, DefaultExperiment
from utils.model import ModelMetaData


def create_ssp(model: ModelMetaData, temp_dir: Path, exp: LSRefExperiment) -> None:

    with SSP(model.paths.build_dir / exp.name, mode="w") as ssp:
        with ssp.system_structure() as ssd:
            ssd.xml.default_experiment = DefaultExperiment(start_time=0.0, stop_time=1.0)

        ssp.add_fmu("step", model.paths.shared_fmu_dir("Modelica.Blocks.Sources.Step"), resource_name="Step", implementation="CoSimulation")
        ssp.add_fmu("gain_a", model.paths.shared_fmu_dir("Modelica.Blocks.Math.Gain"), resource_name="GainA", implementation="CoSimulation")
        ssp.add_fmu("gain_b", model.paths.shared_fmu_dir("Modelica.Blocks.Math.Gain"), resource_name="GainB", implementation="CoSimulation")
        ssp.add_fmu("add", model.paths.shared_fmu_dir("Modelica.Blocks.Math.Add"), resource_name="Add", implementation="CoSimulation")
        
        for parameters in exp.parameters:
            ssp.add_external_parameterset(MODEL_DIR / "ssp" / parameters.source)

        with ssp.system_structure() as ssd:
            system = ssd.xml.system
            system.connections.extend(
                [
                    Connection(start_element="step", start_connector="y", end_element="gain_a", end_connector="u"),
                    Connection(start_element="gain_a", start_connector="y", end_element="gain_b", end_connector="u"),
                    Connection(start_element="gain_b", start_connector="y", end_element="add", end_connector="u1"),
                    Connection(start_element="step", start_connector="y", end_element="add", end_connector="u2"),
                ]
            )

        for resource in [*exp.stimuli, *exp.references]:
            ssp.add_resource(MODEL_DIR / resource.source)
            if resource.mapping is not None:
                ssp.add_resource(MODEL_DIR / resource.mapping)

        with ssp.ls_ref_experiments() as experiments:
            experiments.add_experiment(exp)


EXPERIMENTS_PATH = MODEL_DIR / "experiments.xml"


def main() -> int:
    model = ModelMetaData(MODEL_DIR)
    model.reset_build_dir()

    LSRefExperiments.check_document_compliance(EXPERIMENTS_PATH)

    with tempfile.TemporaryDirectory(prefix="signal_delay_detector_") as temp_dir:
        with LSRefExperiments(EXPERIMENTS_PATH) as experiments:
            for exp in experiments.xml.experiments:
                create_ssp(model, Path(temp_dir), exp)

    print(f"Built {model.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
