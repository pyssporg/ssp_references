#!/usr/bin/env python3
"""Build signal_nested_parameter_bindings and its baseline study.

Form under test: nested components carry inline parameter sets while a root
external SSV+SSM maps into ``add.k1``/``add.k2`` and overrides the nested
``inner.sine.amplitude``. The SysML composes the nested boundary and its
connections; post-processing applies both binding forms.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from pyssp_standard import SSM, SSP
from pyssp_workflow.authoring import build_fixture, report_builds
from pyssp_workflow.fixture import BuiltFixture
from pyssp_workflow.study import read_scenario, scenario_targets

REPO_ROOT = Path(__file__).resolve().parents[3]

MODEL_NAME = "signal_nested_parameter_bindings"
NESTED_SYSTEM = "inner"

SCENARIO_SSV_NAME = "signal_nested_parameter_bindings_parameters.ssv"
ROOT_MAPPING_NAME = "signal_nested_parameter_bindings_mapping.ssm"
ROOT_MAPPINGS = (
    ("add_k1", "add.k1"),
    ("add_k2", "add.k2"),
    ("inner_sine_amplitude", "inner.sine.amplitude"),
)


def _inline_parameters(build: BuiltFixture) -> None:
    """Step component inline, inner system-level inline, gain component inline."""
    targets = scenario_targets(read_scenario(build.descriptor))
    step = {
        name.split(".")[-1]: value
        for name, value in targets.items()
        if name.startswith("step.")
    }
    inner_system = {
        name[len(f"{NESTED_SYSTEM}.") :]: value
        for name, value in targets.items()
        if name.startswith(f"{NESTED_SYSTEM}.sine.")
    }
    gain = {
        name.split(".")[-1]: value
        for name, value in targets.items()
        if name.startswith(f"{NESTED_SYSTEM}.gain.")
    }
    with SSP(build.model_dir, mode="a") as ssp, ssp.system_structure() as ssd:
        root = ssd.system
        next(e for e in root.elements if e.name == "step").extend_inline_parameterset(step)
        inner = next(e for e in root.elements if e.name == NESTED_SYSTEM)
        inner.extend_inline_parameterset(inner_system)
        next(e for e in inner.elements if e.name == "gain").extend_inline_parameterset(gain)


def _root_external_binding(build: BuiltFixture) -> None:
    with tempfile.TemporaryDirectory(prefix=f"{MODEL_NAME}_") as temp_dir:
        ssm_path = Path(temp_dir) / ROOT_MAPPING_NAME
        with SSM(ssm_path, mode="w") as ssm:
            for source, target in ROOT_MAPPINGS:
                ssm.xml.add_mapping(source, target)
        with SSP(build.model_dir, mode="a") as ssp:
            ssp.add_external_parameterset(
                build.descriptor.ssv_path,
                ssm_path,
                resource_name=SCENARIO_SSV_NAME,
                mapping_resource_name=ROOT_MAPPING_NAME,
            )


if __name__ == "__main__":
    builds = build_fixture(
        model_dir=Path(__file__).resolve().parent,
        repo_root=REPO_ROOT,
        studies=("baseline",),
    )
    _inline_parameters(builds["baseline"])
    _root_external_binding(builds["baseline"])
    raise SystemExit(report_builds(builds))
