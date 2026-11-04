"""Compare a simulation run against a trusted reference CSV.

Engine-to-engine comparison answers "do the backends agree?". Reference
comparison answers "does this run match the trusted baseline?", which is the
primary VV gate for fixtures that ship a reference trajectory.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pyssp_workflow import compare
from pyssp_vv.evidence import read_metric_csv

from .gate import SHIFT_TOLERANCE_SAMPLES, GateOutcome, evaluate_gate
from .io import read_json, relative_path, resolve_path, write_json
from .model_policy import signal_invariant_rows
from .registry import RegistryReferenceCsv
from .simulate import SimulationRun


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
    """One reference comparison: the upstream record plus the local gate."""

    request: ReferenceComparisonRequest
    record: compare.ComparisonRecord
    gate: GateOutcome = GateOutcome(status="not_evaluated")

    @property
    def manifest_path(self) -> Path:
        return self.request.manifest_path

    @property
    def metrics_path(self) -> Path:
        return self.record.metrics_csv

    @property
    def summary(self) -> dict[str, float | int | str]:
        return self.record.summary.to_dict()

    def to_dict(self) -> dict[str, object]:
        payload = self.record.to_dict(self.manifest_path.parent)
        payload["request"] = self.request.to_dict()
        payload["gate"] = self.gate.to_dict()
        return payload

    def write_manifest(self) -> Path:
        write_json(self.manifest_path, self.to_dict())
        return self.manifest_path

    @classmethod
    def from_manifest(cls, path: Path) -> "ReferenceComparisonRun":
        data = read_json(path)
        return cls(
            request=ReferenceComparisonRequest.from_manifest(path),
            record=compare.ComparisonRecord.from_dict(data, base_dir=path.parent),
            gate=GateOutcome.from_dict(data.get("gate")),
        )


def compare_reference(request: ReferenceComparisonRequest) -> ReferenceComparisonRun:
    setup = request.run.request.setup
    window = setup.window
    record = compare.compare_csvs(
        compare.ComparisonRequest(
            reference=compare.ResultRef(
                result_csv=request.reference_path,
                label=request.reference.label,
            ),
            candidate=compare.ResultRef(
                result_csv=request.run.result_path,
                label=request.run.request.backend,
            ),
            out_dir=request.run_dir,
            signals=setup.compare_signals,
            start_time=window.start_time,
            stop_time=window.stop_time,
            step_size=window.interval,
            root_system=setup.root_system_name,
            reference_prefix=f"default.{setup.model_name}.",
            result_prefix="fmu.",
            shift_samples=SHIFT_TOLERANCE_SAMPLES,
            edge_samples=SHIFT_TOLERANCE_SAMPLES,
            max_gap_samples=None,
        )
    )
    invariant_rows = signal_invariant_rows(
        compare.ResultRef(
            result_csv=request.run.result_path,
            label=request.run.request.backend,
        ),
        model_name=setup.model_name,
        window=window,
        root_system_name=setup.root_system_name,
    )
    gate = (
        evaluate_gate(
            read_metric_csv(record.metrics_csv),
            gate=setup.gate,
            invariant_rows=invariant_rows,
        )
        if request.gate_enabled
        else GateOutcome(status="not_evaluated")
    )
    run = ReferenceComparisonRun(request=request, record=record, gate=gate)
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
