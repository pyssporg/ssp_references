from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from pyssp_simulate import (
    SimulationResult,
    SimulationSpec,
    simulate,
)

from utils.domain import ResultSet
from utils.filesystem import reset_dir

from .io import read_json, relative_path, resolve_path, write_json
from .setup import SimulationSetup

#: OMSimulator command-line options this fixture suite requires. They keep
#: parameter values in the result CSV and tolerate the fixtures' initial
#: unknowns and input handling; the engine applies them process-wide.
OMS_OPTIONS = (
    "--ignoreInitialUnknowns=true",
    "--wallTime=true",
    "--emitEvents=false",
    "--inputExtrapolation=true",
    "--addParametersToCSV=true",
)


@dataclass(frozen=True)
class SimulationRequest:
    setup: SimulationSetup
    backend: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "backend", self.backend.lower())

    @property
    def run_dir(self) -> Path:
        return self.setup.layout.simulation_run_dir(self.backend)

    @property
    def manifest_path(self) -> Path:
        return self.setup.layout.simulation_manifest_path(self.backend)

    @property
    def result_path(self) -> Path:
        return self.setup.layout.simulation_result_path(self.backend)

    @property
    def config_path(self) -> Path:
        return self.setup.layout.simulation_config_path(self.backend)

    @property
    def log_path(self) -> Path:
        return self.setup.layout.simulation_log_path(self.backend)

    @property
    def stdout_path(self) -> Path:
        return self.setup.layout.simulation_stdout_path(self.backend)

    def to_dict(self) -> dict[str, object]:
        run_dir = self.run_dir
        return {
            "model": self.setup.model_name,
            "case": self.setup.case_name,
            "backend": self.backend,
            "setup_manifest": relative_path(run_dir, self.setup.manifest_path),
        }

    @classmethod
    def from_manifest(cls, path: Path) -> "SimulationRequest":
        data = read_json(path)
        payload = data.get("request", data)
        setup = SimulationSetup.from_manifest(resolve_path(path.parent, payload["setup_manifest"]))
        return cls(
            setup=setup,
            backend=payload["backend"],
        )


@dataclass(frozen=True)
class SimulationRun:
    request: SimulationRequest
    result_path: Path
    status: str = "completed"
    runtime_s: float | None = None
    error: str | None = None
    artifacts: tuple[Path, ...] = field(default_factory=tuple)

    @property
    def manifest_path(self) -> Path:
        return self.request.manifest_path

    @property
    def run_dir(self) -> Path:
        return self.request.run_dir

    def to_dict(self) -> dict[str, object]:
        run_dir = self.run_dir
        return {
            "request": self.request.to_dict(),
            "result": relative_path(run_dir, self.result_path),
            "artifacts": [relative_path(run_dir, path) for path in self.artifacts],
            "status": self.status,
            "runtime_s": self.runtime_s,
            "error": self.error,
        }

    def write_manifest(self) -> Path:
        write_json(self.manifest_path, self.to_dict())
        return self.manifest_path

    def to_result_set(self) -> ResultSet:
        return ResultSet(
            label=self.request.backend,
            path=self.result_path,
            engine=self.request.backend,
        )

    @classmethod
    def from_manifest(cls, path: Path) -> "SimulationRun":
        data = read_json(path)
        request = SimulationRequest.from_manifest(path)
        artifacts = tuple(resolve_path(path.parent, artifact) for artifact in data.get("artifacts", []))
        return cls(
            request=request,
            result_path=resolve_path(path.parent, data["result"]),
            status=data.get("status", "completed"),
            runtime_s=data.get("runtime_s"),
            error=data.get("error"),
            artifacts=artifacts,
        )


def _simulation_spec(request: SimulationRequest, ssp: Path) -> SimulationSpec:
    return SimulationSpec(
        ssp=ssp,
        start_time=request.setup.window.start_time,
        stop_time=request.setup.window.stop_time,
        step_size=request.setup.window.interval,
        tolerance=request.setup.tolerance,
        result_file=request.result_path,
        working_dir=request.run_dir,
        fixed_step=False,
        validate_ssd=False,
        omsimulator_options=OMS_OPTIONS,
    )


def simulate_backend(request: SimulationRequest) -> SimulationRun:
    """Run one backend against the built SSP.

    The study scenario is packaged into the SSP at build time, so the built
    artifact is the complete engine input; parameters are applied from the
    system definition only.
    """
    reset_dir(request.run_dir)
    result: SimulationResult = simulate(
        _simulation_spec(request, request.setup.ssp_root), backend=request.backend
    )

    artifacts = tuple(path for path in result.artifacts if path.is_file())
    run = SimulationRun(
        request=request,
        result_path=request.result_path,
        runtime_s=result.runtime_s,
        artifacts=artifacts,
    )
    run.write_manifest()
    return run
