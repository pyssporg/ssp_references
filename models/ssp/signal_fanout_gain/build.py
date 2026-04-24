#!/usr/bin/env python3

from __future__ import annotations

import os
import sys
from contextlib import ExitStack
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(os.environ.get("SSP_REFERENCES_REPO_ROOT", Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "3rd_party" / "pyssp_standard"))

from pyssp_standard.ssd import Connection, Connector
from workflow.packaging import (
    add_component_to_system,
    materialize_fmu_archive,
    package_ssp,
    set_component_parameter_values,
    unpack_archive_to_runtime_layout,
)
from workflow.model import ModelMetaData


def main() -> int:
    model = ModelMetaData(MODEL_DIR)
    with ExitStack() as stack:
        step_path = stack.enter_context(
            materialize_fmu_archive(model.paths.shared_fmu_dir("Modelica.Blocks.Sources.Step"), "Step.fmu")
        )
        gain_a_path = stack.enter_context(
            materialize_fmu_archive(model.paths.shared_fmu_dir("Modelica.Blocks.Math.Gain"), "GainA.fmu")
        )
        gain_b_path = stack.enter_context(
            materialize_fmu_archive(model.paths.shared_fmu_dir("Modelica.Blocks.Math.Gain"), "GainB.fmu")
        )

        def build_system(system) -> None:
            step = add_component_to_system(
                system, "step", "Step.fmu", step_path, implementation="CoSimulation"
            )
            gain_a = add_component_to_system(
                system, "gain_a", "GainA.fmu", gain_a_path, implementation="CoSimulation"
            )
            gain_b = add_component_to_system(
                system, "gain_b", "GainB.fmu", gain_b_path, implementation="CoSimulation"
            )

            set_component_parameter_values(step, {"height": 2.0, "offset": -1.0, "startTime": 0.25})
            set_component_parameter_values(gain_a, {"k": 2.0})
            set_component_parameter_values(gain_b, {"k": -1.0})

            for signal_name in ["source_y", "gain_a_y", "gain_b_y"]:
                system.connectors.append(Connector(name=signal_name, kind="output", type_name="Real"))

            system.connections.extend(
                [
                    Connection(start_element="step", start_connector="y", end_element="gain_a", end_connector="u"),
                    Connection(start_element="step", start_connector="y", end_element="gain_b", end_connector="u"),
                    Connection(start_element="step", start_connector="y", end_connector="source_y"),
                    Connection(start_element="gain_a", start_connector="y", end_connector="gain_a_y"),
                    Connection(start_element="gain_b", start_connector="y", end_connector="gain_b_y"),
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
                "GainA.fmu": gain_a_path,
                "GainB.fmu": gain_b_path,
            },
        )
    unpack_archive_to_runtime_layout(model.paths.ssp_path, model.paths.unpacked_ssp_dir)
    print(f"Built {model.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
