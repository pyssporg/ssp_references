from __future__ import annotations

import csv
import multiprocessing as mp
import os
import shutil
import time
from dataclasses import dataclass, field
from contextlib import contextmanager
from pathlib import Path
import tempfile
import zipfile
import sys
import traceback

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


def _fmpy_get_connections(system, connectors=None):
    """Resolve FMPy SSP connections for the generated runtime archive.

    FMPy's built-in resolver trips over some system-boundary connections in
    these fixtures, especially models like dcmotor that wire inputs/outputs
    through the root system. We mirror its traversal here and fix that branch
    so the runtime archive can be instantiated without changing the models.
    """
    from fmpy.ssp.ssd import System, build_path, find_connectors

    if connectors is None:
        connectors = {}
        for connector in find_connectors(system):
            connectors[build_path(connector)] = connector

    cons = []

    for connector in system.connectors:
        if connector.kind == "output":
            start_p = None
            end_p = None
            for connection in system.connections:
                if connection.endElement is None and connection.endConnector == connector.name:
                    start_p = build_path(system) + "." + connection.startElement + "." + connection.startConnector
                    end_p = build_path(connector)
                    break
                if connection.startElement is None and connection.startConnector == connector.name:
                    start_p = build_path(connector)
                    end_p = build_path(system) + "." + connection.endElement + "." + connection.endConnector
                    break
            if start_p is None or end_p is None:
                raise KeyError(f"Missing connection for connector {build_path(connector)}")
            cons.append((connectors[start_p], connectors[end_p]))

    for element in system.elements:
        for connector in element.connectors:
            if connector.kind == "input":
                end_p = build_path(element) + "." + connector.name
                start_p = None
                for connection in system.connections:
                    if connection.endElement == element.name and connection.endConnector == connector.name:
                        start_p = build_path(system)
                        if connection.startElement is not None:
                            start_p += "." + connection.startElement
                        start_p += "." + connection.startConnector
                        break
                    if connection.startElement == element.name and connection.startConnector == connector.name:
                        start_p = build_path(system)
                        if connection.endElement is not None:
                            start_p += "." + connection.endElement
                        start_p += "." + connection.endConnector
                        break
                if start_p is None:
                    raise KeyError(f"Missing connection for connector {build_path(element) + '.' + connector.name}")
                cons.append((connectors[start_p], connectors[end_p]))

    for element in system.elements:
        if isinstance(element, System):
            cons += _fmpy_get_connections(element, connectors=connectors)

    return cons


@contextmanager
def _patched_fmpy_ssp_runtime():
    """Temporarily relax FMPy's SSP loader for this repository's fixtures.

    The generated SSP archives are current enough for our other backends, but
    FMPy's loader still rejects some SSP 2.0 schema details. We therefore skip
    validation and swap in the local connection resolver above so boundary
    wiring continues to work for models that depend on it.
    """
    from fmpy.ssp import simulation as fmpy_simulation
    from fmpy.ssp import ssd as fmpy_ssd

    original_validate_tree = fmpy_ssd.validate_tree
    original_get_connections = fmpy_simulation.get_connections

    def _no_validate(*args, **kwargs):
        return None

    # Keep the patch scoped to the FMPy runtime call path only.
    fmpy_ssd.validate_tree = _no_validate
    fmpy_simulation.get_connections = _fmpy_get_connections
    try:
        yield
    finally:
        fmpy_ssd.validate_tree = original_validate_tree
        fmpy_simulation.get_connections = original_get_connections


def _run_fmpy_ssp(runtime_ssp_path: Path, setup: SimulationSetup):
    from fmpy.ssp.simulation import simulate_ssp

    with _patched_fmpy_ssp_runtime():
        return simulate_ssp(
            str(runtime_ssp_path),
            start_time=setup.window.start_time,
            stop_time=setup.window.stop_time,
            step_size=setup.window.interval,
        )


def _configure_omsimulator() -> None:
    from OMSimulator.capi import Capi, Status

    # The OMSimulator package already applies suppressPath while loading FMUs,
    # so only set the remaining historical options here.
    for option in (
        "--ignoreInitialUnknowns=true",
        "--wallTime=true",
        "--emitEvents=false",
        "--inputExtrapolation=true",
    ):
        status = Capi.setCommandLineOption(option)
        if status != Status.ok:
            raise RuntimeError(f"Failed to set OMSimulator command line option {option!r}: {status}")


def _ssp4sim_child_main(config_path: str) -> None:
    from pyssp4sim import Simulator

    try:
        simulator = Simulator(config_path)
        simulator.init()
        simulator.simulate()
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(0)
    except BaseException:
        traceback.print_exc()
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(1)


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
        process = mp.get_context("spawn").Process(
            target=_ssp4sim_child_main,
            args=(str(request.config_path),),
        )
        process.start()
        process.join()
        runtime_s = time.perf_counter() - start
        if process.exitcode != 0:
            raise RuntimeError(
                f"ssp4sim failed for {request.setup.model_name}/{request.setup.case_name} "
                f"with exit code {process.exitcode}"
            )

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
    _configure_omsimulator()
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


def simulate_fmpy(request: SimulationRequest) -> SimulationRun:
    reset_dir(request.run_dir)
    with _runtime_ssp_archive(request.setup.ssp_root) as runtime_ssp_path:
        start = time.perf_counter()
        result = _run_fmpy_ssp(runtime_ssp_path, request.setup)
        runtime_s = time.perf_counter() - start

    write_structured_csv(request.result_path, result)
    if not request.result_path.is_file():
        raise FileNotFoundError(f"FMPy did not write result CSV: {request.result_path}")

    run = SimulationRun(
        request=request,
        result_path=request.result_path,
        runtime_s=runtime_s,
    )
    run.write_manifest()
    return run


def simulate_backend(request: SimulationRequest) -> SimulationRun:
    backend = request.backend.lower()
    if backend == "ssp4sim":
        return simulate_ssp4sim(request)
    if backend == "omsimulator":
        return simulate_omsimulator(request)
    if backend == "fmpy":
        return simulate_fmpy(request)
    raise NotImplementedError(f"Unsupported backend: {request.backend}")
