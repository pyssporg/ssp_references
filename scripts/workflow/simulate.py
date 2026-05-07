from __future__ import annotations

import csv
import os
import shutil
import time
from dataclasses import dataclass, field
from contextlib import contextmanager
from pathlib import Path
import tempfile
import zipfile

from utils.filesystem import reset_dir
from utils.config import REPO_ROOT

from .io import read_json, relative_path, resolve_path, write_json
from .setup import SimulationSetup


@dataclass(frozen=True)
class ResultSet:
    label: str
    path: Path
    engine: str


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
    def result_mat_path(self) -> Path:
        return self.setup.layout.simulation_mat_path(self.backend)

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


def write_structured_csv(path: Path, result) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    headers = list(result.dtype.names or ())
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        for row in result:
            writer.writerow([row[name] for name in headers])


def _ssp4sim_config_payload(
    setup: SimulationSetup,
    *,
    ssp_root: Path,
    result_file: Path,
    log_file: Path,
) -> dict[str, object]:
    return {
        "simulation": {
            "ssp": str(ssp_root.resolve()),
            "ssd": "SystemStructure.ssd",
            "start_time": setup.window.start_time,
            "stop_time": setup.window.stop_time,
            "timestep": setup.window.interval,
            "tolerance": setup.tolerance,
            "realtime": False,
            "working_dir": str(result_file.parent.resolve()),
            "executor": {
                "method": "jacobi",
                "thread_pool_workers": 5,
                "forward_derivatives": True,
                "sub_step": setup.window.interval,
                "jacobi": {
                    "parallel": True,
                    "method": 1,
                },
                "seidel": {
                    "parallel": False,
                },
            },
            "recording": {
                # Keep the legacy recorder keys alongside the newer nested CSV
                # shape so the adapter works with both installed package
                # versions and the current upstream source layout.
                "enable": True,
                "wait_for": True,
                "interval": setup.window.interval,
                "result_file": str(result_file),
                "csv": {
                    "enable": True,
                    "file": str(result_file),
                    "interval": setup.window.interval,
                },
                "influx": {
                    "enable": False,
                },
            },
            "log": {
                "file": str(log_file),
                "level_terminal": "error",
                "level_file": "info",
                "level_json": "disable",
                "level_cutelog": "disable",
                "fmu": False,
            },
        }
    }


@contextmanager
def _runtime_ssp_copy(ssp_root: Path):
    with tempfile.TemporaryDirectory(prefix=f"{ssp_root.name}_") as temp_dir:
        runtime_ssp_root = Path(temp_dir) / "ssp"
        shutil.copytree(ssp_root, runtime_ssp_root)
        yield runtime_ssp_root


def _package_unpacked_fmu(fmu_dir: Path, fmu_path: Path) -> None:
    with zipfile.ZipFile(fmu_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in fmu_dir.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(fmu_dir))


@contextmanager
def _temporary_cwd(path: Path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


@contextmanager
def _runtime_ssp_archive(ssp_root: Path):
    with tempfile.TemporaryDirectory(prefix=f"{ssp_root.name}_") as temp_dir:
        runtime_ssp_root = Path(temp_dir) / "ssp"
        shutil.copytree(ssp_root, runtime_ssp_root)

        resources_dir = runtime_ssp_root / "resources"
        if resources_dir.exists():
            fmu_roots = sorted(
                (path.parent for path in resources_dir.rglob("modelDescription.xml")),
                key=lambda path: len(path.parts),
                reverse=True,
            )
            for fmu_root in fmu_roots:
                fmu_path = fmu_root.with_suffix(".fmu")
                _package_unpacked_fmu(fmu_root, fmu_path)
                shutil.rmtree(fmu_root)

            references_dir = runtime_ssp_root / "references"
            references_dir.mkdir(parents=True, exist_ok=True)
            for source_path in resources_dir.rglob("*"):
                if source_path.is_file() and source_path.suffix in {".csv", ".ssm"}:
                    shutil.copy2(source_path, references_dir / source_path.name)

        runtime_ssp_path = Path(temp_dir) / "runtime.ssp"
        with zipfile.ZipFile(runtime_ssp_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in runtime_ssp_root.rglob("*"):
                if path.is_file():
                    archive.write(path, path.relative_to(runtime_ssp_root))

        yield runtime_ssp_path


def simulate_ssp4sim(request: SimulationRequest) -> SimulationRun:
    from pyssp4sim import Simulator

    reset_dir(request.run_dir)
    with _runtime_ssp_copy(request.setup.ssp_root) as runtime_ssp_root:
        write_json(
            request.config_path,
            _ssp4sim_config_payload(
                request.setup,
                ssp_root=runtime_ssp_root,
                result_file=request.result_path,
                log_file=request.log_path,
            ),
        )

        start = time.perf_counter()
        simulator = Simulator(str(request.config_path))
        simulator.init()
        simulator.simulate()
        del simulator
        runtime_s = time.perf_counter() - start

    if not request.result_path.is_file():
        raise FileNotFoundError(f"ssp4sim did not write result CSV: {request.result_path}")

    run = SimulationRun(
        request=request,
        result_path=request.result_path,
        runtime_s=runtime_s,
        artifacts=(request.config_path, request.log_path),
    )
    run.write_manifest()
    return run


def simulate_omsimulator(request: SimulationRequest) -> SimulationRun:
    from OMSimulator import SSP, Settings

    reset_dir(request.run_dir)
    repo_result_dir = REPO_ROOT / "result"
    if repo_result_dir.exists():
        shutil.rmtree(repo_result_dir)
    Settings.suppressPath = True
    with _temporary_cwd(request.run_dir):
        with _runtime_ssp_archive(request.setup.ssp_root) as runtime_ssp_path:
            model = SSP(str(runtime_ssp_path))
            instantiated_model = model.instantiate()

            start = time.perf_counter()
            try:
                instantiated_model.setStartTime(request.setup.window.start_time)
                instantiated_model.setStopTime(request.setup.window.stop_time)
                instantiated_model.setLoggingInterval(request.setup.window.interval)
                instantiated_model.setResultFile(str(request.result_mat_path))
                instantiated_model.initialize()
                instantiated_model.simulate()
                instantiated_model.terminate()
            finally:
                instantiated_model.delete()
            runtime_s = time.perf_counter() - start

    from utils.csv import unpack_mat_to_csv

    unpack_mat_to_csv(request.result_mat_path, request.result_path)
    stray_result_dir = request.run_dir / "result"
    if stray_result_dir.exists():
        shutil.rmtree(stray_result_dir)
    if not request.result_path.is_file():
        raise FileNotFoundError(f"OMSimulator did not write result CSV: {request.result_path}")

    run = SimulationRun(
        request=request,
        result_path=request.result_path,
        runtime_s=runtime_s,
        artifacts=(request.result_mat_path,),
    )
    run.write_manifest()
    return run


def simulate_backend(request: SimulationRequest) -> SimulationRun:
    backend = request.backend.lower()
    if backend == "ssp4sim":
        return simulate_ssp4sim(request)
    if backend == "omsimulator":
        return simulate_omsimulator(request)
    raise NotImplementedError(f"Unsupported backend: {request.backend}")
