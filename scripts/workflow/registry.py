from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

from utils.config import REPO_ROOT

from .gate import GateConfig
from .io import read_json, write_json
from .layout import ArtifactLayout


def default_registry_path() -> Path:
    return REPO_ROOT / "artifacts" / "simulation_registry.json"


@dataclass(frozen=True)
class RegistryReferenceCsv:
    label: str
    path: Path
    gate: bool = True

    @classmethod
    def from_dict(cls, data: dict) -> "RegistryReferenceCsv":
        return cls(
            label=str(data["label"]),
            path=Path(str(data["path"])),
            gate=bool(data.get("gate", True)),
        )

    def to_dict(self) -> dict[str, object]:
        data: dict[str, object] = {
            "label": self.label,
            "path": self.path.as_posix(),
        }
        if not self.gate:
            data["gate"] = False
        return data


@dataclass(frozen=True)
class RegistryCase:
    name: str
    backends: tuple[str, ...]
    analysis: str | None = None
    reference_csvs: tuple[RegistryReferenceCsv, ...] = ()
    gate: GateConfig = field(default_factory=GateConfig)

    @classmethod
    def from_dict(cls, data: dict) -> "RegistryCase":
        backends = data.get("backends")
        if not isinstance(backends, list):
            raise TypeError("Registry case backends must be a list of backend names")
        normalized_backends = tuple(str(backend).lower() for backend in backends)
        if not normalized_backends:
            raise ValueError("Registry case backends must not be empty")
        analysis = data.get("analysis")
        return cls(
            name=str(data["name"]),
            backends=normalized_backends,
            analysis=str(analysis) if analysis is not None else None,
            reference_csvs=tuple(
                RegistryReferenceCsv.from_dict(reference)
                for reference in data.get("reference_csvs", [])
            ),
            gate=GateConfig.from_dict(data.get("gate")),
        )

    def to_dict(self) -> dict[str, object]:
        data: dict[str, object] = {
            "name": self.name,
            "backends": list(self.backends),
        }
        if self.analysis is not None:
            data["analysis"] = self.analysis
        if self.reference_csvs:
            data["reference_csvs"] = [reference.to_dict() for reference in self.reference_csvs]
        if self.gate != GateConfig():
            data["gate"] = self.gate.to_dict()
        return data


@dataclass(frozen=True)
class RegistryModel:
    name: str
    compare_signals: tuple[str, ...]
    cases: tuple[RegistryCase, ...]
    build: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "RegistryModel":
        compare_signals = data.get("compare_signals")
        if not isinstance(compare_signals, list):
            raise TypeError("Registry model compare_signals must be a list")
        normalized_compare_signals = tuple(str(signal).strip() for signal in compare_signals if str(signal).strip())
        if not normalized_compare_signals:
            raise ValueError("Registry model compare_signals must not be empty")

        cases = data.get("cases")
        if not isinstance(cases, list):
            raise TypeError("Registry model cases must be a list")
        build = data.get("build")
        return cls(
            name=str(data["name"]),
            compare_signals=normalized_compare_signals,
            cases=tuple(RegistryCase.from_dict(case) for case in cases),
            build=str(build) if build is not None else None,
        )

    def to_dict(self) -> dict[str, object]:
        data: dict[str, object] = {
            "name": self.name,
            "compare_signals": list(self.compare_signals),
            "cases": [case.to_dict() for case in self.cases],
        }
        if self.build is not None:
            data["build"] = self.build
        return data


@dataclass(frozen=True)
class SimulationCaseSpec:
    model_name: str
    case_name: str
    ssp_root: Path
    backends: tuple[str, ...]
    compare_signals: tuple[str, ...]
    reference_csvs: tuple[RegistryReferenceCsv, ...] = ()
    gate: GateConfig = field(default_factory=GateConfig)
    build_name: str | None = None
    analysis_name: str | None = None
    analysis_root: Path | None = None

    @property
    def is_analysis_case(self) -> bool:
        return self.analysis_root is not None and self.analysis_name is not None

    @property
    def layout(self) -> ArtifactLayout:
        if self.is_analysis_case:
            return ArtifactLayout.from_model_root(
                self.model_name,
                self.analysis_name,
                self.ssp_root,
                self.analysis_root,
            )
        return ArtifactLayout.from_ssp_root(self.ssp_root)


@dataclass(frozen=True)
class SimulationRegistry:
    models: tuple[RegistryModel, ...]

    @classmethod
    def from_dict(cls, data: dict) -> "SimulationRegistry":
        raw_models = data.get("models", [])
        if not isinstance(raw_models, list):
            raise TypeError("Registry models must be a list")

        return cls(
            models=tuple(RegistryModel.from_dict(item) for item in raw_models),
        )

    @classmethod
    def from_file(cls, path: Path) -> "SimulationRegistry":
        return cls.from_dict(read_json(path))

    def to_dict(self) -> dict[str, object]:
        return {
            "models": [model.to_dict() for model in self.models],
        }

    def write(self, path: Path) -> Path:
        write_json(path, self.to_dict())
        return path

    def expand(
        self,
        *,
        model_names: Sequence[str] | None = None,
        case_names: Sequence[str] | None = None,
        backend_names: Sequence[str] | None = None,
    ) -> list[SimulationCaseSpec]:
        model_filter = set(model_names or ())
        case_filter = set(case_names or ())
        backend_filter = {str(name).lower() for name in (backend_names or ())}
        specs: list[SimulationCaseSpec] = []

        for model in self.models:
            if model_filter and model.name not in model_filter:
                continue
            for case in model.cases:
                if case_filter and case.name not in case_filter:
                    continue
                selected_backends = tuple(
                    backend
                    for backend in case.backends
                    if not backend_filter or backend in backend_filter
                )
                if not selected_backends:
                    continue

                if model.build is not None or case.analysis is not None:
                    build_name = model.build or "model"
                    analysis_name = case.analysis or case.name
                    ssp_root = (
                        REPO_ROOT
                        / "artifacts"
                        / "models"
                        / model.name
                        / analysis_name
                        / build_name
                    )
                    analysis_root = (
                        REPO_ROOT
                        / "artifacts"
                        / "analyses"
                        / model.name
                        / analysis_name
                    )
                else:
                    build_name = None
                    analysis_name = None
                    ssp_root = (
                        REPO_ROOT / "artifacts" / "models" / model.name / case.name
                    )
                    analysis_root = None

                specs.append(
                    SimulationCaseSpec(
                        model_name=model.name,
                        case_name=case.name,
                        ssp_root=ssp_root,
                        backends=selected_backends,
                        compare_signals=model.compare_signals,
                        reference_csvs=case.reference_csvs,
                        gate=case.gate,
                        build_name=build_name,
                        analysis_name=analysis_name,
                        analysis_root=analysis_root,
                    )
                )
        return specs


def load_registry(path: Path | None = None) -> SimulationRegistry:
    registry_path = path or default_registry_path()
    return SimulationRegistry.from_file(registry_path)
