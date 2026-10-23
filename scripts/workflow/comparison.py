"""Compose engine-to-engine comparisons.

Measurement and the reviewed metric table come from ``pyssp_vv`` and
``pyssp_workflow.execute``. This module owns the artifact layout, the
repository gate, and the comparison manifests.
"""

from __future__ import annotations

from itertools import combinations
from dataclasses import dataclass
from pathlib import Path

from pyssp_workflow import execute
from pyssp_vv.evidence import read_metric_csv

from utils.filesystem import reset_dir

from .gate import (
    SHIFT_TOLERANCE_SAMPLES,
    GateOutcome,
    combine_gate_outcomes,
    evaluate_gate,
)
from .io import read_json, relative_path, resolve_path, write_json
from .model_policy import signal_invariant_rows
from .simulate import SimulationRun


@dataclass(frozen=True)
class ComparisonRequest:
    run_a: SimulationRun
    run_b: SimulationRun

    @property
    def runs(self) -> tuple[SimulationRun, SimulationRun]:
        return (self.run_a, self.run_b)

    def validate(self) -> None:
        run_a_setup = self.run_a.request.setup
        run_b_setup = self.run_b.request.setup
        if run_a_setup.layout.ssp_root != run_b_setup.layout.ssp_root:
            raise ValueError("Comparison requires both runs to use the same SSP root")
        if run_a_setup.model_name != run_b_setup.model_name:
            raise ValueError("Comparison requires both runs to use the same model")
        if run_a_setup.case_name != run_b_setup.case_name:
            raise ValueError("Comparison requires both runs to use the same case")
        if run_a_setup.window != run_b_setup.window:
            raise ValueError("Comparison requires both runs to use the same execution window")
        if run_a_setup.compare_signals != run_b_setup.compare_signals:
            raise ValueError("Comparison requires both runs to use the same selected signals")
        if self.run_a.request.backend == self.run_b.request.backend:
            raise ValueError("Comparison requires distinct backends")

    @property
    def case_name(self) -> str:
        return self.run_a.request.setup.case_name

    @property
    def run_dir(self) -> Path:
        return self.run_a.request.setup.layout.comparison_run_dir(
            self.run_a.request.backend,
            self.run_b.request.backend,
        )

    @property
    def manifest_path(self) -> Path:
        return self.run_a.request.setup.layout.comparison_manifest_path(
            self.run_a.request.backend,
            self.run_b.request.backend,
        )

    @property
    def metrics_path(self) -> Path:
        return self.run_a.request.setup.layout.comparison_metrics_path(
            self.run_a.request.backend,
            self.run_b.request.backend,
        )

    def to_dict(self) -> dict[str, object]:
        run_dir = self.run_dir
        return {
            "runs": [
                {
                    "backend": run.request.backend,
                    "manifest": relative_path(run_dir, run.manifest_path),
                }
                for run in self.runs
            ],
            "case": self.case_name,
        }

    @classmethod
    def from_manifest(cls, path: Path) -> "ComparisonRequest":
        data = read_json(path)
        payload = data.get("request", data)
        run_entries = payload["runs"]
        if not isinstance(run_entries, list) or len(run_entries) != 2:
            raise ValueError("Comparison request must contain exactly two runs")
        runs = tuple(
            SimulationRun.from_manifest(resolve_path(path.parent, entry["manifest"]))
            for entry in run_entries
        )
        return cls(run_a=runs[0], run_b=runs[1])


@dataclass(frozen=True)
class ComparisonRun:
    """One measured pair: the upstream record plus the local gate payload."""

    request: ComparisonRequest
    record: execute.ComparisonRecord
    gate: GateOutcome = GateOutcome(status="not_evaluated")
    max_signal_invariant_abs_error: float = 0.0
    signal_invariant_count: int = 0

    @property
    def manifest_path(self) -> Path:
        return self.request.manifest_path

    @property
    def run_dir(self) -> Path:
        return self.request.run_dir

    @property
    def metrics_path(self) -> Path:
        return self.record.metrics_csv

    @property
    def summary(self) -> dict[str, float | int | str]:
        return self.record.summary.to_dict()

    def summary_with_locals(self) -> dict[str, float | int | str]:
        """Upstream summary plus the repo's invariant evidence."""
        summary = self.summary
        summary["max_signal_invariant_abs_error"] = self.max_signal_invariant_abs_error
        summary["signal_invariant_count"] = self.signal_invariant_count
        return summary

    def to_dict(self) -> dict[str, object]:
        payload = self.record.to_dict(self.manifest_path.parent)
        payload["request"] = self.request.to_dict()
        payload["gate"] = self.gate.to_dict()
        payload["summary"] = self.summary_with_locals()
        return payload

    def write_manifest(self) -> Path:
        write_json(self.manifest_path, self.to_dict())
        return self.manifest_path

    @classmethod
    def from_manifest(cls, path: Path) -> "ComparisonRun":
        data = read_json(path)
        summary = data.get("summary") or {}
        return cls(
            request=ComparisonRequest.from_manifest(path),
            record=execute.ComparisonRecord.from_dict(data, base_dir=path.parent),
            gate=GateOutcome.from_dict(data.get("gate")),
            max_signal_invariant_abs_error=float(
                summary.get("max_signal_invariant_abs_error", 0.0)
            ),
            signal_invariant_count=int(summary.get("signal_invariant_count", 0)),
        )


@dataclass(frozen=True)
class ComparisonBatchRequest:
    runs: tuple[SimulationRun, ...]

    def validate(self) -> None:
        if len(self.runs) < 2:
            raise ValueError("Comparison requires at least two simulation runs")

        first_setup = self.runs[0].request.setup
        seen_backends: set[str] = set()
        for run in self.runs:
            setup = run.request.setup
            if setup.layout.ssp_root != first_setup.layout.ssp_root:
                raise ValueError("Comparison requires all runs to use the same SSP root")
            if setup.model_name != first_setup.model_name:
                raise ValueError("Comparison requires all runs to use the same model")
            if setup.case_name != first_setup.case_name:
                raise ValueError("Comparison requires all runs to use the same case")
            if setup.window != first_setup.window:
                raise ValueError("Comparison requires all runs to use the same execution window")
            if setup.compare_signals != first_setup.compare_signals:
                raise ValueError("Comparison requires all runs to use the same selected signals")
            if run.request.backend in seen_backends:
                raise ValueError("Comparison requires unique backends")
            seen_backends.add(run.request.backend)

    @property
    def model_name(self) -> str:
        return self.runs[0].request.setup.model_name

    @property
    def case_name(self) -> str:
        return self.runs[0].request.setup.case_name

    @property
    def run_dir(self) -> Path:
        return self.runs[0].request.setup.layout.comparison_case_root

    @property
    def manifest_path(self) -> Path:
        return self.runs[0].request.setup.layout.comparison_batch_manifest_path

    def to_dict(self) -> dict[str, object]:
        run_dir = self.run_dir
        return {
            "model": self.model_name,
            "case": self.case_name,
            "runs": [
                {
                    "backend": run.request.backend,
                    "manifest": relative_path(run_dir, run.manifest_path),
                }
                for run in self.runs
            ],
        }

    @classmethod
    def from_manifest(cls, path: Path) -> "ComparisonBatchRequest":
        data = read_json(path)
        payload = data.get("request", data)
        run_entries = payload["runs"]
        if not isinstance(run_entries, list) or len(run_entries) < 2:
            raise ValueError("Comparison requires at least two simulation runs")
        runs = tuple(
            SimulationRun.from_manifest(resolve_path(path.parent, entry["manifest"]))
            for entry in run_entries
        )
        return cls(runs=runs)


@dataclass(frozen=True)
class ComparisonBatchRun:
    request: ComparisonBatchRequest
    comparisons: tuple[ComparisonRun, ...]
    summary: dict[str, float | int | str]
    status: str = "completed"
    error: str | None = None
    gate: GateOutcome = GateOutcome(status="not_evaluated")

    @property
    def manifest_path(self) -> Path:
        return self.request.manifest_path

    @property
    def run_dir(self) -> Path:
        return self.request.run_dir

    def to_dict(self) -> dict[str, object]:
        run_dir = self.run_dir
        return {
            "request": self.request.to_dict(),
            "summary": self.summary,
            "comparisons": [
                {
                    **comparison.record.to_dict(run_dir),
                    "summary": comparison.summary_with_locals(),
                    "runs": [
                        {
                            "backend": run.request.backend,
                            "manifest": relative_path(run_dir, run.manifest_path),
                        }
                        for run in comparison.request.runs
                    ],
                    "manifest": relative_path(run_dir, comparison.manifest_path),
                    "gate": comparison.gate.to_dict(),
                }
                for comparison in self.comparisons
            ],
            "status": self.status,
            "error": self.error,
            "gate": self.gate.to_dict(),
        }

    def write_manifest(self) -> Path:
        write_json(self.manifest_path, self.to_dict())
        return self.manifest_path

    @classmethod
    def from_manifest(cls, path: Path) -> "ComparisonBatchRun":
        data = read_json(path)
        request = ComparisonBatchRequest.from_manifest(path)
        comparisons = tuple(
            ComparisonRun.from_manifest(resolve_path(path.parent, comparison["manifest"]))
            for comparison in data.get("comparisons", [])
        )
        return cls(
            request=request,
            comparisons=comparisons,
            summary=data["summary"],
            status=data.get("status", "completed"),
            error=data.get("error"),
            gate=GateOutcome.from_dict(data.get("gate")),
        )


def _summarize_batch(
    runs: tuple[SimulationRun, ...],
    comparisons: tuple[ComparisonRun, ...],
) -> dict[str, float | int | str]:
    return {
        "backend_count": len(runs),
        "comparison_count": len(comparisons),
        "max_abs_error": max(
            (comparison.summary["max_abs_error"] for comparison in comparisons),
            default=0.0,
        ),
        "max_rel_error": max(
            (comparison.summary["max_rel_error"] for comparison in comparisons),
            default=0.0,
        ),
        "max_shift_abs_error": max(
            (
                comparison.summary["max_shift_abs_error"]
                for comparison in comparisons
            ),
            default=0.0,
        ),
        "max_signal_invariant_abs_error": max(
            (
                comparison.max_signal_invariant_abs_error
                for comparison in comparisons
            ),
            default=0.0,
        ),
        "min_compared_signal_count": min(
            (
                comparison.summary["compared_signal_count"]
                for comparison in comparisons
            ),
            default=0,
        ),
        "gate_result": combine_gate_outcomes(
            comparison.gate for comparison in comparisons
        ).status,
    }


def compare_runs(request: ComparisonRequest) -> ComparisonRun:
    request.validate()
    reset_dir(request.run_dir)
    setup = request.run_a.request.setup
    window = setup.window
    record = execute.compare_result_csvs(
        execute.ComparisonRequest(
            reference=execute.ResultRef(
                result_csv=request.run_a.result_path,
                label=request.run_a.request.backend,
            ),
            candidate=execute.ResultRef(
                result_csv=request.run_b.result_path,
                label=request.run_b.request.backend,
            ),
            out_dir=request.run_dir,
            signals=setup.compare_signals,
            start_time=window.start_time,
            stop_time=window.stop_time,
            step_size=window.interval,
            root_system=setup.root_system_name,
            reference_prefix="fmu.",
            result_prefix="fmu.",
            shift_samples=SHIFT_TOLERANCE_SAMPLES,
            edge_samples=SHIFT_TOLERANCE_SAMPLES,
            max_gap_samples=None,
        )
    )
    invariant_rows = [
        *signal_invariant_rows(
            execute.ResultRef(
                result_csv=request.run_a.result_path,
                label=request.run_a.request.backend,
            ),
            model_name=setup.model_name,
            window=window,
            root_system_name=setup.root_system_name,
        ),
        *signal_invariant_rows(
            execute.ResultRef(
                result_csv=request.run_b.result_path,
                label=request.run_b.request.backend,
            ),
            model_name=setup.model_name,
            window=window,
            root_system_name=setup.root_system_name,
        ),
    ]
    run = ComparisonRun(
        request=request,
        record=record,
        gate=evaluate_gate(
            read_metric_csv(record.metrics_csv),
            gate=setup.gate,
            invariant_rows=invariant_rows,
        ),
        max_signal_invariant_abs_error=max(
            (float(row["max_abs_error"]) for row in invariant_rows),
            default=0.0,
        ),
        signal_invariant_count=len(invariant_rows),
    )
    run.write_manifest()
    return run


def compare_run_batch(request: ComparisonBatchRequest) -> ComparisonBatchRun:
    request.validate()
    comparisons = tuple(
        compare_runs(ComparisonRequest(run_a=run_a, run_b=run_b))
        for run_a, run_b in combinations(request.runs, 2)
    )
    batch = ComparisonBatchRun(
        request=request,
        comparisons=comparisons,
        summary=_summarize_batch(request.runs, comparisons),
        gate=combine_gate_outcomes(
            comparison.gate for comparison in comparisons
        ),
    )
    batch.write_manifest()
    return batch
