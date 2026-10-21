"""Compare a simulation run against a trusted reference CSV.

Engine-to-engine comparison answers "do the backends agree?". Reference
comparison answers "does this run match the trusted baseline?", which is the
primary VV gate for fixtures that ship a reference trajectory.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from pyssp_simulate import SimulationResult

from utils.comparison import compare_column_sets, signal_invariant_metrics, write_metrics_csv
from utils.csv import load_numeric_csv

from .gate import GateOutcome, evaluate_gate
from .io import read_json, relative_path, resolve_path, write_json
from .registry import RegistryReferenceCsv
from .simulate import SimulationRun


def load_reference_columns(path: Path, model_name: str) -> dict[str, np.ndarray]:
    """Load a reference CSV and strip its ``default.<model>.`` prefixes."""
    if hasattr(SimulationResult, "from_reference_csv"):
        result = SimulationResult.from_reference_csv(path, model_name=model_name)
        return {name: result.data[name] for name in result.data.dtype.names or ()}

    # pyssp_simulate 0.1.0 predates the reference loader.
    data = load_numeric_csv(path)["columns"]
    prefix = f"default.{model_name}."
    columns: dict[str, np.ndarray] = {}
    for name, values in data.items():
        canonical = "time" if name == "time" else name[len(prefix) :] if name.startswith(prefix) else name
        if canonical not in columns:
            columns[canonical] = values
    return columns


@dataclass(frozen=True)
class ReferenceComparisonRequest:
    run: SimulationRun
    reference: RegistryReferenceCsv
    reference_path: Path

    @property
    def gate_enabled(self) -> bool:
        return self.reference.gate

    @property
    def label(self) -> str:
        return self.reference.label

    @property
    def run_dir(self) -> Path:
        return self.run.request.setup.layout.reference_comparison_dir(
            self.run.request.backend, self.label
        )

    @property
    def manifest_path(self) -> Path:
        return self.run.request.setup.layout.reference_comparison_manifest_path(
            self.run.request.backend, self.label
        )

    @property
    def metrics_path(self) -> Path:
        return self.run.request.setup.layout.reference_comparison_metrics_path(
            self.run.request.backend, self.label
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "backend": self.run.request.backend,
            "reference": self.label,
            "reference_gate": self.gate_enabled,
            "run_manifest": relative_path(self.run_dir, self.run.manifest_path),
            "reference_path": str(self.reference_path),
        }

    @classmethod
    def from_manifest(cls, path: Path) -> "ReferenceComparisonRequest":
        data = read_json(path)
        payload = data.get("request", data)
        run = SimulationRun.from_manifest(
            resolve_path(path.parent, payload["run_manifest"])
        )
        return cls(
            run=run,
            reference=RegistryReferenceCsv(
                label=str(payload["reference"]),
                path=Path(str(payload["reference_path"])),
                gate=bool(payload.get("reference_gate", True)),
            ),
            reference_path=resolve_path(path.parent, payload["reference_path"]),
        )


@dataclass(frozen=True)
class ReferenceComparisonRun:
    request: ReferenceComparisonRequest
    summary: dict[str, float | int | str]
    metrics_path: Path
    status: str = "completed"
    error: str | None = None
    gate: GateOutcome = GateOutcome(status="not_evaluated")

    @property
    def manifest_path(self) -> Path:
        return self.request.manifest_path

    def to_dict(self) -> dict[str, object]:
        return {
            "request": self.request.to_dict(),
            "summary": self.summary,
            "metrics": relative_path(self.request.run_dir, self.metrics_path),
            "status": self.status,
            "error": self.error,
            "gate": self.gate.to_dict(),
        }

    def write_manifest(self) -> Path:
        write_json(self.manifest_path, self.to_dict())
        return self.manifest_path

    @classmethod
    def from_manifest(cls, path: Path) -> "ReferenceComparisonRun":
        data = read_json(path)
        request = ReferenceComparisonRequest.from_manifest(path)
        return cls(
            request=request,
            summary=data["summary"],
            metrics_path=resolve_path(path.parent, data["metrics"]),
            status=data.get("status", "completed"),
            error=data.get("error"),
            gate=GateOutcome(
                status=str(data.get("gate", {}).get("status", "not_evaluated")),
                reasons=tuple(data.get("gate", {}).get("reasons", [])),
            ),
        )


def compare_reference(request: ReferenceComparisonRequest) -> ReferenceComparisonRun:
    setup = request.run.request.setup
    run_columns = load_numeric_csv(
        request.run.result_path,
        engine=request.run.request.backend,
        root_system_name=setup.root_system_name,
    )["columns"]
    reference_columns = load_reference_columns(request.reference_path, setup.model_name)

    summary, metrics = compare_column_sets(
        reference_columns,
        run_columns,
        run_a_label=request.reference.label,
        run_b_label=request.run.request.backend,
        engine_a=None,
        engine_b=request.run.request.backend,
        window=setup.window,
        selected_signals=setup.compare_signals,
        root_system_name=setup.root_system_name,
    )
    invariant_rows = signal_invariant_metrics(
        request.run.to_result_set(),
        model_name=setup.model_name,
        window=setup.window,
        root_system_name=setup.root_system_name,
    )
    gate = (
        evaluate_gate(metrics, gate=setup.gate, invariant_rows=invariant_rows)
        if request.gate_enabled
        else GateOutcome(status="not_evaluated")
    )

    request.run_dir.mkdir(parents=True, exist_ok=True)
    write_metrics_csv(request.metrics_path, metrics)
    run = ReferenceComparisonRun(
        request=request,
        summary=summary,
        metrics_path=request.metrics_path,
        gate=gate,
    )
    run.write_manifest()
    return run


def compare_references(
    run: SimulationRun,
    references: tuple[RegistryReferenceCsv, ...],
    *,
    repo_root: Path,
) -> tuple[ReferenceComparisonRun, ...]:
    return tuple(
        compare_reference(
            ReferenceComparisonRequest(
                run=run,
                reference=reference,
                reference_path=(
                    reference.path if reference.path.is_absolute() else repo_root / reference.path
                ),
            )
        )
        for reference in references
    )
