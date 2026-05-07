from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from utils.config import REPO_ROOT


LS_REF_EXPERIMENTS_RELATIVE = Path("extra") / "org.fmi-standard.fmi-ls-ref" / "experiments.xml"


def sanitize_label(label: str) -> str:
    sanitized = []
    for character in label:
        sanitized.append(character if character.isalnum() or character in {"-", "_"} else "_")
    return "".join(sanitized).strip("_")


def comparison_run_name(run_a_label: str, run_b_label: str) -> str:
    return f"{sanitize_label(run_a_label)}_vs_{sanitize_label(run_b_label)}"


@dataclass(frozen=True)
class ArtifactLayout:
    model_name: str
    case_name: str
    ssp_root: Path

    @classmethod
    def from_ssp_root(cls, ssp_root: Path) -> "ArtifactLayout":
        resolved_root = ssp_root.resolve()
        if not resolved_root.exists():
            raise FileNotFoundError(f"SSP root not found: {resolved_root}")
        return cls(
            model_name=resolved_root.parent.name,
            case_name=resolved_root.name,
            ssp_root=resolved_root,
        )

    @property
    def artifact_root(self) -> Path:
        return REPO_ROOT / "artifacts"

    @property
    def simulation_case_root(self) -> Path:
        return (
            self.artifact_root
            / "simulation"
            / sanitize_label(self.model_name)
            / sanitize_label(self.case_name)
        )

    @property
    def comparison_case_root(self) -> Path:
        return (
            self.artifact_root
            / "comparisons"
            / sanitize_label(self.model_name)
            / sanitize_label(self.case_name)
        )

    @property
    def setup_manifest_path(self) -> Path:
        return self.simulation_case_root / "setup.json"

    @property
    def system_structure_path(self) -> Path:
        return self.ssp_root / "SystemStructure.ssd"

    @property
    def ls_ref_experiments_path(self) -> Path:
        return self.ssp_root / LS_REF_EXPERIMENTS_RELATIVE

    @property
    def resources_dir(self) -> Path:
        return self.ssp_root / "resources"

    def simulation_run_dir(self, backend: str) -> Path:
        return self.simulation_case_root / sanitize_label(backend)

    def simulation_manifest_path(self, backend: str) -> Path:
        return self.simulation_run_dir(backend) / "simulation.json"

    def simulation_result_path(self, backend: str) -> Path:
        return self.simulation_run_dir(backend) / "result.csv"

    def simulation_mat_path(self, backend: str) -> Path:
        return self.simulation_run_dir(backend) / "result.mat"

    def simulation_config_path(self, backend: str) -> Path:
        return self.simulation_run_dir(backend) / "config.json"

    def simulation_log_path(self, backend: str) -> Path:
        return self.simulation_run_dir(backend) / "simulation.log"

    def simulation_stdout_path(self, backend: str) -> Path:
        return self.simulation_run_dir(backend) / "stdout.log"

    def comparison_run_dir(self, run_a_backend: str, run_b_backend: str) -> Path:
        return self.comparison_case_root / comparison_run_name(run_a_backend, run_b_backend)

    def comparison_manifest_path(self, run_a_backend: str, run_b_backend: str) -> Path:
        return self.comparison_run_dir(run_a_backend, run_b_backend) / "comparison.json"

    def comparison_metrics_path(self, run_a_backend: str, run_b_backend: str) -> Path:
        return self.comparison_run_dir(run_a_backend, run_b_backend) / "metrics.csv"

    @property
    def comparison_batch_manifest_path(self) -> Path:
        return self.comparison_case_root / "comparisons.json"
