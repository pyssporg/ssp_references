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
from utils.model import ModelMetaData


def main() -> int:
    model = ModelMetaData(MODEL_DIR)
    output_path = model.paths.ssp_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    model.paths.fmus_dir.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()

    step_path = model.paths.fmus_dir / "Step.fmu"
    gain_path = model.paths.fmus_dir / "Gain.fmu"
    parameters_path = MODEL_DIR / "ssp" / "resources" / "signal_step_gain_parameters.ssv"
    package_archive(model.paths.shared_fmu_dir("Modelica.Blocks.Sources.Step"), step_path)
    package_archive(model.paths.shared_fmu_dir("Modelica.Blocks.Math.Gain"), gain_path)
    with SSP(output_path, mode="w") as ssp:
        with ssp.system_structure() as ssd:
            ssd.xml.default_experiment = DefaultExperiment(start_time=0.0, stop_time=1.0)

        ssp.add_fmu("step", step_path, resource_name="Step.fmu", implementation="CoSimulation")
        ssp.add_fmu("gain", gain_path, resource_name="Gain.fmu", implementation="CoSimulation")
        ssp.add_external_parameterset(parameters_path)

        with ssp.system_structure() as ssd:
            system = ssd.xml.system
            system.connections.extend(
                [
                    Connection(start_element="step", start_connector="y", end_element="gain", end_connector="u"),
                    Connection(start_element="step", start_connector="y", end_connector="step_y"),
                    Connection(start_element="gain", start_connector="y", end_connector="gain_y"),
                ]
            )

    unpack_archive(model.paths.ssp_path, model.paths.unpacked_ssp_dir, recursive_fmus=True, overwrite=True)
    print(f"Built {model.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
