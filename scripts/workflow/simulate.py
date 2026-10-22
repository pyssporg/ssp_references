from __future__ import annotations

import os
import tempfile
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

from pyssp_simulate import SimulationSpec, simulate
from pyssp_simulate.result import SimulationResult, read_result_csv, write_result_csv
from pyssp_simulate.runtime import prepare_runtime_ssp
from pyssp_standard.common.archive import package_archive
from pyssp_workflow.execute import inject_scenario
from pyssp_workflow.params import read_study_descriptor

from utils.domain import ResultSet
from utils.filesystem import reset_dir

from .engine_compat import configure_omsimulator, patched_fmpy_ssp_runtime
from .io import read_json, relative_path, resolve_path, write_json
from .setup import SimulationSetup


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
    )


@contextmanager
def _raw_ssp_archive(ssp_root: Path):
    """Zip an SSP root without rebuilding its unpacked FMU directories.

    ``pyssp_simulate`` repackages unpacked FMUs when it receives a directory.
    ssp4sim can load the unpacked layout directly, and at least one fixture
    depends on it, so ssp4sim gets an as-is archive instead.
    """
    with tempfile.TemporaryDirectory(prefix=f"{ssp_root.name}_") as temp_dir:
        archive = Path(temp_dir) / "runtime.ssp"
        package_archive(
            ssp_root,
            archive,
            recursive=False,
            overwrite=True,
        )
        yield archive


def _run_backend(
    request: SimulationRequest,
    ssp: Path,
    backend: str,
) -> SimulationRun:
    reset_dir(request.run_dir)
    start = time.perf_counter()
    result: SimulationResult = simulate(_simulation_spec(request, ssp), backend=backend)
    runtime_s = time.perf_counter() - start

    if not request.result_path.is_file():
        raise FileNotFoundError(
            f"{backend} did not write result CSV: {request.result_path}"
        )

    # ssp4sim writes graph diagnostics into its working directory. They are
    # not part of this repository's run contract, so keep the artifact
    # directory limited to result/config/log files.
    for name in ("graph_output.dot", "model_graph.dot", "tree_output.txt"):
        (request.run_dir / name).unlink(missing_ok=True)

    artifacts = tuple(path for path in result.artifacts if path.is_file())
    run = SimulationRun(
        request=request,
        result_path=request.result_path,
        runtime_s=result.runtime_s if result.runtime_s is not None else runtime_s,
        artifacts=artifacts,
    )
    run.write_manifest()
    return run


def simulate_ssp4sim(request: SimulationRequest, ssp_root: Path) -> SimulationRun:
    with _raw_ssp_archive(ssp_root) as runtime_ssp:
        return _run_backend(request, runtime_ssp, "ssp4sim")


@contextmanager
def _temporary_cwd(path: Path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def simulate_omsimulator(request: SimulationRequest, ssp_root: Path) -> SimulationRun:
    """Run OMSimulator without forcing a fixed step size.

    ``pyssp_simulate`` calls ``setFixedStepSize``, which suppresses event
    handling in event-driven fixtures such as BouncingBall. Keep the call
    local until the upstream backend makes the step mode configurable. The
    runtime archive and result CSV handling still come from ``pyssp_simulate``.
    """
    from OMSimulator import SSP as OMSSP, Settings

    reset_dir(request.run_dir)
    configure_omsimulator()
    Settings.suppressPath = True

    with prepare_runtime_ssp(ssp_root) as runtime:
        with _temporary_cwd(request.run_dir):
            model = OMSSP(str(runtime.archive))
            instance = model.instantiate()
            start = time.perf_counter()
            try:
                instance.setStartTime(request.setup.window.start_time)
                instance.setStopTime(request.setup.window.stop_time)
                instance.setLoggingInterval(request.setup.window.interval)
                instance.setResultFile(str(request.result_path))
                instance.initialize()
                instance.simulate()
                instance.terminate()
            finally:
                instance.delete()
            runtime_s = time.perf_counter() - start

        if not request.result_path.is_file():
            raise FileNotFoundError(
                f"OMSimulator did not write result CSV: {request.result_path}"
            )
        # Parse once so malformed or empty output fails in the simulation stage,
        # then leave the engine's own CSV untouched for comparison.
        read_result_csv(request.result_path, root_system=runtime.container_names)

    stray_result_dir = request.run_dir / "result"
    if stray_result_dir.exists():
        import shutil

        shutil.rmtree(stray_result_dir)

    run = SimulationRun(
        request=request,
        result_path=request.result_path,
        runtime_s=runtime_s,
    )
    run.write_manifest()
    return run


def _apply_fmpy_mapping(binding):
    """Resolve FMPy's externally loaded SSM into target-named parameters."""
    from fmpy.ssp.ssd import Parameter, ParameterSet

    if not binding.parameterValues:
        return None
    parameter_set = binding.parameterValues[0]
    mappings = [
        entry
        for mapping in binding.parameterMapping
        for entry in mapping.mappingEntries
    ]
    if not mappings:
        return parameter_set

    by_name = {parameter.name: parameter for parameter in parameter_set.parameters}
    resolved = ParameterSet(name=parameter_set.name)
    for entry in mappings:
        source = by_name.get(entry.source)
        if source is None:
            raise ValueError(
                f"FMPy mapping source '{entry.source}' is not present in "
                f"parameter set '{parameter_set.name}'"
            )
        resolved.parameters.append(
            Parameter(
                name=entry.target,
                type=source.type,
                value=source.value,
                unit=source.unit,
            )
        )
    return resolved


def simulate_fmpy(request: SimulationRequest, ssp_root: Path) -> SimulationRun:
    """Run FMPy with the SSP parameter bindings applied.

    ``pyssp_simulate``'s FMPy backend calls ``simulate_ssp`` without a
    parameter set, so SSV values are silently ignored. FMPy supports the
    argument, so pass the SSD's first parameter set explicitly and apply its
    external SSM mapping before simulation.
    """
    from fmpy.ssp.simulation import simulate_ssp
    from fmpy.ssp.ssd import read_ssd

    reset_dir(request.run_dir)
    with prepare_runtime_ssp(ssp_root) as runtime:
        with patched_fmpy_ssp_runtime():
            ssd = read_ssd(str(runtime.archive), validate=False)
            binding = next(
                (
                    candidate
                    for candidate in ssd.system.parameterBindings
                    if candidate.parameterValues
                ),
                None,
            )
            parameter_set = _apply_fmpy_mapping(binding) if binding is not None else None

            start = time.perf_counter()
            raw = simulate_ssp(
                str(runtime.archive),
                start_time=request.setup.window.start_time,
                stop_time=request.setup.window.stop_time,
                step_size=request.setup.window.interval,
                parameter_set=parameter_set,
            )
            runtime_s = time.perf_counter() - start

    write_result_csv(request.result_path, raw)
    if not request.result_path.is_file():
        raise FileNotFoundError(f"FMPy did not write result CSV: {request.result_path}")

    run = SimulationRun(
        request=request,
        result_path=request.result_path,
        runtime_s=runtime_s,
    )
    run.write_manifest()
    return run


def _simulate_backend(request: SimulationRequest, ssp_root: Path) -> SimulationRun:
    backend = request.backend.lower()
    if backend == "ssp4sim":
        return simulate_ssp4sim(request, ssp_root)
    if backend == "omsimulator":
        return simulate_omsimulator(request, ssp_root)
    if backend == "fmpy":
        return simulate_fmpy(request, ssp_root)
    raise NotImplementedError(f"Unsupported backend: {request.backend}")


def simulate_backend(request: SimulationRequest) -> SimulationRun:
    setup = getattr(request, "setup", None)
    if setup is None or setup.descriptor_path is None:
        return _simulate_backend(request, getattr(setup, "ssp_root", None))

    study = read_study_descriptor(setup.descriptor_path)
    with inject_scenario(
        setup.ssp_root,
        study.ssv_path,
        study.ssm_path,
        target_ssd=study.target_ssd,
    ) as runtime_root:
        return _simulate_backend(request, runtime_root)
