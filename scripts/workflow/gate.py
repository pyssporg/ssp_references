"""Pass/fail policy for simulation comparisons.

The metrics are produced by :mod:`utils.comparison`; this module only turns
them into a verdict. The gate uses the lag-tolerant max error so ordinary
one-step co-simulation skew does not fail an otherwise matching signal.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


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

    def limit(self, row: Mapping[str, object]) -> float:
        reference_peak = max(
            abs(float(row.get("run_a_min", 0.0))),
            abs(float(row.get("run_a_max", 0.0))),
        )
        return self.atol + self.rtol * reference_peak


@dataclass(frozen=True)
class GateOutcome:
    status: str
    reasons: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "reasons": list(self.reasons),
        }


def evaluate_gate(
    metrics: Iterable[Mapping[str, object]],
    *,
    gate: GateConfig,
    invariant_rows: Iterable[Mapping[str, object]] = (),
) -> GateOutcome:
    reasons: list[str] = []

    for row in metrics:
        signal = str(row["signal"])
        value = float(row["max_shift_abs_error"])
        limit = gate.limit(row)
        if value != value:  # NaN
            reasons.append(f"{signal}: non-finite comparison error")
        elif value > limit:
            reasons.append(
                f"{signal}: max_shift_abs_error={value:.6g} exceeds {limit:.6g}"
            )

    for row in invariant_rows:
        value = float(row["max_abs_error"])
        if value > gate.max_invariant_abs_error:
            reasons.append(
                f"{row['invariant']} ({row['run_label']}): "
                f"invariant error={value:.6g} exceeds "
                f"{gate.max_invariant_abs_error:.6g}"
            )

    return GateOutcome(status="fail" if reasons else "pass", reasons=tuple(reasons))
