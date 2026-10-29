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
        "select": {"scenario": "nominalK3"},
        "components": ["gain", "step"],
        "subsystems": [],
        "nested": {},
        "fmu": "resources/Gain.fmu",
    },
    ("variation_attribute_set", "boosted_k9"): {
        "select": {"scenario": "boostedK9"},
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


def test_attribute_variation_leaves_the_structure_untouched(tmp_path: Path) -> None:
    """Parameter variation changes the SSV, never the SSD."""
    architecture = (
        REPO_ROOT / "models" / "ssp" / "variation_attribute_set" / "architecture"
    )
    nominal = tmp_path / "nominal.ssd"
    boosted = tmp_path / "boosted.ssd"
    derive_ssd_from_sysml(
        architecture, nominal, "System", selections={"scenario": "nominalK3"}
    )
    derive_ssd_from_sysml(
        architecture, boosted, "System", selections={"scenario": "boostedK9"}
    )
    nominal_text = nominal.read_text()
    boosted_text = boosted.read_text()
    assert "NominalK3" in nominal_text and "BoostedK9" in boosted_text
    assert nominal_text.replace("NominalK3", "SET") == boosted_text.replace(
        "BoostedK9", "SET"
    )


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
