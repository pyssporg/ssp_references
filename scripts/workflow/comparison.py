from __future__ import annotations

from itertools import combinations
from dataclasses import dataclass
from pathlib import Path

from utils.comparison import compare_result_sets, write_metrics_csv
from utils.filesystem import reset_dir

from .io import read_json, relative_path, resolve_path, write_json
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
    request: ComparisonRequest
    summary: dict[str, float | int | str]
    metrics_path: Path
    status: str = "completed"
    error: str | None = None

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
            "metrics": relative_path(run_dir, self.metrics_path),
            "status": self.status,
            "error": self.error,
        }

    def write_manifest(self) -> Path:
        write_json(self.manifest_path, self.to_dict())
        return self.manifest_path

    @classmethod
    def from_manifest(cls, path: Path) -> "ComparisonRun":
        data = read_json(path)
        request = ComparisonRequest.from_manifest(path)
        return cls(
            request=request,
            summary=data["summary"],
            metrics_path=resolve_path(path.parent, data["metrics"]),
            status=data.get("status", "completed"),
            error=data.get("error"),
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
                    "runs": [
                        {
                            "backend": run.request.backend,
                            "manifest": relative_path(run_dir, run.manifest_path),
                        }
                        for run in comparison.request.runs
                    ],
                    "manifest": relative_path(run_dir, comparison.manifest_path),
                    "metrics": relative_path(run_dir, comparison.metrics_path),
                    "summary": comparison.summary,
                }
                for comparison in self.comparisons
            ],
            "status": self.status,
            "error": self.error,
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
        )


def _summarize_batch(
    runs: tuple[SimulationRun, ...],
    comparisons: tuple[ComparisonRun, ...],
) -> dict[str, float | int | str]:
    max_abs_error = max(
        (float(comparison.summary.get("max_abs_error", 0.0)) for comparison in comparisons),
        default=0.0,
    )
    max_rel_error = max(
        (float(comparison.summary.get("max_rel_error", 0.0)) for comparison in comparisons),
        default=0.0,
    )
    min_compared_signal_count = min(
        (int(comparison.summary.get("compared_signal_count", 0)) for comparison in comparisons),
        default=0,
    )
    return {
        "backend_count": len(runs),
        "comparison_count": len(comparisons),
        "max_abs_error": max_abs_error,
        "max_rel_error": max_rel_error,
        "min_compared_signal_count": min_compared_signal_count,
    }


def compare_runs(request: ComparisonRequest) -> ComparisonRun:
    request.validate()
    reset_dir(request.run_dir)
    summary, metrics = compare_result_sets(
        request.run_a.to_result_set(),
        request.run_b.to_result_set(),
        window=request.run_a.request.setup.window,
        selected_signals=request.run_a.request.setup.compare_signals,
        root_system_name=request.run_a.request.setup.root_system_name,
    )
    write_metrics_csv(request.metrics_path, metrics)
    run = ComparisonRun(
        request=request,
        summary=summary,
        metrics_path=request.metrics_path,
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
    )
    batch.write_manifest()
    return batch
