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


def build_signal_step_add(model) -> None:
    with ExitStack() as stack:
        step_a_path = stack.enter_context(
            materialize_fmu_archive(model.paths.shared_fmu_dir("Modelica.Blocks.Sources.Step"), "StepA.fmu")
        )
        step_b_path = stack.enter_context(
            materialize_fmu_archive(model.paths.shared_fmu_dir("Modelica.Blocks.Sources.Step"), "StepB.fmu")
        )
        add_path = stack.enter_context(
            materialize_fmu_archive(model.paths.shared_fmu_dir("Modelica.Blocks.Math.Add"), "Add.fmu")
        )

        def build_system(system) -> None:
            step_a = add_component_to_system(
                system, "step_a", "StepA.fmu", step_a_path, implementation="CoSimulation"
            )
            step_b = add_component_to_system(
                system, "step_b", "StepB.fmu", step_b_path, implementation="CoSimulation"
            )
            add = add_component_to_system(
                system, "add", "Add.fmu", add_path, implementation="CoSimulation"
            )

            set_component_parameter_values(step_a, {"height": 1.5, "offset": 0.5, "startTime": 0.25})
            set_component_parameter_values(step_b, {"height": -0.5, "offset": 1.0, "startTime": 0.5})
            set_component_parameter_values(add, {"k1": 1.0, "k2": 1.0})

            for signal_name in ["step_a_y", "step_b_y", "sum_y"]:
                system.connectors.append(Connector(name=signal_name, kind="output", type_=TypeReal(None)))

            system.connections.extend(
                [
                    Connection(start_element="step_a", start_connector="y", end_element="add", end_connector="u1"),
                    Connection(start_element="step_b", start_connector="y", end_element="add", end_connector="u2"),
                    Connection(start_element="step_a", start_connector="y", end_connector="step_a_y"),
                    Connection(start_element="step_b", start_connector="y", end_connector="step_b_y"),
                    Connection(start_element="add", start_connector="y", end_connector="sum_y"),
                ]
            )

        package_ssp(
            output_path=model.paths.ssp_path,
            system_name=model.name,
            build_system=build_system,
            start_time=0.0,
            stop_time=1.0,
            resource_files={
                "StepA.fmu": step_a_path,
                "StepB.fmu": step_b_path,
                "Add.fmu": add_path,
            },
        )


if __name__ == "__main__":
    setup_directory(MODEL_DIR, ssp_builder=build_signal_step_add)
