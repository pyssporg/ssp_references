from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from workflow.layout import ArtifactLayout
from workflow.setup import SimulationSetup, SimulationWindow
from workflow.simulate import (
    OMS_OPTIONS,
    SimulationRequest,
    _simulation_spec,
    simulate_backend,
)


@pytest.fixture(autouse=True)
def isolated_repo_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    monkeypatch.setattr("workflow.layout.REPO_ROOT", repo_root)
    monkeypatch.setattr("utils.config.REPO_ROOT", repo_root)


def _request(tmp_path: Path, backend: str = "ssp4sim") -> SimulationRequest:
    ssp_root = tmp_path / "ssp_root"
    ssp_root.mkdir(parents=True, exist_ok=True)
    (ssp_root / "SystemStructure.ssd").write_text("<ssd:SystemStructureDescription />")
    layout = ArtifactLayout(model_name="TestModel", case_name="testcase", ssp_root=ssp_root)
    window = SimulationWindow(start_time=1.0, stop_time=11.0, interval=0.1)
    setup = SimulationSetup(
        layout=layout,
        window=window,
        tolerance=1e-5,
        backends=("ssp4sim",),
        compare_signals=("signal",),
        root_system_name="system",
    )
    return SimulationRequest(setup=setup, backend=backend)


def test_simulation_spec_maps_setup(tmp_path: Path) -> None:
    """R-003: The adapter maps the frozen setup into a pyssp_simulate spec.

    Backward trace: IMP-015 contract R-003.
    """
    request = _request(tmp_path)

    spec = _simulation_spec(request, request.setup.ssp_root)

    assert spec.ssp == request.setup.ssp_root
    assert spec.start_time == pytest.approx(1.0)
    assert spec.stop_time == pytest.approx(11.0)
    assert spec.step_size == pytest.approx(0.1)
    assert spec.tolerance == pytest.approx(1e-5)
    assert spec.result_file == request.result_path
    assert spec.working_dir == request.run_dir
    assert spec.fixed_step is False
    assert spec.validate_ssd is False
    assert spec.omsimulator_options == OMS_OPTIONS


def test_simulate_backend_delegates_to_pyssp_simulate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """R-007: The adapter hands the spec to pyssp_simulate and records the run."""
    request = _request(tmp_path)
    artifact = request.run_dir / "ssp4sim.log"
    calls: list[tuple[object, str]] = []

    def fake_simulate(spec, backend):
        calls.append((spec, backend))
        return SimpleNamespace(runtime_s=1.5, artifacts=(artifact, tmp_path / "missing.log"))

    def ensure_run_dir_artifact(*args, **kwargs):
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text("log")

    monkeypatch.setattr("workflow.simulate.simulate", fake_simulate)
    monkeypatch.setattr("workflow.simulate.reset_dir", ensure_run_dir_artifact)

    run = simulate_backend(request)

    assert len(calls) == 1
    spec, backend = calls[0]
    assert backend == "ssp4sim"
    assert spec == _simulation_spec(request, request.setup.ssp_root)
    assert run.runtime_s == pytest.approx(1.5)
    assert run.artifacts == (artifact,)
    assert run.manifest_path.is_file()
