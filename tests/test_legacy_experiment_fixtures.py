"""Guards for legacy SSP bodies whose experiments are authored in SysML.

The model hierarchy stays in the checked-in ``ssp/`` directory. The SysML
composition declares only a boundary ``SspModel`` marker and the study
experiment. These tests check the descriptor, the generated LS-REF experiment,
and that the built SSD still comes from the legacy body rather than from the
boundary marker.
"""

from __future__ import annotations

import json
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest
from pyssp_standard import LSRefExperiments

REPO_ROOT = Path(__file__).resolve().parents[1]
SSD = "{http://ssp-standard.org/SSP1/SystemStructureDescription}"

EXPECTED: dict[str, dict] = {
    "dcmotor": {
        "model_source": "models/ssp/dcmotor/ssp",
        "start_time": 0.0,
        "stop_time": 1.0,
        "step_size": 0.001,
        "built_components": ["SuT_edrive_mass", "SuT_emachine_model", "stimuli_model"],
        "source_components": ["stimuli_model"],
        "source_subsystems": ["SuT"],
    },
    "embrace": {
        "model_source": "models/ssp/embrace/ssp",
        "start_time": 0.0,
        "stop_time": 10.0,
        "step_size": 0.01,
        "built_components": [
            "AdaptionUnit",
            "Atmos",
            "BC",
            "Consumer",
            "ECS_HW",
            "ECS_SW",
        ],
        "source_components": [
            "AdaptionUnit",
            "Atmos",
            "BC",
            "Consumer",
            "ECS_HW",
            "ECS_SW",
        ],
        "source_subsystems": [],
    },
}


def _root(system_structure_path: Path):
    return ET.parse(system_structure_path).getroot().find(f"{SSD}System")


def _names(system, element: str) -> list[str]:
    return sorted(item.get("name") for item in system.findall(f"{SSD}Elements/{SSD}{element}"))


def _descriptor(model: str) -> dict:
    path = REPO_ROOT / "artifacts" / "studies" / model / "baseline" / "study.json"
    if not path.is_file():
        pytest.skip(f"study descriptor missing for {model}; run build_models.py")
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("model", sorted(EXPECTED))
def test_study_descriptor_is_experiment_only(model: str) -> None:
    expected = EXPECTED[model]
    descriptor = _descriptor(model)

    assert descriptor["study"] == "baseline"
    assert descriptor["model_source"] == expected["model_source"]
    assert "scenario" not in descriptor
    experiment = descriptor["experiment"]
    assert experiment["start_time"] == expected["start_time"]
    assert experiment["stop_time"] == expected["stop_time"]
    assert experiment["step_size"] == expected["step_size"]

    study_dir = REPO_ROOT / "artifacts" / "studies" / model / "baseline"
    assert [path.name for path in study_dir.iterdir()] == ["study.json"]


@pytest.mark.parametrize("model", sorted(EXPECTED))
def test_built_experiment_matches_descriptor(model: str) -> None:
    descriptor = _descriptor(model)
    experiments_path = (
        REPO_ROOT
        / "artifacts"
        / "models"
        / model
        / "baseline"
        / "model"
        / "extra"
        / "org.fmi-standard.fmi-ls-ref"
        / "experiments.xml"
    )
    if not experiments_path.is_file():
        pytest.skip(f"built experiment missing for {model}; run build_models.py")

    with LSRefExperiments(experiments_path, mode="r") as experiments:
        stored = list(experiments.xml.experiments)

    assert len(stored) == 1
    experiment = stored[0]
    assert experiment.name == descriptor["study"]
    assert experiment.target == "SystemStructure.ssd"
    assert experiment.start_time == descriptor["experiment"]["start_time"]
    assert experiment.stop_time == descriptor["experiment"]["stop_time"]
    assert experiment.step_size == descriptor["experiment"]["step_size"]
    assert experiment.tolerance is None


@pytest.mark.parametrize("model", sorted(EXPECTED))
def test_built_ssd_comes_from_the_legacy_body(model: str) -> None:
    expected = EXPECTED[model]
    built = REPO_ROOT / "artifacts" / "models" / model / "baseline" / "model" / "SystemStructure.ssd"
    if not built.is_file():
        pytest.skip(f"build output missing for {model}; run build_models.py")

    system = _root(built)
    assert _names(system, "Component") == expected["built_components"]
    assert _names(system, "System") == []

    source = _root(REPO_ROOT / "models" / "ssp" / model / "ssp" / "SystemStructure.ssd")
    assert _names(source, "Component") == expected["source_components"]
    assert _names(source, "System") == expected["source_subsystems"]


def test_registry_selects_study_cases() -> None:
    data = json.loads((REPO_ROOT / "artifacts" / "simulation_registry.json").read_text())
    models = {model["name"]: model for model in data["models"]}
    for model in EXPECTED:
        assert models[model]["build"] == "model"
        assert models[model]["cases"][0]["study"] == "baseline"
