#!/usr/bin/env python3
"""Build signal_nested_parameter_bindings and its baseline study.

Form under test: nested components carry inline parameter sets while a root
external SSV+SSM maps into ``add.k1``/``add.k2`` and overrides the nested
``inner.sine.amplitude``. The SysML composes the nested boundary and its
connections; the package hook applies both binding forms.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from pyssp_standard import SSP, SSM  # noqa: E402

from utils.authoring import (  # noqa: E402
    StudyDescriptor,
    build_fixture,
    scenario_targets,
)

MODEL_NAME = "signal_nested_parameter_bindings"
MODEL_COMPOSITION = "System"
STUDY_COMPOSITION = "baseline"
NESTED_SYSTEM = "inner"

SCENARIO_SSV_NAME = "signal_nested_parameter_bindings_parameters.ssv"
ROOT_MAPPING_NAME = "signal_nested_parameter_bindings_mapping.ssm"
ROOT_MAPPINGS = (
    ("add_k1", "add.k1"),
    ("add_k2", "add.k2"),
    ("inner_sine_amplitude", "inner.sine.amplitude"),
)


def _inline_parameters(model_build_dir: Path, descriptor: StudyDescriptor) -> None:
    """Step component inline, inner system-level inline, gain component inline."""
    targets = scenario_targets(descriptor)
    step = {name.split(".")[-1]: value for name, value in targets.items() if name.startswith("step.")}
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
    with SSP(model_build_dir, mode="a") as ssp:
        with ssp.system_structure() as ssd:
            root = ssd.xml.system
            next(e for e in root.elements if e.name == "step").extend_inline_parameterset(step)
            inner = next(e for e in root.elements if e.name == NESTED_SYSTEM)
            inner.extend_inline_parameterset(inner_system)
            next(e for e in inner.elements if e.name == "gain").extend_inline_parameterset(gain)


def _root_external_binding(
    model_build_dir: Path, descriptor: StudyDescriptor
) -> None:
    with tempfile.TemporaryDirectory(prefix=f"{MODEL_NAME}_") as temp_dir:
        ssm_path = Path(temp_dir) / ROOT_MAPPING_NAME
        with SSM(ssm_path, mode="w") as ssm:
            for source, target in ROOT_MAPPINGS:
                ssm.xml.add_mapping(source, target)
        with SSP(model_build_dir, mode="a") as ssp:
            ssp.add_external_parameterset(
                descriptor.ssv_path,
                ssm_path,
                resource_name=SCENARIO_SSV_NAME,
                mapping_resource_name=ROOT_MAPPING_NAME,
            )


def package(model_build_dir: Path, descriptor: StudyDescriptor) -> None:
    _inline_parameters(model_build_dir, descriptor)
    _root_external_binding(model_build_dir, descriptor)


def main() -> int:
    output = build_fixture(
        model_dir=MODEL_DIR,
        repo_root=REPO_ROOT,
        model_name=MODEL_NAME,
        composition=MODEL_COMPOSITION,
        study=STUDY_COMPOSITION,
        package=package,
    )
    print(f"Built {MODEL_NAME}: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
