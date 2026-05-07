from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree as ET

from .io import read_json, relative_path, resolve_path, write_json
from .layout import ArtifactLayout, LS_REF_EXPERIMENTS_RELATIVE
from .registry import SimulationCaseSpec


@dataclass(frozen=True)
class SimulationWindow:
    start_time: float
    stop_time: float
    interval: float


def _parse_float(attributes: dict[str, str], key: str, path: Path) -> float:
    if key not in attributes:
        raise KeyError(f"Missing '{key}' in LS-REF experiment {path}")
    return float(attributes[key])


def _read_root_system_name(system_structure_path: Path) -> str:
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

    root = ET.parse(experiments_path).getroot()
    for experiment in root.findall(".//{*}Experiment"):
        if experiment.attrib.get("name") != case_name:
            continue

        start_time = _parse_float(experiment.attrib, "startTime", experiments_path)
        stop_time = _parse_float(experiment.attrib, "stopTime", experiments_path)
        interval = _parse_float(experiment.attrib, "stepSize", experiments_path)
        tolerance = _parse_float(experiment.attrib, "tolerance", experiments_path)
        description = experiment.attrib.get("description")
        return (
            SimulationWindow(
                start_time=start_time,
                stop_time=stop_time,
                interval=interval,
            ),
            tolerance,
            description,
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

    @classmethod
    def from_spec(cls, spec: SimulationCaseSpec) -> "SimulationSetup":
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
        )

    @classmethod
    def from_manifest(cls, path: Path) -> "SimulationSetup":
        data = read_json(path)
        manifest_root = path.parent
        layout = ArtifactLayout(
            model_name=data["model"],
            case_name=data["case"],
            ssp_root=resolve_path(manifest_root, data["ssp_root"]).resolve(),
        )
        window = SimulationWindow(**data["window"])
        backends = data["backends"]
        if not isinstance(backends, list):
            raise TypeError("Simulation setup backends must be a list of backend names")
        compare_signals = data["compare_signals"]
        if not isinstance(compare_signals, list):
            raise TypeError("Simulation setup compare_signals must be a list of signal names")
        root_system_name = str(data.get("root_system_name") or _read_root_system_name(layout.system_structure_path))
        return cls(
            layout=layout,
            window=window,
            tolerance=float(data["tolerance"]),
            backends=tuple(str(backend).lower() for backend in backends),
            compare_signals=tuple(str(signal).strip() for signal in compare_signals if str(signal).strip()),
            root_system_name=root_system_name,
            description=data.get("description"),
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
            "system_structure": relative_path(manifest_root, self.layout.system_structure_path),
            "ls_ref_experiments": relative_path(manifest_root, self.layout.ls_ref_experiments_path),
            "resources_dir": relative_path(manifest_root, self.layout.resources_dir),
        }
        if self.description is not None:
            data["description"] = self.description
        return data

    def write_manifest(self) -> Path:
        write_json(self.manifest_path, self.to_dict())
        return self.manifest_path


def prepare_setup(spec: SimulationCaseSpec) -> SimulationSetup:
    return SimulationSetup.from_spec(spec)
