#!/usr/bin/env python3
"""Build and simulate a two-FMU SSP with the minimal pyssp packages.

The only imports are the public surfaces of ``pyssp_sysml2`` (architecture to
SSP) and ``pyssp_simulate`` (SSP to trajectories). No repository-local
workflow or registry code is involved.
"""

from __future__ import annotations

from pathlib import Path

from pyssp_simulate import SimulationSpec, simulate
from pyssp_sysml2 import generate_ssp

EXAMPLE_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXAMPLE_DIR.parents[1]
BUILD_DIR = EXAMPLE_DIR / "build"


def main() -> int:
    ssp_path = generate_ssp(
        architecture_path=EXAMPLE_DIR / "architecture",
        output_path=BUILD_DIR / "simple_chain.ssp",
        composition="SimpleChain",
        fmu_root=REPO_ROOT,
    )
    print(f"Built {ssp_path}")

    result = simulate(
        SimulationSpec(
            ssp=ssp_path,
            start_time=0.0,
            stop_time=1.0,
            step_size=0.001,
            tolerance=1e-6,
            result_file=BUILD_DIR / "ssp4sim.csv",
        ),
        backend="ssp4sim",
    )

    print(f"Signals: {', '.join(result.signals)}")
    print(f"Samples: {len(result)}")
    for signal in result.signals:
        values = result[signal]
        print(f"{signal}: first={values[0]:.6g} last={values[-1]:.6g}")
    print(f"Result CSV: {BUILD_DIR / 'ssp4sim.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
