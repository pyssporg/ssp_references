from __future__ import annotations

import json
from pathlib import Path
from xml.etree import ElementTree as ET

import numpy as np
import pytest

from workflow.comparison import (
    ComparisonBatchRequest,
    ComparisonBatchRun,
    ComparisonRequest,
    ComparisonRun,
    compare_run_batch,
    compare_runs,
)
from workflow.registry import (
    RegistryCase,
    RegistryModel,
    RegistryReferenceCsv,
    SimulationCaseSpec,
    SimulationRegistry,
    load_registry,
)
from workflow.setup import prepare_setup
from workflow.simulate import SimulationRequest, SimulationRun, write_structured_csv
from utils.csv import extract_series, load_numeric_csv


@pytest.fixture(autouse=True)
def isolated_repo_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    monkeypatch.setattr("workflow.layout.REPO_ROOT", repo_root)
    monkeypatch.setattr("workflow.registry.REPO_ROOT", repo_root)
    monkeypatch.setattr("workflow.simulate.REPO_ROOT", repo_root)
    monkeypatch.setattr("utils.config.REPO_ROOT", repo_root)


def make_ssp_root(tmp_path: Path, model_name: str = "ExampleModel") -> Path:
    ssp_root = tmp_path / "artifacts" / "models" / model_name / "baseline"
    (ssp_root / "extra" / "org.fmi-standard.fmi-ls-ref").mkdir(parents=True)
    (ssp_root / "resources").mkdir()
    (ssp_root / "SystemStructure.ssd").write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<ssd:SystemStructure xmlns:ssd="http://ssp-standard.org/SSP1/SystemStructure">
  <ssd:System name="system" />
</ssd:SystemStructure>
"""
    )
    (ssp_root / "extra" / "org.fmi-standard.fmi-ls-ref" / "experiments.xml").write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<Experiments name="ExampleModel experiments">
  <Experiment
      name="baseline"
      target="SystemStructure.ssd"
      startTime="0.0"
      stopTime="1.0"
      stepSize="1.0"
      tolerance="0.0001"
      description="Baseline case"/>
</Experiments>
"""
    )
    return ssp_root


def write_series(path: Path, signal_values: list[float]) -> None:
    result = np.array(
        [(float(index), value) for index, value in enumerate(signal_values)],
        dtype=[("time", float), ("signal", float)],
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    write_structured_csv(path, result)


def write_prefixed_csv(path: Path, signal_name: str, signal_values: list[float]) -> None:
    rows = ["time,{}".format(signal_name)]
    for index, value in enumerate(signal_values):
        rows.append(f"{float(index)},{value}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(rows) + "\n")


def write_columns(path: Path, columns: dict[str, list[float]]) -> None:
    names = list(columns)
    row_count = len(next(iter(columns.values())))
    rows = [",".join(["time", *names])]
    for index in range(row_count):
        values = [str(float(index))]
        values.extend(str(columns[name][index]) for name in names)
        rows.append(",".join(values))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(rows) + "\n")


def test_extract_series_uses_signed_data_row_for_alias_sign() -> None:
    headers, _, columns = extract_series(
        names=["time", "signal", "negated_alias"],
        descriptions=["time", "signal", "negated alias"],
        data_info=np.array(
            [
                [0, 2, 2],
                [1, 2, -2],
                [0, 0, 0],
                [-1, -1, -1],
            ]
        ),
        data_1=np.empty((0, 0)),
        data_2=np.array(
            [
                [0.0, 1.0],
                [2.0, 3.0],
            ]
        ),
    )

    assert headers == ["time", "signal", "negated_alias"]
    np.testing.assert_array_equal(columns[1], np.array([2.0, 3.0]))
    np.testing.assert_array_equal(columns[2], np.array([-2.0, -3.0]))


def test_reference_csvs_are_not_inverted() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    checks = [
        (
            repo_root / "models/ssp/BouncingBall/references/BouncingBall-cs.csv",
            {
                "default.BouncingBall.h": (0, 1.0),
                "default.BouncingBall.v": (1, -0.00981),
            },
        ),
        (
            repo_root / "models/ssp/Dahlquist/references/Dahlquist-cs.csv",
            {
                "default.Dahlquist.x": (0, 1.0),
                "default.Dahlquist.der(x)": (0, -1.0),
            },
        ),
        (
            repo_root / "models/ssp/Stair/references/Stair-cs.csv",
            {
                "default.Stair.counter": (0, 1.0),
            },
        ),
        (
            repo_root / "models/ssp/VanDerPol/references/VanDerPol-cs.csv",
            {
                "default.VanDerPol.x0": (0, 2.0),
                "default.VanDerPol.der(x1)": (0, -2.0),
            },
        ),
    ]

    for path, expected_values in checks:
        columns = load_numeric_csv(path)["columns"]
        for column_name, (row_index, expected_value) in expected_values.items():
            assert columns[column_name][row_index] == pytest.approx(expected_value)


def test_modelica_block_fmus_expose_dependency_metadata() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    expected_dependencies = {
        "Modelica.Blocks.Math.Gain": ("2", "2 4"),
        "Modelica.Blocks.Math.Add": ("2 3", "2 3 5 6"),
    }

    for model_name, (output_dependencies, initial_dependencies) in expected_dependencies.items():
        path = repo_root / "models" / "fmu" / model_name / "fmu" / "modelDescription.xml"
        root = ET.parse(path).getroot()
        outputs = root.find(".//{*}ModelStructure/{*}Outputs/{*}Unknown")
        initial = root.find(".//{*}ModelStructure/{*}InitialUnknowns/{*}Unknown")

        assert outputs is not None
        assert outputs.attrib["dependencies"] == output_dependencies
        assert initial is not None
        assert initial.attrib["dependencies"] == initial_dependencies


def test_registry_includes_algebraic_loop_fixtures() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    registry = load_registry(repo_root / "artifacts" / "simulation_registry.json")
    models = {model.name: model for model in registry.models}

    assert models["signal_algebraic_loop"].compare_signals == ("sine.y", "add.y", "gain.y")
    assert models["signal_nested_algebraic_loop"].compare_signals == (
        "sine.y",
        "add_outer.y",
        "gain_outer.y",
        "add_inner.y",
        "gain_inner.y",
    )


def test_registry_roundtrip_supports_multiple_models_and_cases() -> None:
    registry = SimulationRegistry(
        models=(
            RegistryModel(
                name="ExampleModel",
                compare_signals=("signal",),
                cases=(
                    RegistryCase(name="baseline", backends=("ssp4sim", "omsimulator", "fmpy")),
                    RegistryCase(name="fast", backends=("ssp4sim",)),
                ),
            ),
            RegistryModel(
                name="OtherModel",
                compare_signals=("output",),
                cases=(RegistryCase(name="baseline", backends=("omsimulator",)),),
            ),
        ),
    )

    loaded = SimulationRegistry.from_dict(registry.to_dict())
    assert loaded == registry


def test_registry_roundtrip_supports_reference_csvs() -> None:
    registry = SimulationRegistry(
        models=(
            RegistryModel(
                name="ExampleModel",
                compare_signals=("signal",),
                cases=(
                    RegistryCase(
                        name="baseline",
                        backends=("ssp4sim",),
                        reference_csvs=(
                            RegistryReferenceCsv(
                                label="reference-cs",
                                path=Path("models/ssp/ExampleModel/references/ExampleModel-cs.csv"),
                            ),
                            RegistryReferenceCsv(
                                label="reference-me",
                                path=Path("models/ssp/ExampleModel/references/ExampleModel-me.csv"),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )

    loaded = SimulationRegistry.from_dict(registry.to_dict())
    spec = loaded.expand()[0]

    assert loaded == registry
    assert [reference.label for reference in spec.reference_csvs] == ["reference-cs", "reference-me"]


def test_setup_manifest_roundtrip(tmp_path: Path) -> None:
    ssp_root = make_ssp_root(tmp_path)
    spec = SimulationCaseSpec(
        model_name="ExampleModel",
        case_name="baseline",
        ssp_root=ssp_root,
        backends=("ssp4sim", "omsimulator", "fmpy"),
        compare_signals=("signal",),
    )

    setup = prepare_setup(spec)
    manifest_path = setup.write_manifest()

    assert manifest_path.exists()
    assert setup.model_name == "ExampleModel"
    assert setup.case_name == "baseline"
    assert setup.window.start_time == pytest.approx(0.0)
    assert setup.window.stop_time == pytest.approx(1.0)
    assert setup.window.interval == pytest.approx(1.0)
    assert setup.tolerance == pytest.approx(0.0001)
    assert setup.description == "Baseline case"

    loaded = type(setup).from_manifest(manifest_path)
    assert loaded.ssp_root == ssp_root.resolve()
    assert loaded.model_name == "ExampleModel"
    assert loaded.case_name == "baseline"
    assert loaded.backends == ("ssp4sim", "omsimulator", "fmpy")
    assert loaded.compare_signals == ("signal",)
    assert loaded.root_system_name == "system"
    assert loaded.window == setup.window
    assert loaded.tolerance == pytest.approx(setup.tolerance)


def test_simulation_run_manifest_roundtrip(tmp_path: Path) -> None:
    ssp_root = make_ssp_root(tmp_path)
    spec = SimulationCaseSpec(
        model_name="ExampleModel",
        case_name="baseline",
        ssp_root=ssp_root,
        backends=("ssp4sim", "omsimulator", "fmpy"),
        compare_signals=("signal",),
    )
    setup = prepare_setup(spec)
    setup.write_manifest()

    request = SimulationRequest(setup=setup, backend="ssp4sim")
    write_series(request.result_path, [0.0, 1.0])

    run = SimulationRun(
        request=request,
        result_path=request.result_path,
        runtime_s=0.25,
    )
    manifest_path = run.write_manifest()

    assert manifest_path.exists()

    loaded = SimulationRun.from_manifest(manifest_path)
    assert loaded.request.backend == "ssp4sim"
    assert loaded.request.setup.ssp_root == setup.ssp_root
    assert loaded.result_path == request.result_path
    assert loaded.runtime_s == pytest.approx(0.25)


def test_compare_runs_writes_metrics_and_manifest(tmp_path: Path) -> None:
    ssp_root = make_ssp_root(tmp_path)
    spec = SimulationCaseSpec(
        model_name="ExampleModel",
        case_name="baseline",
        ssp_root=ssp_root,
        backends=("ssp4sim", "omsimulator", "fmpy"),
        compare_signals=("signal",),
    )
    setup = prepare_setup(spec)
    setup.write_manifest()

    left_request = SimulationRequest(setup=setup, backend="ssp4sim")
    right_request = SimulationRequest(setup=setup, backend="omsimulator")

    write_series(left_request.result_path, [0.0, 1.0])
    write_series(right_request.result_path, [0.0, 1.1])

    left_run = SimulationRun(request=left_request, result_path=left_request.result_path)
    right_run = SimulationRun(request=right_request, result_path=right_request.result_path)
    left_run.write_manifest()
    right_run.write_manifest()

    comparison = compare_runs(ComparisonRequest(run_a=left_run, run_b=right_run))

    assert comparison.manifest_path.exists()
    assert comparison.metrics_path.exists()
    assert comparison.summary["compared_signal_count"] == 1
    assert comparison.summary["max_abs_error"] == pytest.approx(0.1)

    loaded = ComparisonRun.from_manifest(comparison.manifest_path)
    assert loaded.summary == comparison.summary
    assert loaded.metrics_path == comparison.metrics_path

    payload = json.loads(comparison.manifest_path.read_text())
    assert set(payload["request"]) == {"case", "runs"}
    assert len(payload["request"]["runs"]) == 2


def test_compare_runs_normalizes_prefixed_signal_names(tmp_path: Path) -> None:
    ssp_root = make_ssp_root(tmp_path)
    spec = SimulationCaseSpec(
        model_name="ExampleModel",
        case_name="baseline",
        ssp_root=ssp_root,
        backends=("ssp4sim", "omsimulator"),
        compare_signals=("step.y",),
    )
    setup = prepare_setup(spec)
    setup.write_manifest()

    left_request = SimulationRequest(setup=setup, backend="ssp4sim")
    right_request = SimulationRequest(setup=setup, backend="omsimulator")

    write_prefixed_csv(left_request.result_path, "system.step.y", [0.0, 1.0])
    write_prefixed_csv(right_request.result_path, "root.system.step.y", [0.0, 1.0])

    left_run = SimulationRun(request=left_request, result_path=left_request.result_path)
    right_run = SimulationRun(request=right_request, result_path=right_request.result_path)
    left_run.write_manifest()
    right_run.write_manifest()

    comparison = compare_runs(ComparisonRequest(run_a=left_run, run_b=right_run))

    assert comparison.summary["compared_signal_count"] == 1
    assert comparison.summary["max_abs_error"] == pytest.approx(0.0)


def test_compare_runs_validates_signal_invariants(tmp_path: Path) -> None:
    ssp_root = make_ssp_root(tmp_path, model_name="signal_step_gain")
    spec = SimulationCaseSpec(
        model_name="signal_step_gain",
        case_name="baseline",
        ssp_root=ssp_root,
        backends=("ssp4sim", "omsimulator"),
        compare_signals=("step.y", "gain.y"),
    )
    setup = prepare_setup(spec)
    setup.write_manifest()

    left_request = SimulationRequest(setup=setup, backend="ssp4sim")
    right_request = SimulationRequest(setup=setup, backend="omsimulator")
    columns = {
        "step.y": [1.0, 3.0],
        "gain.y": [3.0, 9.0],
    }
    write_columns(left_request.result_path, columns)
    write_columns(right_request.result_path, columns)

    left_run = SimulationRun(request=left_request, result_path=left_request.result_path)
    right_run = SimulationRun(request=right_request, result_path=right_request.result_path)
    left_run.write_manifest()
    right_run.write_manifest()

    comparison = compare_runs(ComparisonRequest(run_a=left_run, run_b=right_run))

    assert comparison.summary["signal_invariant_count"] == 2
    assert comparison.summary["max_signal_invariant_abs_error"] == pytest.approx(0.0)


def test_compare_runs_fails_on_signal_invariant_violation(tmp_path: Path) -> None:
    ssp_root = make_ssp_root(tmp_path, model_name="signal_step_gain")
    spec = SimulationCaseSpec(
        model_name="signal_step_gain",
        case_name="baseline",
        ssp_root=ssp_root,
        backends=("ssp4sim", "omsimulator"),
        compare_signals=("step.y", "gain.y"),
    )
    setup = prepare_setup(spec)
    setup.write_manifest()

    left_request = SimulationRequest(setup=setup, backend="ssp4sim")
    right_request = SimulationRequest(setup=setup, backend="omsimulator")
    write_columns(
        left_request.result_path,
        {
            "step.y": [1.0, 3.0],
            "gain.y": [3.0, 9.0],
        },
    )
    write_columns(
        right_request.result_path,
        {
            "step.y": [1.0, 3.0],
            "gain.y": [3.0, 8.0],
        },
    )

    left_run = SimulationRun(request=left_request, result_path=left_request.result_path)
    right_run = SimulationRun(request=right_request, result_path=right_request.result_path)
    left_run.write_manifest()
    right_run.write_manifest()

    with pytest.raises(ValueError, match="Signal invariant failed"):
        compare_runs(ComparisonRequest(run_a=left_run, run_b=right_run))


def test_compare_run_batch_writes_results_for_multiple_backends(tmp_path: Path) -> None:
    ssp_root = make_ssp_root(tmp_path)
    spec = SimulationCaseSpec(
        model_name="ExampleModel",
        case_name="baseline",
        ssp_root=ssp_root,
        backends=("ssp4sim", "omsimulator", "fmpy"),
        compare_signals=("signal",),
    )
    setup = prepare_setup(spec)
    setup.write_manifest()

    requests = [
        SimulationRequest(setup=setup, backend="ssp4sim"),
        SimulationRequest(setup=setup, backend="omsimulator"),
        SimulationRequest(setup=setup, backend="fmpy"),
    ]
    write_series(requests[0].result_path, [0.0, 1.0])
    write_series(requests[1].result_path, [0.0, 1.1])
    write_series(requests[2].result_path, [0.0, 0.9])

    runs = tuple(SimulationRun(request=request, result_path=request.result_path) for request in requests)
    for run in runs:
        run.write_manifest()

    batch = compare_run_batch(ComparisonBatchRequest(runs=runs))

    assert batch.manifest_path.exists()
    assert batch.summary["backend_count"] == 3
    assert batch.summary["comparison_count"] == 3
    assert batch.summary["min_compared_signal_count"] == 1
    assert batch.summary["max_abs_error"] == pytest.approx(0.2)
    assert len(batch.comparisons) == 3

    loaded = ComparisonBatchRun.from_manifest(batch.manifest_path)
    assert loaded.summary == batch.summary
    assert len(loaded.comparisons) == 3

    payload = json.loads(batch.manifest_path.read_text())
    assert set(payload["request"]) == {"case", "model", "runs"}
    assert len(payload["request"]["runs"]) == 3
    assert len(payload["comparisons"]) == 3
    assert all("runs" in comparison for comparison in payload["comparisons"])
