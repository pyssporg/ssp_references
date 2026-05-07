from __future__ import annotations

import json
from pathlib import Path

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
from workflow.registry import RegistryCase, RegistryModel, SimulationCaseSpec, SimulationRegistry
from workflow.setup import prepare_setup
from workflow.simulate import SimulationRequest, SimulationRun, write_structured_csv


def make_ssp_root(tmp_path: Path) -> Path:
    ssp_root = tmp_path / "artifacts" / "models" / "ToyModel" / "baseline"
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
<Experiments name="ToyModel experiments">
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
    write_structured_csv(path, result)


def write_prefixed_csv(path: Path, signal_name: str, signal_values: list[float]) -> None:
    rows = ["time,{}".format(signal_name)]
    for index, value in enumerate(signal_values):
        rows.append(f"{float(index)},{value}")
    path.write_text("\n".join(rows) + "\n")


def test_registry_roundtrip_supports_multiple_models_and_cases() -> None:
    registry = SimulationRegistry(
        models=(
            RegistryModel(
                name="ToyModel",
                compare_signals=("signal",),
                cases=(
                    RegistryCase(name="baseline", backends=("ssp4sim", "omsimulator")),
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


def test_setup_manifest_roundtrip(tmp_path: Path) -> None:
    ssp_root = make_ssp_root(tmp_path)
    spec = SimulationCaseSpec(
        model_name="ToyModel",
        case_name="baseline",
        ssp_root=ssp_root,
        backends=("ssp4sim", "omsimulator"),
        compare_signals=("signal",),
    )

    setup = prepare_setup(spec)
    manifest_path = setup.write_manifest()

    assert manifest_path.exists()
    assert setup.model_name == "ToyModel"
    assert setup.case_name == "baseline"
    assert setup.window.start_time == pytest.approx(0.0)
    assert setup.window.stop_time == pytest.approx(1.0)
    assert setup.window.interval == pytest.approx(1.0)
    assert setup.tolerance == pytest.approx(0.0001)
    assert setup.description == "Baseline case"

    loaded = type(setup).from_manifest(manifest_path)
    assert loaded.ssp_root == ssp_root.resolve()
    assert loaded.model_name == "ToyModel"
    assert loaded.case_name == "baseline"
    assert loaded.backends == ("ssp4sim", "omsimulator")
    assert loaded.compare_signals == ("signal",)
    assert loaded.root_system_name == "system"
    assert loaded.window == setup.window
    assert loaded.tolerance == pytest.approx(setup.tolerance)


def test_simulation_run_manifest_roundtrip(tmp_path: Path) -> None:
    ssp_root = make_ssp_root(tmp_path)
    spec = SimulationCaseSpec(
        model_name="ToyModel",
        case_name="baseline",
        ssp_root=ssp_root,
        backends=("ssp4sim", "omsimulator"),
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
        model_name="ToyModel",
        case_name="baseline",
        ssp_root=ssp_root,
        backends=("ssp4sim", "omsimulator"),
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
        model_name="ToyModel",
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


def test_compare_run_batch_writes_results_for_multiple_backends(tmp_path: Path) -> None:
    ssp_root = make_ssp_root(tmp_path)
    spec = SimulationCaseSpec(
        model_name="ToyModel",
        case_name="baseline",
        ssp_root=ssp_root,
        backends=("ssp4sim", "omsimulator", "ecos"),
        compare_signals=("signal",),
    )
    setup = prepare_setup(spec)
    setup.write_manifest()

    requests = [
        SimulationRequest(setup=setup, backend="ssp4sim"),
        SimulationRequest(setup=setup, backend="omsimulator"),
        SimulationRequest(setup=setup, backend="ecos"),
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
