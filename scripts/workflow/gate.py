"""V&V judgment adapter over :mod:`pyssp_vv.judge`.

Measurement comes from ``pyssp_vv.measure``. This module keeps the repository
policy inputs (tolerances, model invariants) and maps the resulting verdict back
to the manifest shape. ``invalid`` is preserved as its own verdict.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from pyssp_vv.evidence import MetricRow
from pyssp_vv.judge import judge
from pyssp_vv.policy import (
    ComparisonPolicy,
    Criterion,
    MetricName,
    Policy,
    Sufficiency,
)

#: Samples excluded at each series edge (initialization and shutdown
#: transients) and the largest lag searched by the shift-tolerant error.
SHIFT_TOLERANCE_SAMPLES = 2


@dataclass(frozen=True)
class GateConfig:
    """Tolerance policy for one comparison."""

    atol: float = 1e-3
    rtol: float = 1e-2
    max_invariant_abs_error: float = 1e-8

    @classmethod
    def from_dict(cls, data: Mapping[str, object] | None) -> "GateConfig":
        if not data:
            return cls()
        return cls(
            atol=float(data.get("atol", 1e-3)),
            rtol=float(data.get("rtol", 1e-2)),
            max_invariant_abs_error=float(
                data.get("max_invariant_abs_error", 1e-8)
            ),
        )

    def to_dict(self) -> dict[str, float]:
        return {
            "atol": self.atol,
            "rtol": self.rtol,
            "max_invariant_abs_error": self.max_invariant_abs_error,
        }

    def comparison_policy(self) -> Policy:
        """Policy for engine/reference trajectory comparisons."""
        return Policy(
            comparison=ComparisonPolicy(
                shift_samples=SHIFT_TOLERANCE_SAMPLES,
                max_gap_samples=None,
            ),
            criterion=Criterion(
                atol=self.atol,
                rtol=self.rtol,
                metric=MetricName.MAX_ABS,
            ),
            sufficiency=Sufficiency(
                min_coverage=0.0,
                degenerate_range=0.0,
                reject_shift_at_boundary=False,
            ),
        )

    def invariant_policy(self) -> Policy:
        """Policy for model-specific algebraic invariants."""
        return Policy(
            criterion=Criterion(
                atol=self.max_invariant_abs_error,
                rtol=0.0,
                metric=MetricName.MAX_ABS,
            ),
            sufficiency=Sufficiency(
                min_coverage=0.0,
                degenerate_range=0.0,
                reject_shift_at_boundary=False,
            ),
        )


@dataclass(frozen=True)
class GateOutcome:
    status: str
    reasons: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "reasons": list(self.reasons),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object] | None) -> "GateOutcome":
        payload = data or {}
        return cls(
            status=str(payload.get("status", "not_evaluated")),
            reasons=tuple(str(reason) for reason in payload.get("reasons", [])),
        )


@dataclass(frozen=True)
class _Metric:
    signal: str
    coverage: float
    max_abs_error: float
    mean_abs_error: float
    rmse: float
    normalised_max_abs_error: float
    reference_min: float
    reference_max: float
    shift_samples: int
    undefined: tuple[str, ...] = ()


def _comparison_metric(row: MetricRow) -> _Metric:
    return _Metric(
        signal=row.signal,
        coverage=row.coverage,
        # The gate uses the lag-tolerant error as its acceptance value.
        max_abs_error=row.max_shift_abs_error,
        mean_abs_error=row.mean_abs_error,
        rmse=row.rmse,
        normalised_max_abs_error=row.normalised_max_abs_error,
        reference_min=row.run_a_min,
        reference_max=row.run_a_max,
        shift_samples=row.shift_samples,
        undefined=row.undefined,
    )


def _invariant_metric(row: Mapping[str, object]) -> _Metric:
    return _Metric(
        signal=str(row["invariant"]),
        coverage=1.0,
        max_abs_error=float(row["max_abs_error"]),
        mean_abs_error=float(row.get("mean_abs_error", float("nan"))),
        rmse=float(row.get("rmse", float("nan"))),
        normalised_max_abs_error=float("nan"),
        reference_min=0.0,
        reference_max=1.0,
        shift_samples=0,
    )


def _verdict(statuses: Iterable[str]) -> str:
    values = set(statuses)
    if "invalid" in values:
        return "invalid"
    if "fail" in values:
        return "fail"
    if values and values <= {"pass"}:
        return "pass"
    return "not_evaluated"


def _reason_text(item, reason) -> str:
    detail = f" ({reason.detail})" if reason.detail else ""
    return f"{item.signal}: {reason.code}{detail}"


def evaluate_gate(
    metrics: Iterable[MetricRow],
    *,
    gate: GateConfig,
    invariant_rows: Iterable[Mapping[str, object]] = (),
) -> GateOutcome:
    comparison_metrics = [_comparison_metric(row) for row in metrics]
    invariant_metrics = [_invariant_metric(row) for row in invariant_rows]

    judgments = []
    if comparison_metrics:
        judgments.append(judge(comparison_metrics, gate.comparison_policy()))
    if invariant_metrics:
        judgments.append(judge(invariant_metrics, gate.invariant_policy()))

    if not judgments:
        return GateOutcome(
            status="invalid",
            reasons=("no-signals: nothing was measured",),
        )

    reasons = tuple(
        _reason_text(item, reason)
        for judgment in judgments
        for item in judgment.signals
        for reason in item.reasons
    )
    status = _verdict(judgment.verdict.value for judgment in judgments)
    return GateOutcome(status=status, reasons=reasons)


def combine_gate_outcomes(outcomes: Iterable[GateOutcome]) -> GateOutcome:
    """Aggregate verdicts pessimistically: invalid dominates fail."""
    items = tuple(outcomes)
    status = _verdict(item.status for item in items)
    reasons = tuple(reason for item in items for reason in item.reasons)
    return GateOutcome(status=status, reasons=reasons)
