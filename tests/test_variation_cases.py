"""Per-study assertions for the SysML variation-point fixtures.

Each variation point is selected at build time and produces one SSP per
selection. This module regenerates the SSD from the source with an explicit
selection map, so the fixture's claim is checked without a build: the selected
variant changes exactly the element tree it is supposed to change.

One row per (model, study); each row names one variation point and the
structure it must produce.
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from pyssp_workflow.authoring import derive_ssd_from_sysml

REPO_ROOT = Path(__file__).resolve().parents[1]
SSD = "{http://ssp-standard.org/SSP1/SystemStructureDescription}"

# model, study, selection (model-rooted), root components, subsystems,
# nested components per subsystem, packaged FMU for the varied part.
# The SSP export resolves every attribute point in the package, so both
# studies' usages must resolve even when one case is under test.
ATTRIBUTE_SELECTION = {
    "nominal_scenario": "nominalK3",
    "boosted_scenario": "boostedK9",
}

CASES: dict[tuple[str, str], dict] = {
    ("variation_source_swap", "step"): {
        "select": {"source": "step"},
        "components": ["source"],
        "subsystems": [],
        "nested": {},
        "fmu": "resources/Step.fmu",
    },
    ("variation_source_swap", "sine"): {
        "select": {"source": "sine"},
        "components": ["source"],
        "subsystems": [],
        "nested": {},
        "fmu": "resources/Sine.fmu",
    },
    ("variation_body_gain", "one_stage"): {
        "select": {"path": "oneStage"},
        "components": ["source"],
        "subsystems": ["path"],
        "nested": {"path": ["gain"]},
        "fmu": "resources/Gain.fmu",
    },
    ("variation_body_gain", "two_stages"): {
        "select": {"path": "twoStages"},
        "components": ["source"],
        "subsystems": ["path"],
        "nested": {"path": ["gain", "product"]},
        "fmu": "resources/Product.fmu",
    },
    ("variation_attribute_set", "nominal_k3"): {
        "select": ATTRIBUTE_SELECTION,
        "components": ["gain", "step"],
        "subsystems": [],
        "nested": {},
        "fmu": "resources/Gain.fmu",
    },
    ("variation_attribute_set", "boosted_k9"): {
        "select": ATTRIBUTE_SELECTION,
        "components": ["gain", "step"],
        "subsystems": [],
        "nested": {},
        "fmu": "resources/Gain.fmu",
    },
    ("variation_nested", "direct"): {
        "select": {"path": "directPath"},
        "components": ["source"],
        "subsystems": ["path"],
        "nested": {"path": ["gain"]},
        "fmu": "resources/Gain.fmu",
    },
    ("variation_nested", "nested_gain"): {
        "select": {"path": "nestedPath", "path.inner_stage": "gainStage"},
        "components": ["source"],
        "subsystems": ["path"],
        "nested": {"path": ["output_gain"], "path.inner_stage": ["gain"]},
        "fmu": "resources/Gain.fmu",
    },
}


def _root(path: Path):
    return ET.parse(path).getroot().find(f"{SSD}System")


def _components(system) -> list[str]:
    return sorted(
        element.get("name")
        for element in system.findall(f"{SSD}Elements/{SSD}Component")
    )


def _subsystems(system) -> list[str]:
    return sorted(
        element.get("name")
        for element in system.findall(f"{SSD}Elements/{SSD}System")
    )


def _nested_component_names(system) -> list[str]:
    return sorted(
        element.get("name")
        for element in system.findall(f"{SSD}Elements/{SSD}Component")
    )


def _nested(system, dotted: str):
    current = system
    for name in dotted.split("."):
        current = current.find(f"{SSD}Elements/{SSD}System[@name='{name}']")
        assert current is not None, f"subsystem {dotted} missing"
    return current


@pytest.mark.parametrize("key", sorted(CASES))
def test_selection_produces_its_element_tree(tmp_path: Path, key: tuple[str, str]) -> None:
    """One selection changes exactly the structure the fixture documents."""
    model, _study = key
    case = CASES[key]
    output = tmp_path / f"{model}.ssd"
    derive_ssd_from_sysml(
        REPO_ROOT / "models" / "ssp" / model / "architecture",
        output,
        "System",
        selections=case["select"],
    )
    system = _root(output)
    assert _components(system) == case["components"]
    assert _subsystems(system) == case["subsystems"]
    for dotted, expected in case["nested"].items():
        assert _nested_component_names(_nested(system, dotted)) == expected


def test_attribute_variation_keeps_the_structure_and_changes_the_values() -> None:
    """Parameter variation changes the packaged values, never the element tree."""
    base = REPO_ROOT / "artifacts" / "models" / "variation_attribute_set"
    studies = {"nominal_k3": 3.0, "boosted_k9": 9.0}
    ssds = {study: base / study / "model" / "SystemStructure.ssd" for study in studies}
    if not all(path.is_file() for path in ssds.values()):
        pytest.skip("build output missing; run build_models.py")

    def without_bindings(path: Path) -> bytes:
        root = ET.parse(path).getroot()
        for parent in root.iter():
            for child in list(parent):
                if child.tag.endswith("ParameterBindings"):
                    parent.remove(child)
        return ET.tostring(root)

    assert without_bindings(ssds["nominal_k3"]) == without_bindings(ssds["boosted_k9"])

    for study, expected in studies.items():
        ssd = ET.parse(ssds[study]).getroot()
        binding = ssd.find(f".//{SSD}ParameterBindings/{SSD}ParameterBinding")
        assert binding is not None
        ssv = ET.parse(ssds[study].parent / binding.get("source")).getroot()
        values = {
            parameter.get("name"): parameter.find("{http://ssp-standard.org/SSP1/SystemStructureParameterValues}Real").get("value")
            for parameter in ssv.iter()
            if parameter.tag.endswith("Parameter")
        }
        assert float(values["k"]) == expected, values


@pytest.mark.parametrize("study", ["step", "sine"])
def test_built_ssp_records_the_selection(study: str) -> None:
    """The packaged SSP carries the selection identity that produced it."""
    selection = (
        REPO_ROOT
        / "artifacts"
        / "models"
        / "variation_source_swap"
        / study
        / "model"
        / "extra"
        / "org.pyssp"
        / "selection.json"
    )
    if not selection.is_file():
        pytest.skip(f"build output missing for {study}; run build_models.py")
    assert json.loads(selection.read_text())["selections"] == {"source": study}


# (model, study) -> the mapping target that only exists after the selection is
# resolved. A scenario bound through a variation-resolved usage must reach the
# SSP as an external SSV + SSM pair; an inline mapping is not readable by every
# engine and an absent binding leaves the FMU on its defaults.
PACKAGED: dict[tuple[str, str], str] = {
    ("variation_source_swap", "step"): "source.height",
    ("variation_source_swap", "sine"): "source.amplitude",
    ("variation_attribute_set", "nominal_k3"): "gain.k",
    ("variation_attribute_set", "boosted_k9"): "gain.k",
    ("variation_body_gain", "one_stage"): "path.gain.k",
    ("variation_body_gain", "two_stages"): "path.gain.k",
    ("variation_nested", "direct"): "path.gain.k",
    ("variation_nested", "nested_gain"): "path.inner_stage.gain.k",
}


@pytest.mark.parametrize("key", sorted(PACKAGED))
def test_built_ssp_packages_the_selected_scenario(key: tuple[str, str]) -> None:
    """The built SSP binds the study scenario to a variation-resolved target."""
    model, study = key
    ssd_path = (
        REPO_ROOT / "artifacts" / "models" / model / study / "model" / "SystemStructure.ssd"
    )
    if not ssd_path.is_file():
        pytest.skip(f"build output missing for {model}/{study}; run build_models.py")

    binding = ET.parse(ssd_path).getroot().find(
        f".//{SSD}ParameterBindings/{SSD}ParameterBinding"
    )
    assert binding is not None, "the SSP has no parameter binding"
    assert binding.get("source"), "the SSV is not packaged as an external resource"

    mapping = binding.find(f"{SSD}ParameterMapping")
    assert mapping is not None and mapping.get("source"), (
        "the SSM must be an external resource, not an inline mapping"
    )
    ssm_path = ssd_path.parent / mapping.get("source")
    assert ssm_path.is_file(), f"packaged SSM missing: {ssm_path}"
    targets = {
        entry.get("target")
        for entry in ET.parse(ssm_path).getroot()
        if entry.get("target")
    }
    assert PACKAGED[key] in targets, f"{PACKAGED[key]} not mapped; got {sorted(targets)}"
