from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree as ET

from pyssp_standard import LSRefExperiments
from pyssp_workflow.params import read_study_descriptor

from utils.domain import SimulationWindow

from .gate import GateConfig
from .io import read_json, relative_path, resolve_path, write_json
from .layout import ArtifactLayout, LS_REF_EXPERIMENTS_RELATIVE
from .registry import SimulationCaseSpec


def _required_float(value: float | None, key: str, path: Path) -> float:
    if value is None:
        raise KeyError(f"Missing '{key}' in LS-REF experiment {path}")
    return float(value)


def _read_root_system_name(system_structure_path: Path) -> str:
    # Deliberately lenient: the SSD facade requires a conformant root
    # name/version, while setup only needs the first system name.
    if not system_structure_path.is_file():
        raise FileNotFoundError(f"System structure not found: {system_structure_path}")

    root = ET.parse(system_structure_path).getroot()
    system = root.find(".//{*}System")
    if system is None:
        raise ValueError(f"No system element found in {system_structure_path}")

    system_name = system.attrib.get("name")
    if not system_name:
        raise ValueError(f"System element in {system_structure_path} is missing a name")
    return str(system_name)


def read_experiment_window(ssp_root: Path, case_name: str) -> tuple[SimulationWindow, float, str | None]:
    experiments_path = ssp_root / LS_REF_EXPERIMENTS_RELATIVE
    if not experiments_path.is_file():
        raise FileNotFoundError(f"LS-REF experiments file not found: {experiments_path}")

    with LSRefExperiments(experiments_path, mode="r") as experiments:
        for experiment in experiments.xml.experiments:
            if experiment.name != case_name:
                continue

            return (
                SimulationWindow(
                    start_time=_required_float(
                        experiment.start_time, "startTime", experiments_path
                    ),
                    stop_time=_required_float(
                        experiment.stop_time, "stopTime", experiments_path
                    ),
                    interval=_required_float(
                        experiment.step_size, "stepSize", experiments_path
                    ),
                ),
                _required_float(
                    experiment.tolerance, "tolerance", experiments_path
                ),
                experiment.description,
            )

    raise ValueError(f"Experiment '{case_name}' not found in {experiments_path}")


@dataclass(frozen=True)
class SimulationSetup:
    layout: ArtifactLayout
    window: SimulationWindow
    tolerance: float
    backends: tuple[str, ...] = field(default_factory=tuple)
    compare_signals: tuple[str, ...] = field(default_factory=tuple)
    root_system_name: str = ""
    description: str | None = None
    gate: GateConfig = field(default_factory=GateConfig)
    study_name: str | None = None
    study_root: Path | None = None
    scenario_ssv: Path | None = None
    scenario_ssm: Path | None = None
    descriptor_path: Path | None = None

    def __post_init__(self) -> None:
        normalized_backends = tuple(str(backend).lower() for backend in self.backends)
        if not normalized_backends:
            raise ValueError("Simulation setup must declare at least one backend")
        object.__setattr__(self, "backends", normalized_backends)

        normalized_signals = tuple(str(signal).strip() for signal in self.compare_signals if str(signal).strip())
        if not normalized_signals:
            raise ValueError("Simulation setup must declare at least one compare signal")
        object.__setattr__(self, "compare_signals", normalized_signals)

        root_system_name = str(self.root_system_name).strip()
        if not root_system_name:
            raise ValueError("Simulation setup must declare a root system name")
        object.__setattr__(self, "root_system_name", root_system_name)

    @property
    def is_study(self) -> bool:
        return self.descriptor_path is not None

    @classmethod
    def from_spec(cls, spec: SimulationCaseSpec) -> "SimulationSetup":
        descriptor = (
            spec.study_root / "study.json"
            if spec.study_root is not None
            else None
        )
        if descriptor is not None and not descriptor.is_file():
            raise FileNotFoundError(f"Study descriptor not found: {descriptor}")
        if descriptor is not None:
            study = read_study_descriptor(descriptor)
            layout = ArtifactLayout.from_model_root(
                spec.model_name,
                study.study,
                spec.ssp_root,
                spec.study_root,
            )
            root_system_name = _read_root_system_name(layout.system_structure_path)
            return cls(
                layout=layout,
                window=SimulationWindow(
                    start_time=study.experiment.start_time,
                    stop_time=study.experiment.stop_time,
                    interval=study.experiment.step_size,
                ),
                tolerance=study.experiment.tolerance,
                backends=spec.backends,
                compare_signals=spec.compare_signals,
                root_system_name=root_system_name,
                gate=spec.gate,
                study_name=study.study,
                study_root=spec.study_root,
                scenario_ssv=study.ssv_path,
                scenario_ssm=study.ssm_path,
                descriptor_path=descriptor,
            )

        layout = ArtifactLayout.from_ssp_root(spec.ssp_root)
        if layout.model_name != spec.model_name or layout.case_name != spec.case_name:
            raise ValueError(
                "Registry spec does not match the SSP root layout: "
                f"{spec.model_name}/{spec.case_name} -> {spec.ssp_root}"
            )

        window, tolerance, description = read_experiment_window(spec.ssp_root, spec.case_name)
        root_system_name = _read_root_system_name(layout.system_structure_path)
        return cls(
            layout=layout,
            window=window,
            tolerance=tolerance,
            backends=spec.backends,
            compare_signals=spec.compare_signals,
            root_system_name=root_system_name,
            description=description,
            gate=spec.gate,
        )

    @classmethod
    def from_manifest(cls, path: Path) -> "SimulationSetup":
        data = read_json(path)
        manifest_root = path.parent
        study_root = (
            resolve_path(manifest_root, data["study_root"]).resolve()
            if data.get("study_root")
            else None
        )
        layout = ArtifactLayout(
            model_name=data["model"],
            case_name=data["case"],
            ssp_root=resolve_path(manifest_root, data["ssp_root"]).resolve(),
            study_root=study_root,
        )
        window = SimulationWindow(**data["window"])
        backends = data["backends"]
        if not isinstance(backends, list):
            raise TypeError("Simulation setup backends must be a list of backend names")
        compare_signals = data["compare_signals"]
        if not isinstance(compare_signals, list):
            raise TypeError("Simulation setup compare_signals must be a list of signal names")
        root_system_name = str(data.get("root_system_name") or _read_root_system_name(layout.system_structure_path))
        descriptor = (
            resolve_path(manifest_root, data["study_descriptor"])
            if data.get("study_descriptor")
            else None
        )
        return cls(
            layout=layout,
            window=window,
            tolerance=float(data["tolerance"]),
            backends=tuple(str(backend).lower() for backend in backends),
            compare_signals=tuple(str(signal).strip() for signal in compare_signals if str(signal).strip()),
            root_system_name=root_system_name,
            description=data.get("description"),
            gate=GateConfig.from_dict(data.get("gate")),
            study_name=data.get("study"),
            study_root=study_root,
            scenario_ssv=(
                resolve_path(manifest_root, data["scenario_ssv"])
                if data.get("scenario_ssv")
                else None
            ),
            scenario_ssm=(
                resolve_path(manifest_root, data["scenario_ssm"])
                if data.get("scenario_ssm")
                else None
            ),
            descriptor_path=descriptor,
        )

    @property
    def model_name(self) -> str:
        return self.layout.model_name

    @property
    def case_name(self) -> str:
        return self.layout.case_name

    @property
    def ssp_root(self) -> Path:
        return self.layout.ssp_root

    @property
    def manifest_path(self) -> Path:
        return self.layout.setup_manifest_path

    def to_dict(self) -> dict[str, object]:
        manifest_root = self.manifest_path.parent
        data: dict[str, object] = {
            "model": self.model_name,
            "case": self.case_name,
            "ssp_root": relative_path(manifest_root, self.ssp_root),
            "window": {
                "start_time": self.window.start_time,
                "stop_time": self.window.stop_time,
                "interval": self.window.interval,
            },
            "tolerance": self.tolerance,
            "backends": list(self.backends),
            "compare_signals": list(self.compare_signals),
            "root_system_name": self.root_system_name,
            "gate": self.gate.to_dict(),
            "system_structure": relative_path(manifest_root, self.layout.system_structure_path),
            "resources_dir": relative_path(manifest_root, self.layout.resources_dir),
        }
        if self.layout.ls_ref_experiments_path.is_file():
            data["ls_ref_experiments"] = relative_path(
                manifest_root, self.layout.ls_ref_experiments_path
            )
        if self.description is not None:
            data["description"] = self.description
        if self.study_name is not None:
            data["study"] = self.study_name
        if self.study_root is not None:
            data["study_root"] = relative_path(manifest_root, self.study_root)
        if self.descriptor_path is not None:
            data["study_descriptor"] = relative_path(manifest_root, self.descriptor_path)
        if self.scenario_ssv is not None:
            data["scenario_ssv"] = relative_path(manifest_root, self.scenario_ssv)
        if self.scenario_ssm is not None:
            data["scenario_ssm"] = relative_path(manifest_root, self.scenario_ssm)
        return data

    def write_manifest(self) -> Path:
        write_json(self.manifest_path, self.to_dict())
        return self.manifest_path


def prepare_setup(spec: SimulationCaseSpec) -> SimulationSetup:
    return SimulationSetup.from_spec(spec)
