"""Integration test for the full build→simulate→compare pipeline."""

import shutil
from pathlib import Path

import numpy as np
import pytest

from pyssp_simulate.result import write_result_csv

from workflow.comparison import ComparisonBatchRequest, compare_run_batch
from workflow.registry import load_registry
from workflow.setup import prepare_setup
from workflow.simulate import SimulationRequest, SimulationRun


@pytest.fixture(autouse=True)
def isolated_repo_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Monkeypatches REPO_ROOT in all workflow modules to use tmp_path."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    monkeypatch.setattr("workflow.layout.REPO_ROOT", repo_root)
    monkeypatch.setattr("workflow.registry.REPO_ROOT", repo_root)
    monkeypatch.setattr("utils.config.REPO_ROOT", repo_root)


def test_full_pipeline_build_simulate_compare(tmp_path: Path) -> None:
    """Exercises build→simulate→compare for signal_step_gain within a single test function."""

    # === Stage 1: Build — copy real SSP artifacts into isolated repo ===
    repo = Path(__file__).resolve().parents[1]
    real_ssp_root = (
        repo / "artifacts" / "models" / "signal_step_gain" / "test_baseline" / "model"
    )
    real_study_root = (
        repo / "artifacts" / "studies" / "signal_step_gain" / "test_baseline"
    )
    isolated_ssp_root = (
        tmp_path
        / "repo"
        / "artifacts"
        / "models"
        / "signal_step_gain"
        / "test_baseline"
        / "model"
    )
    isolated_study_root = (
        tmp_path / "repo" / "artifacts" / "studies" / "signal_step_gain" / "test_baseline"
    )
    shutil.copytree(real_ssp_root, isolated_ssp_root)
    shutil.copytree(real_study_root, isolated_study_root)

    # Load real registry
    real_registry_path = (
        Path(__file__).resolve().parents[1] / "artifacts" / "simulation_registry.json"
    )
    registry = load_registry(real_registry_path)

    # === Stage 2: Simulate — set up and produce synthetic results ===
    specs = registry.expand(model_names=["signal_step_gain"])
    spec = specs[0]

    setup = prepare_setup(spec)
    setup.write_manifest()

    runs: list[SimulationRun] = []
    for backend in spec.backends:
        request = SimulationRequest(setup=setup, backend=backend)
        # Write 3-column CSV: time, step.y, gain.y
        result = np.array(
            [(0.0, 0.0, 0.0), (0.1, 1.0, 3.0), (0.2, 1.0, 3.0)],
            dtype=[("time", "f8"), ("step.y", "f8"), ("gain.y", "f8")],
        )
        write_result_csv(request.result_path, result)
        run = SimulationRun(request=request, result_path=request.result_path)
        run.write_manifest()
        runs.append(run)

    # === Stage 3: Compare ===
    batch = compare_run_batch(ComparisonBatchRequest(runs=tuple(runs)))

    # === Verify ===
    # All manifests exist
    assert setup.manifest_path.exists()
    for run in runs:
        assert run.manifest_path.exists()
        assert run.result_path.exists()
    assert batch.manifest_path.exists()
    for comp in batch.comparisons:
        assert comp.manifest_path.exists()
        assert comp.metrics_path.exists()

    # Comparison summary structure
    assert batch.summary["backend_count"] == 3
    assert batch.summary["comparison_count"] == 3
    assert batch.summary["gate_result"] in {"pass", "fail"}
