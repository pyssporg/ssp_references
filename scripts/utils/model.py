from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import REPO_ROOT

FIXED_GENERATION_DATE_AND_TIME = "1970-01-01T00:00:00Z"


@dataclass(frozen=True)
class ModelPaths:
    name: str
    model_dir: Path

    @property
    def source_ssp_dir(self) -> Path:
        return self.model_dir / "ssp"

    @property
    def build_dir(self) -> Path:
        return REPO_ROOT / "build" / "models" / self.name

    @property
    def ssp_path(self) -> Path:
        return self.build_dir / f"{self.name}.ssp"

    @property
    def unpacked_ssp_dir(self) -> Path:
        return self.build_dir / "ssp"

    @property
    def fmus_dir(self) -> Path:
        return self.build_dir / "fmus"

    @property
    def references_dir(self) -> Path:
        return self.build_dir / "references"

    @property
    def shared_fmu_models_dir(self) -> Path:
        return REPO_ROOT / "models" / "fmu"

    @property
    def reference_results_dir(self) -> Path:
        return self.shared_fmu_models_dir / self.name / "references"

    @property
    def simulation_results_dir(self) -> Path:
        return self.build_dir / "simulation_results"

    @property
    def comparisons_dir(self) -> Path:
        return self.simulation_results_dir / "comparisons"

    def engine_results_dir(self, engine_name: str) -> Path:
        return self.simulation_results_dir / engine_name

    def fmu_path(self, fmu_name: str | None = None) -> Path:
        actual_name = fmu_name or self.name
        return self.fmus_dir / f"{actual_name}.fmu"

    def shared_fmu_dir(self, fmu_name: str | None = None) -> Path:
        actual_name = fmu_name or self.name
        return self.shared_fmu_models_dir / actual_name / "fmu"


class ModelMetaData:
    def __init__(self, model_dir: Path):
        self.dir = model_dir
        self.name = self.dir.name
        self.paths = model_paths(self.dir, self.name)


def model_paths(model_dir: Path, model_name: str) -> ModelPaths:
    return ModelPaths(name=model_name, model_dir=model_dir)

