from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from utils.config import REPO_ROOT

from .io import read_json, write_json
from .layout import ArtifactLayout


def default_registry_path() -> Path:
    return REPO_ROOT / "artifacts" / "simulation_registry.json"


@dataclass(frozen=True)
class RegistryCase:
    name: str
    backends: tuple[str, ...]

    @classmethod
    def from_dict(cls, data: dict) -> "RegistryCase":
        backends = data.get("backends")
        if not isinstance(backends, list):
            raise TypeError("Registry case backends must be a list of backend names")
        normalized_backends = tuple(str(backend).lower() for backend in backends)
        if not normalized_backends:
            raise ValueError("Registry case backends must not be empty")
        return cls(
            name=str(data["name"]),
            backends=normalized_backends,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "backends": list(self.backends),
        }


@dataclass(frozen=True)
class RegistryModel:
    name: str
    compare_signals: tuple[str, ...]
    cases: tuple[RegistryCase, ...]

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
        return cls(
            name=str(data["name"]),
            compare_signals=normalized_compare_signals,
            cases=tuple(RegistryCase.from_dict(case) for case in cases),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "compare_signals": list(self.compare_signals),
            "cases": [case.to_dict() for case in self.cases],
        }


@dataclass(frozen=True)
class SimulationCaseSpec:
    model_name: str
    case_name: str
    ssp_root: Path
    backends: tuple[str, ...]
    compare_signals: tuple[str, ...]

    @property
    def layout(self) -> ArtifactLayout:
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

                ssp_root = REPO_ROOT / "artifacts" / "models" / model.name / case.name
                specs.append(
                    SimulationCaseSpec(
                        model_name=model.name,
                        case_name=case.name,
                        ssp_root=ssp_root,
                        backends=selected_backends,
                        compare_signals=model.compare_signals,
                    )
                )
        return specs


def load_registry(path: Path | None = None) -> SimulationRegistry:
    registry_path = path or default_registry_path()
    return SimulationRegistry.from_file(registry_path)
