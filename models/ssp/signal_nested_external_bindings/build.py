#!/usr/bin/env python3
"""Build signal_nested_external_bindings and its baseline study.

The SysML authors the nested ``Inner`` system and its boundary wiring. A
post-processing step binds the step scenario inline and attaches the nested
system's scenario as an external SSV+SSM binding (the form this fixture
exercises).
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from pyssp_standard import SSM, SSP, SSV
from pyssp_workflow.authoring import build_fixture, report_builds
from pyssp_workflow.binding import bind
from pyssp_workflow.fixture import BuiltFixture
from pyssp_workflow.study import read_scenario

REPO_ROOT = Path(__file__).resolve().parents[3]

MODEL_NAME = "signal_nested_external_bindings"
NESTED_SYSTEM = "inner"


def _nested_external_binding(build: BuiltFixture) -> None:
    model_build_dir = build.model_dir
    scenario = read_scenario(build.descriptor)
    prefix = f"{NESTED_SYSTEM}."
    pairs = [
        (source, target)
        for source, target in scenario.mappings
        if target.startswith(prefix)
    ]
    values = scenario.values
    ssv_name = f"{NESTED_SYSTEM}_parameters.ssv"
    ssm_name = f"{NESTED_SYSTEM}_mapping.ssm"

    with tempfile.TemporaryDirectory(prefix=f"{MODEL_NAME}_") as temp_dir:
        ssv_path = Path(temp_dir) / ssv_name
        ssm_path = Path(temp_dir) / ssm_name
        with SSV(ssv_path, mode="w") as ssv:
            ssv.xml.name = f"{NESTED_SYSTEM}_parameters"
            for member in sorted({source for source, _ in pairs}):
                ssv.xml.add_parameter(parname=member, ptype="Real", value=values[member])
        with SSM(ssm_path, mode="w") as ssm:
            for source, target in pairs:
                ssm.xml.add_mapping(source, target[len(prefix) :])

        with SSP(model_build_dir, mode="a") as ssp:
            ssp.add_resource(ssv_path)
            ssp.add_resource(ssm_path)
            with ssp.system_structure() as ssd:
                system = next(
                    element
                    for element in ssd.xml.system.elements
                    if element.name == NESTED_SYSTEM
                )
                system.add_external_parameterset(
                    source=f"resources/{ssv_name}",
                    mapping_source=f"resources/{ssm_name}",
                )


if __name__ == "__main__":
    builds = build_fixture(
        model_dir=Path(__file__).resolve().parent,
        repo_root=REPO_ROOT,
        studies=("baseline",),
    )
    scenario = read_scenario(builds["baseline"].descriptor)
    bind(
        builds["baseline"],
        scenario.ssv_path,
        ssm=scenario.ssm_path,
        mode="inline",
        mapping="flatten",
        components=frozenset({"step"}),
    )
    _nested_external_binding(builds["baseline"])
    raise SystemExit(report_builds(builds))
