"""Guards for the SysML-authored fixtures.

Two layers are checked:

- ``test_sysml_wiring`` regenerates each fixture's SSD from its SysML source
  and asserts the composition wiring. This is the SysML -> SSP transformation.
- ``test_built_scenario_form`` asserts the parameter-application form of the
  committed build output. The fixture applies the form in an explicit packaging
  step after ``build_fixture``, so this covers what the SysML dialect cannot
  express.

The expected structures are the verified migration targets. Rebuild with
``python3 scripts/build_models.py run-all`` after changing a fixture.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pyssp_standard import SSV
from pyssp_workflow.authoring import derive_ssd_from_sysml

REPO_ROOT = Path(__file__).resolve().parents[1]

SSD = "{http://ssp-standard.org/SSP1/SystemStructureDescription}"


# model -> study, expected components, two-element connections, subsystems, form
EXPECTED: dict[str, dict] = {
    "signal_fanout_gain": {
        "study": "baseline",
        "components": ["gain_a", "gain_b", "step"],
        "connections": [("step", "y", "gain_a", "u"), ("step", "y", "gain_b", "u")],
        "subsystems": [],
        "form": "external-target-named",
    },
    "signal_step_gain": {
        "study": "test_baseline",
        "components": ["gain", "step"],
        "connections": [("step", "y", "gain", "u")],
        "subsystems": [],
        "form": "external+mapping",
    },
    "signal_algebraic_loop": {
        "study": "baseline",
        "components": ["add", "gain", "sine"],
        "connections": [
            ("add", "y", "gain", "u"),
            ("gain", "y", "add", "u2"),
            ("sine", "y", "add", "u1"),
        ],
        "subsystems": [],
        "form": "external-target-named",
    },
    "signal_delay_detector": {
        "study": "baseline",
        "components": ["add", "gain_a", "gain_b", "step"],
        "connections": [
            ("gain_a", "y", "gain_b", "u"),
            ("gain_b", "y", "add", "u1"),
            ("step", "y", "add", "u2"),
            ("step", "y", "gain_a", "u"),
        ],
        "subsystems": [],
        "form": "external-target-named",
    },
    "signal_nested_algebraic_loop": {
        "study": "baseline",
        "components": ["add_inner", "add_outer", "gain_inner", "gain_outer", "sine"],
        "connections": [
            ("add_inner", "y", "add_outer", "u2"),
            ("add_inner", "y", "gain_inner", "u"),
            ("add_outer", "y", "gain_outer", "u"),
            ("gain_inner", "y", "add_inner", "u2"),
            ("gain_outer", "y", "add_inner", "u1"),
            ("sine", "y", "add_outer", "u1"),
        ],
        "subsystems": [],
        "form": "external-target-named",
    },
    "signal_step_product": {
        "study": "baseline",
        "components": ["product", "sine", "step"],
        "connections": [("sine", "y", "product", "u2"), ("step", "y", "product", "u1")],
        "subsystems": [],
        "form": "external+mapping",
    },
    "signal_step_add": {
        "study": "baseline",
        "components": ["add", "step_a", "step_b"],
        "connections": [("step_a", "y", "add", "u1"), ("step_b", "y", "add", "u2")],
        "subsystems": [],
        "form": "external+mapping",
    },
    "signal_sine_gain_add": {
        "study": "baseline",
        "components": ["add", "gain", "sine", "step"],
        "connections": [
            ("gain", "y", "add", "u1"),
            ("sine", "y", "gain", "u"),
            ("step", "y", "add", "u2"),
        ],
        "subsystems": [],
        "form": "inline",
    },
    "signal_parameter_inline_with_mapping": {
        "study": "baseline",
        "components": ["step"],
        "connections": [],
        "subsystems": [],
        "form": "inline+mapping",
    },
    "signal_nested_pass_through": {
        "study": "baseline",
        "components": ["add", "step"],
        "connections": [("inner", "v", "add", "u1"), ("step", "y", "inner", "u")],
        "subsystems": ["inner"],
        "boundary": [("add.y", "y")],
        "subsystem_boundary": {"inner": [("u", "gain.u"), ("gain.y", "v")]},
        "form": "none",
    },
    "signal_nested_external_bindings": {
        "study": "baseline",
        "components": ["step"],
        "connections": [],
        "subsystems": ["inner"],
        "boundary": [("step.y", "y")],
        "subsystem_boundary": {"inner": [("sine.y", "y")]},
        "form": "none",
    },
    "signal_nested_parameter_bindings": {
        "study": "baseline",
        "components": ["add", "step"],
        "connections": [("inner", "y", "add", "u2"), ("step", "y", "add", "u1")],
        "subsystems": ["inner"],
        "boundary": [("add.y", "y")],
        "subsystem_boundary": {"inner": [("gain.y", "y")]},
        "form": "external+mapping",
    },
    "pyfmu_csv_source_sink": {
        "study": "baseline",
        "components": ["sink", "source"],
        "connections": [("source", "y", "sink", "u")],
        "subsystems": [],
        "form": "external+mapping",
    },
    "scenario": {
        "study": "baseline",
        "components": ["scenario"],
        "connections": [],
        "subsystems": [],
        "form": "external+mapping",
    },
}


def _root(system_structure_path: Path):
    from xml.etree import ElementTree as ET

    return ET.parse(system_structure_path).getroot().find(f"{SSD}System")


def _components(system) -> list[str]:
    return sorted(e.get("name") for e in system.findall(f"{SSD}Elements/{SSD}Component"))


def _subsystems(system) -> list[str]:
    return sorted(e.get("name") for e in system.findall(f"{SSD}Elements/{SSD}System"))


def _wiring(system) -> list[tuple[str, str, str, str]]:
    """Connections between two elements; boundary ends are excluded."""
    result = []
    for connection in system.findall(f"{SSD}Connections/{SSD}Connection"):
        start_element = connection.get("startElement")
        end_element = connection.get("endElement")
        if start_element and end_element:
            result.append(
                (
                    start_element,
                    connection.get("startConnector"),
                    end_element,
                    connection.get("endConnector"),
                )
            )
    return sorted(result)


def _endpoint(element: str | None, connector: str) -> str:
    """`part.connector`, or just `connector` for the system boundary."""
    return connector if element is None else f"{element}.{connector}"


def _boundary_wiring(system) -> list[tuple[str, str]]:
    """Connections with at least one end on the system boundary."""
    result = []
    for connection in system.findall(f"{SSD}Connections/{SSD}Connection"):
        start_element = connection.get("startElement")
        end_element = connection.get("endElement")
        if start_element is None or end_element is None:
            result.append(
                (
                    _endpoint(start_element, connection.get("startConnector")),
                    _endpoint(end_element, connection.get("endConnector")),
                )
            )
    return sorted(result)


def _form(system) -> str:
    binding = system.find(f"{SSD}ParameterBindings/{SSD}ParameterBinding")
    if binding is None:
        return "none"
    mapping = binding.find(f"{SSD}ParameterMapping")
    if binding.get("source"):
        return "external+mapping" if mapping is not None else "external-target-named"
    return "inline+mapping" if mapping is not None else "inline"


@pytest.mark.parametrize("model", sorted(EXPECTED))
def test_sysml_wiring(tmp_path: Path, model: str) -> None:
    """The SysML composition regenerates the expected SSD wiring."""
    expected = EXPECTED[model]
    output = tmp_path / f"{model}.ssd"
    derive_ssd_from_sysml(
        REPO_ROOT / "models" / "ssp" / model / "architecture",
        output,
        "System",
    )
    system = _root(output)
    assert _components(system) == expected["components"]
    assert _subsystems(system) == expected["subsystems"]
    assert _wiring(system) == sorted(expected["connections"])
    assert _boundary_wiring(system) == sorted(expected.get("boundary", []))
    for subsystem_name, connections in expected.get("subsystem_boundary", {}).items():
        subsystem = system.find(f"{SSD}Elements/{SSD}System[@name='{subsystem_name}']")
        assert subsystem is not None
        assert _boundary_wiring(subsystem) == sorted(connections)


@pytest.mark.parametrize("model", sorted(EXPECTED))
def test_built_scenario_form(model: str) -> None:
    """The committed build output exposes the fixture's parameter form."""
    expected = EXPECTED[model]
    ssd = (
        REPO_ROOT
        / "artifacts"
        / "models"
        / model
        / expected["study"]
        / "model"
        / "SystemStructure.ssd"
    )
    if not ssd.is_file():
        pytest.skip(f"build output missing for {model}; run build_models.py")
    system = _root(ssd)
    assert _components(system) == expected["components"]
    assert _subsystems(system) == expected["subsystems"]
    assert _form(system) == expected["form"]


def test_pyfmu_csv_source_sink_structure_needs_no_fmu(tmp_path: Path) -> None:
    """The CSV fixture's SysML defines the full structure without an FMU."""
    output = tmp_path / "pyfmu_csv_source_sink.ssd"
    derive_ssd_from_sysml(
        REPO_ROOT / "models" / "ssp" / "pyfmu_csv_source_sink" / "architecture",
        output,
        "System",
    )
    system = _root(output)
    assert _components(system) == ["sink", "source"]
    assert _subsystems(system) == []
    assert _wiring(system) == [("source", "y", "sink", "u")]
    sources = {
        element.get("name"): element.get("source")
        for element in system.findall(f"{SSD}Elements/{SSD}Component")
    }
    assert sources == {"sink": "resources/Gain.fmu", "source": ""}


SCENARIO_INPUT = (
    "Alt;L;0,0;300,5000\n"
    "Mach;L;0,0;300,1.2\n"
    "heat_load;ZOH;0,50;150,4000\n"
    "Wgt_On_Whl;ZOH;0,1;150,0\n"
    "Aircraft_state;ZOH;0,0;150,4"
)


def _ssv_parameters(path: Path) -> list[tuple[str, str, str | None]]:
    with SSV(path, mode="r") as ssv:
        return [
            (parameter.name, parameter.type_name, parameter.attributes.get("value"))
            for parameter in ssv.xml.parameters
        ]


def test_scenario_preserves_legacy_parameter_set() -> None:
    """The SysML set reproduces the old SSV member names, types, and values."""
    ssv = (
        REPO_ROOT
        / "artifacts"
        / "models"
        / "scenario"
        / "baseline"
        / "model"
        / "resources"
        / "parameter_sets"
        / "ScenarioSet.ssv"
    )
    if not ssv.is_file():
        pytest.skip("build output missing for scenario; run build_models.py")

    assert _ssv_parameters(ssv) == [
        ("scenario_input", "String", SCENARIO_INPUT),
        ("Alt_start", "Real", "0"),
        ("Mach_start", "Real", "0"),
        ("heat_load_start", "Real", "50"),
        ("Wgt_On_Whl_start", "Real", "1"),
        ("Aircraft_state_start", "Real", "0"),
    ]


def test_scenario_mapping_keeps_only_the_live_target() -> None:
    """The model-owned binding maps only the one parameter in this SSP."""
    ssd = (
        REPO_ROOT
        / "artifacts"
        / "models"
        / "scenario"
        / "baseline"
        / "model"
        / "SystemStructure.ssd"
    )
    if not ssd.is_file():
        pytest.skip("build output missing for scenario; run build_models.py")

    from pyssp_standard import SSD as Ssp1SSD

    with Ssp1SSD(ssd, mode="r") as document:
        [binding] = document.xml.system.parameter_bindings
        mappings = [
            (mapping.source, mapping.target)
            for mapping in binding.parameter_mapping.mapping.mappings
        ]
    assert mappings == [("scenario_input", "scenario.scenario_input")]


def test_scenario_has_one_root_parameter_binding() -> None:
    """The built SSP has exactly one root binding, not the old duplicate."""
    ssd = (
        REPO_ROOT
        / "artifacts"
        / "models"
        / "scenario"
        / "baseline"
        / "model"
        / "SystemStructure.ssd"
    )
    if not ssd.is_file():
        pytest.skip("build output missing for scenario; run build_models.py")

    system = _root(ssd)
    assert len(system.findall(f"{SSD}ParameterBindings/{SSD}ParameterBinding")) == 1


def test_registry_resolves_model_study_build_layout() -> None:
    """Migrated cases resolve to artifacts/models/<model>/<study>/<build>."""
    from workflow.registry import load_registry

    registry = load_registry(REPO_ROOT / "artifacts" / "simulation_registry.json")
    models = {model.name: model for model in registry.models}
    root = REPO_ROOT / "artifacts" / "models"

    for model, expected in EXPECTED.items():
        if model not in models:
            continue
        assert models[model].build == "model"
        spec = registry.expand(model_names=[model])[0]
        assert spec.ssp_root == root / model / expected["study"] / "model"
        assert spec.study_root == (
            REPO_ROOT / "artifacts" / "studies" / model / expected["study"]
        )


@pytest.mark.parametrize("model", sorted(EXPECTED))
def test_study_descriptor_has_step_and_no_tolerance(model: str) -> None:
    """Study descriptors carry the window and step, never a tolerance."""
    import json

    descriptor = (
        REPO_ROOT
        / "artifacts"
        / "studies"
        / model
        / EXPECTED[model]["study"]
        / "study.json"
    )
    if not descriptor.is_file():
        pytest.skip(f"study descriptor missing for {model}; run build_models.py")
    experiment = json.loads(descriptor.read_text(encoding="utf-8"))["experiment"]
    assert "step_size" in experiment
    assert "tolerance" not in experiment


def test_vanderpol_registers_three_studies() -> None:
    """VanDerPol exercises one exported model with three registered studies."""
    from workflow.registry import load_registry

    registry = load_registry(REPO_ROOT / "artifacts" / "simulation_registry.json")
    specs = registry.expand(model_names=["VanDerPol"])

    assert [spec.case_name for spec in specs] == ["baseline", "fast", "slow"]
    assert [spec.study_name for spec in specs] == ["baseline", "fast", "slow"]
    assert all(spec.ssp_root.name == "model" for spec in specs)


@pytest.mark.parametrize(
    ("study", "expected"),
    [
        ("baseline", "mu set to 1.0"),
        ("fast", "mu set to 2.0"),
        ("slow", "mu set to 0.5"),
    ],
)
def test_vanderpol_study_description_reaches_setup(
    study: str, expected: str
) -> None:
    """The Study doc reaches the descriptor and the frozen setup manifest."""
    descriptor_path = REPO_ROOT / "artifacts" / "studies" / "VanDerPol" / study / "study.json"
    setup_path = REPO_ROOT / "artifacts" / "simulation" / "VanDerPol" / study / "setup.json"
    if not descriptor_path.is_file():
        pytest.skip(f"study descriptor missing for VanDerPol/{study}")

    descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
    assert expected in descriptor["description"]
    if not setup_path.is_file():
        pytest.skip(f"setup manifest missing for VanDerPol/{study}; run simulations")

    setup = json.loads(setup_path.read_text(encoding="utf-8"))
    assert setup["description"] == descriptor["description"]
