from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree as ET

from pyssp_workflow.analysis import read_analysis_descriptor

from utils.domain import SimulationWindow

from .gate import GateConfig
from .io import read_json, relative_path, resolve_path, write_json
from .layout import ArtifactLayout
from .registry import SimulationCaseSpec


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


@dataclass(frozen=True)
class SimulationSetup:
    layout: ArtifactLayout
    window: SimulationWindow
    tolerance: float | None = None
    backends: tuple[str, ...] = field(default_factory=tuple)
    compare_signals: tuple[str, ...] = field(default_factory=tuple)
    root_system_name: str = ""
    description: str | None = None
    gate: GateConfig = field(default_factory=GateConfig)
    analysis_name: str | None = None
    analysis_root: Path | None = None

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
    def is_analysis(self) -> bool:
        return self.analysis_root is not None

    @classmethod
    def from_spec(cls, spec: SimulationCaseSpec) -> "SimulationSetup":
        if spec.analysis_root is None:
            raise ValueError(
                f"Case '{spec.model_name}/{spec.case_name}' has no analysis descriptor; "
                "the analysis supplies the experiment window"
            )
        descriptor = spec.analysis_root / "analysis.json"
        if not descriptor.is_file():
            raise FileNotFoundError(f"Analysis descriptor not found: {descriptor}")

        analysis = read_analysis_descriptor(descriptor)
        layout = ArtifactLayout.from_model_root(
            spec.model_name,
            analysis.analysis,
            spec.ssp_root,
            spec.analysis_root,
        )
        root_system_name = _read_root_system_name(layout.system_structure_path)
        return cls(
            layout=layout,
            window=SimulationWindow(
                start_time=analysis.experiment.start_time,
                stop_time=analysis.experiment.stop_time,
                interval=analysis.experiment.step_size,
            ),
            backends=spec.backends,
            compare_signals=spec.compare_signals,
            root_system_name=root_system_name,
            gate=spec.gate,
            analysis_name=analysis.analysis,
            analysis_root=spec.analysis_root,
            description=analysis.description,
        )

    @classmethod
    def from_manifest(cls, path: Path) -> "SimulationSetup":
        data = read_json(path)
        manifest_root = path.parent
        analysis_root = (
            resolve_path(manifest_root, data["analysis_root"]).resolve()
            if data.get("analysis_root")
            else None
        )
        layout = ArtifactLayout(
            model_name=data["model"],
            case_name=data["case"],
            ssp_root=resolve_path(manifest_root, data["ssp_root"]).resolve(),
            analysis_root=analysis_root,
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
            tolerance=data.get("tolerance"),
            backends=tuple(str(backend).lower() for backend in backends),
            compare_signals=tuple(str(signal).strip() for signal in compare_signals if str(signal).strip()),
            root_system_name=root_system_name,
            description=data.get("description"),
            gate=GateConfig.from_dict(data.get("gate")),
            analysis_name=data.get("analysis"),
            analysis_root=analysis_root,
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
            "backends": list(self.backends),
            "compare_signals": list(self.compare_signals),
            "root_system_name": self.root_system_name,
            "gate": self.gate.to_dict(),
            "system_structure": relative_path(manifest_root, self.layout.system_structure_path),
            "resources_dir": relative_path(manifest_root, self.layout.resources_dir),
        }
        if self.tolerance is not None:
            data["tolerance"] = self.tolerance
        if self.description is not None:
            data["description"] = self.description
        if self.analysis_name is not None:
            data["analysis"] = self.analysis_name
        if self.analysis_root is not None:
            data["analysis_root"] = relative_path(manifest_root, self.analysis_root)
        return data

    def write_manifest(self) -> Path:
        write_json(self.manifest_path, self.to_dict())
        return self.manifest_path


def prepare_setup(spec: SimulationCaseSpec) -> SimulationSetup:
    return SimulationSetup.from_spec(spec)
