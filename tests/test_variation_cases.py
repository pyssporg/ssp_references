"""Per-analysis assertions for the SysML variation-point fixtures.

Each variation point is selected at build time and produces one SSP per
selection. This module regenerates the SSD from the source with an explicit
selection map, so the fixture's claim is checked without a build: the selected
variant changes exactly the element tree it is supposed to change.

One row per (model, analysis); each row names one variation point and the
structure it must produce.
"""

from __future__ import annotations

import importlib.util
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from pyssp_workflow.authoring import derive_ssd_from_sysml

REPO_ROOT = Path(__file__).resolve().parents[1]
SSD = "{http://ssp-standard.org/SSP1/SystemStructureDescription}"

# model, analysis, selection (model-rooted), root components, subsystems,
# nested components per subsystem, packaged FMU for the varied part.
# The SSP export resolves every attribute point in the package, so both
# analyses' usages must resolve even when one case is under test.
ATTRIBUTE_SELECTION = {
    "nominal_scenario": "nominalK3",
    "boosted_scenario": "boostedK9",
}

# Every scenario usage on every composed analysis must resolve, including the
# pruned `sine_high` analysis, because the adapter collects attribute usages
# from all analyses that compose System.
EXCLUDES_SCENARIOS = {
    "step_baseline_scenario": "baseline",
    "step_high_scenario": "highGain",
    "sine_baseline_scenario": "baseline",
    "sine_high_scenario": "highGain",
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
    ("variation_conditional_requires", "step_single"): {
        "select": {"source": "stepImplementation", "gain": "singleStage"},
        "components": ["gain", "source"],
        "subsystems": [],
        "nested": {},
        "fmu": "resources/Gain.fmu",
    },
    ("variation_conditional_requires", "step_two"): {
        "select": {"source": "stepImplementation", "gain": "twoStages"},
        "components": ["source"],
        "subsystems": ["gain"],
        "nested": {"gain": ["firstStage", "secondStage"]},
        "fmu": "resources/Gain.fmu",
    },
    ("variation_conditional_requires", "sine_single"): {
        "select": {"source": "sineImplementation", "gain": "singleStage"},
        "components": ["gain", "source"],
        "subsystems": [],
        "nested": {},
        "fmu": "resources/Sine.fmu",
    },
    ("variation_conditional_excludes", "step_baseline"): {
        "select": {"source": "stepImplementation", **EXCLUDES_SCENARIOS},
        "components": ["gain", "source"],
        "subsystems": [],
        "nested": {},
        "fmu": "resources/Gain.fmu",
    },
    ("variation_conditional_excludes", "step_high"): {
        "select": {"source": "stepImplementation", **EXCLUDES_SCENARIOS},
        "components": ["gain", "source"],
        "subsystems": [],
        "nested": {},
        "fmu": "resources/Gain.fmu",
    },
    ("variation_conditional_excludes", "sine_baseline"): {
        "select": {"source": "sineImplementation", **EXCLUDES_SCENARIOS},
        "components": ["gain", "source"],
        "subsystems": [],
        "nested": {},
        "fmu": "resources/Sine.fmu",
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
    model, _analysis = key
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
    analyses = {"nominal_k3": 3.0, "boosted_k9": 9.0}
    ssds = {analysis: base / analysis / "model" / "SystemStructure.ssd" for analysis in analyses}
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

    for analysis, expected in analyses.items():
        ssd = ET.parse(ssds[analysis]).getroot()
        binding = ssd.find(f".//{SSD}ParameterBindings/{SSD}ParameterBinding")
        assert binding is not None
        ssv = ET.parse(ssds[analysis].parent / binding.get("source")).getroot()
        values = {
            parameter.get("name"): parameter.find("{http://ssp-standard.org/SSP1/SystemStructureParameterValues}Real").get("value")
            for parameter in ssv.iter()
            if parameter.tag.endswith("Parameter")
        }
        assert float(values["k"]) == expected, values


@pytest.mark.parametrize("analysis", ["step", "sine"])
def test_built_ssp_records_the_selection(analysis: str) -> None:
    """The packaged SSP carries the selection identity that produced it."""
    selection = (
        REPO_ROOT
        / "artifacts"
        / "models"
        / "variation_source_swap"
        / analysis
        / "model"
        / "extra"
        / "org.pyssp"
        / "selection.json"
    )
    if not selection.is_file():
        pytest.skip(f"build output missing for {analysis}; run build_models.py")
    assert json.loads(selection.read_text())["selections"] == {"source": analysis}


# (model, analysis) -> the mapping target that only exists after the selection is
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
    ("variation_conditional_requires", "step_single"): "gain.k",
    ("variation_conditional_requires", "step_two"): "gain.firstStage.k",
    ("variation_conditional_requires", "sine_single"): "gain.k",
    ("variation_conditional_excludes", "step_baseline"): "gain.k",
    ("variation_conditional_excludes", "step_high"): "gain.k",
    ("variation_conditional_excludes", "sine_baseline"): "gain.k",
}


@pytest.mark.parametrize("key", sorted(PACKAGED))
def test_built_ssp_packages_the_selected_scenario(key: tuple[str, str]) -> None:
    """The built SSP binds the analysis scenario to a variation-resolved target."""
    model, analysis = key
    ssd_path = (
        REPO_ROOT / "artifacts" / "models" / model / analysis / "model" / "SystemStructure.ssd"
    )
    if not ssd_path.is_file():
        pytest.skip(f"build output missing for {model}/{analysis}; run build_models.py")

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


def _packaged_mapping_targets(ssd_path: Path) -> set[str]:
    binding = ET.parse(ssd_path).getroot().find(
        f".//{SSD}ParameterBindings/{SSD}ParameterBinding"
    )
    assert binding is not None, "the SSP has no parameter binding"
    mapping = binding.find(f"{SSD}ParameterMapping")
    assert mapping is not None and mapping.get("source"), (
        "the SSM must be an external resource, not an inline mapping"
    )
    ssm_path = ssd_path.parent / mapping.get("source")
    assert ssm_path.is_file(), f"packaged SSM missing: {ssm_path}"
    return {
        entry.get("target")
        for entry in ET.parse(ssm_path).getroot()
        if entry.get("target")
    }


def test_two_stage_selection_binds_both_stages() -> None:
    """The cascaded branch maps the scenario to both internal Gain stages."""
    ssd_path = (
        REPO_ROOT
        / "artifacts"
        / "models"
        / "variation_conditional_requires"
        / "step_two"
        / "model"
        / "SystemStructure.ssd"
    )
    if not ssd_path.is_file():
        pytest.skip(
            "build output missing for variation_conditional_requires/step_two; "
            "run build_models.py"
        )

    targets = _packaged_mapping_targets(ssd_path)
    assert {"gain.firstStage.k", "gain.secondStage.k"} <= targets


def _load_build_module(model: str):
    path = REPO_ROOT / "models" / "ssp" / model / "build.py"
    spec = importlib.util.spec_from_file_location(f"fixture_{model}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    ("model", "pruned"),
    [
        ("variation_conditional_requires", "sine_two"),
        ("variation_conditional_excludes", "sine_high"),
    ],
)
def test_conditional_guard_prunes_illegal_selection(model: str, pruned: str) -> None:
    """The adapter-backed predicate rejects the illegal branch and never builds it."""
    module = _load_build_module(model)
    module._validate_guard()
    assert not hasattr(module, "is_legal"), "the fixture still defines a local rule"
    assert pruned in module.PRUNED
    assert pruned not in module.SELECTIONS
    assert pruned in module.SCOPED
    assert module._selection_is_legal(pruned, module.SCOPED[pruned]) is False

    for analysis, scoped in module.SCOPED.items():
        legal = module._selection_is_legal(analysis, scoped)
        assert (analysis in module.SELECTIONS) is legal
        assert (analysis in module.PRUNED) is not legal

    assert not (REPO_ROOT / "artifacts" / "models" / model / pruned).exists()
    assert not (REPO_ROOT / "artifacts" / "analyses" / model / pruned).exists()

    from workflow.registry import load_registry

    registry = load_registry(REPO_ROOT / "artifacts" / "simulation_registry.json")
    registered = next(entry for entry in registry.models if entry.name == model)
    assert {case.name for case in registered.cases} == set(module.SELECTIONS)


@pytest.mark.parametrize(
    ("model", "symbols"),
    [
        (
            "variation_conditional_requires",
            ("constraint def SineRequiresSingleStage", "assert requiresSingleStage"),
        ),
        (
            "variation_conditional_excludes",
            ("constraint def SineExcludesHighGain", "assert excludesHighGain"),
        ),
    ],
)
def test_conditional_architecture_declares_the_constraint(
    model: str, symbols: tuple[str, ...]
) -> None:
    """The authored rule and its assertion stay in the SysML source."""
    source = (
        REPO_ROOT / "models" / "ssp" / model / "architecture" / f"{model}.sysml"
    ).read_text(encoding="utf-8")
    for symbol in symbols:
        assert symbol in source


@pytest.mark.parametrize(
    ("model", "analysis", "expected"),
    [
        (
            "variation_conditional_requires",
            "step_single",
            {"source": "stepImplementation", "gain": "singleStage"},
        ),
        (
            "variation_conditional_requires",
            "step_two",
            {"source": "stepImplementation", "gain": "twoStages"},
        ),
        (
            "variation_conditional_excludes",
            "step_high",
            {"source": "stepImplementation", "step_high_scenario": "highGain"},
        ),
        (
            "variation_conditional_excludes",
            "sine_baseline",
            {"source": "sineImplementation", "sine_baseline_scenario": "baseline"},
        ),
    ],
)
def test_conditional_selection_record_matches_the_built_case(
    model: str, analysis: str, expected: dict[str, str]
) -> None:
    """The packaged record names the selection that produced the SSP."""
    selection = (
        REPO_ROOT
        / "artifacts"
        / "models"
        / model
        / analysis
        / "model"
        / "extra"
        / "org.pyssp"
        / "selection.json"
    )
    if not selection.is_file():
        pytest.skip(
            f"build output missing for {model}/{analysis}; run build_models.py"
        )

    selections = json.loads(selection.read_text())["selections"]
    assert selections.items() >= expected.items()
