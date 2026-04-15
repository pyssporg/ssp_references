from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .config import REPO_ROOT


@dataclass(frozen=True)
class ModelPaths:
    name: str
    model_dir: Path

    @property
    def ssp_path(self) -> Path:
        return self.model_dir / f"{self.name}.ssp"

    @property
    def unpacked_ssp_dir(self) -> Path:
        return self.model_dir / "ssp"

    @property
    def fmus_dir(self) -> Path:
        return self.model_dir / "fmus"

    @property
    def references_dir(self) -> Path:
        return self.model_dir / "references"

    def fmu_path(self, fmu_name: str | None = None) -> Path:
        actual_name = fmu_name or self.name
        return self.fmus_dir / f"{actual_name}.fmu"


class ModelMetaData:
    def __init__(self, model_dir: Path):
        self.dir = model_dir
        self.metadata = load_model_metadata(self.dir)
        self.name = self.metadata["model_name"]
        self.paths = model_paths(self.dir, self.name)
        self.source_ssp = resolve_metadata_paths(self.metadata["source"]["ssp"])
        self.source_fmu = resolve_metadata_paths(self.metadata["source"]["fmu"])
        self.source_results = resolve_metadata_paths(self.metadata["source"].get("results", []))


def model_paths(model_dir: Path, model_name: str) -> ModelPaths:
    return ModelPaths(name=model_name, model_dir=model_dir)


def load_model_metadata(model_dir: Path) -> dict:
    metadata_path = model_dir / "metadata.json"
    if not metadata_path.is_file():
        raise FileNotFoundError(f"Model metadata not found: {metadata_path}")
    return json.loads(metadata_path.read_text())


def resolve_metadata_paths(entries: list[str]) -> list[Path]:
    return [REPO_ROOT / entry for entry in entries]


def require_single_source(entries: list[Path], source_type: str) -> Path:
    if len(entries) != 1:
        raise ValueError(f"Expected exactly one {source_type} source entry, found {len(entries)}")
    return entries[0]
