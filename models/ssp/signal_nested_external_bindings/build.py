#!/usr/bin/env python3
"""Build signal_nested_external_bindings and its baseline study.

The SysML authors the nested ``Inner`` system and its boundary wiring. The
package hook applies the step scenario inline and attaches the nested
system's scenario as an external SSV+SSM binding (the form this fixture
exercises).
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from pyssp_standard import SSP, SSM, SSV
from pyssp_workflow.authoring import run_fixture
from pyssp_workflow.execute import apply_inline_components
from pyssp_workflow.params import (
    StudyDescriptor,
    scenario_mappings,
    scenario_values,
)

REPO_ROOT = Path(__file__).resolve().parents[3]

MODEL_NAME = "signal_nested_external_bindings"
NESTED_SYSTEM = "inner"


def _nested_external_binding(
    model_build_dir: Path, descriptor: StudyDescriptor
) -> None:
    prefix = f"{NESTED_SYSTEM}."
    pairs = [
        (source, target)
        for source, target in scenario_mappings(descriptor)
        if target.startswith(prefix)
    ]
    values = scenario_values(descriptor)
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


def package(model_build_dir: Path, descriptor: StudyDescriptor) -> None:
    apply_inline_components(model_build_dir, descriptor, only={"step"})
    _nested_external_binding(model_build_dir, descriptor)


if __name__ == "__main__":
    raise SystemExit(
        run_fixture(
            Path(__file__).resolve().parent,
            repo_root=REPO_ROOT,
            package=package,
        )
    )
