#!/usr/bin/env python3

from __future__ import annotations

import os
import sys
from contextlib import ExitStack
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(os.environ["SSP_REFERENCES_REPO_ROOT"])
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from pyssp_standard.common_content_ssc import TypeReal
from pyssp_standard.ssd import Connection, Connector
from workflow.packaging import (
    add_component_to_system,
    materialize_fmu_archive,
    package_ssp,
    set_component_parameter_values,
)
from workflow.setup import setup_directory


def build_signal_step_gain(model) -> None:
    with ExitStack() as stack:
        step_path = stack.enter_context(
            materialize_fmu_archive(model.paths.shared_fmu_dir("Modelica.Blocks.Sources.Step"), "Step.fmu")
        )
        gain_path = stack.enter_context(
            materialize_fmu_archive(model.paths.shared_fmu_dir("Modelica.Blocks.Math.Gain"), "Gain.fmu")
        )

        def build_system(system) -> None:
            step = add_component_to_system(
                system, "step", "Step.fmu", step_path, implementation="CoSimulation"
            )
            gain = add_component_to_system(
                system, "gain", "Gain.fmu", gain_path, implementation="CoSimulation"
            )

            set_component_parameter_values(step, {"height": 2.0, "offset": 1.0, "startTime": 0.25})
            set_component_parameter_values(gain, {"k": 3.0})

            for signal_name in ["step_y", "gain_y"]:
                system.connectors.append(Connector(name=signal_name, kind="output", type_=TypeReal(None)))

            system.connections.extend(
                [
                    Connection(start_element="step", start_connector="y", end_element="gain", end_connector="u"),
                    Connection(start_element="step", start_connector="y", end_connector="step_y"),
                    Connection(start_element="gain", start_connector="y", end_connector="gain_y"),
                ]
            )

        package_ssp(
            output_path=model.paths.ssp_path,
            system_name=model.name,
            build_system=build_system,
            start_time=0.0,
            stop_time=1.0,
            resource_files={
                "Step.fmu": step_path,
                "Gain.fmu": gain_path,
            },
        )


if __name__ == "__main__":
    setup_directory(MODEL_DIR, ssp_builder=build_signal_step_gain)
