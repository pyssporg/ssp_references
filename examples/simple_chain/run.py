#!/usr/bin/env python3
"""Build and simulate a two-FMU SSP with the minimal pyssp packages.

The only imports are the public surfaces of ``pyssp_sysml2`` (architecture to
SSP), ``pycps_sysml2`` (the dialect core definitions the architecture imports),
and ``pyssp_simulate`` (SSP to trajectories). No repository-local workflow or
registry code is involved.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from pycps_sysml2 import core_definitions
from pyssp_simulate import SimulationSpec, simulate
from pyssp_sysml2 import generate_ssp

EXAMPLE_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXAMPLE_DIR.parents[1]
DEFAULT_OUT = Path("build") / "examples" / "simple_chain"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help=f"output directory (default: {DEFAULT_OUT})",
    )
    args = parser.parse_args(argv)

    ssp_path = generate_ssp(
        architecture_path=EXAMPLE_DIR / "architecture",
        output_path=args.out / "simple_chain.ssp",
        composition="SimpleChain",
        fmu_root=REPO_ROOT,
        includes=(core_definitions(),),
    )
    csv_path = args.out / "ssp4sim.csv"

    simulate(
        SimulationSpec(
            ssp=ssp_path,
            start_time=0.0,
            stop_time=1.0,
            step_size=0.001,
            tolerance=1e-6,
            result_file=csv_path,
        ),
        backend="ssp4sim",
    )

    print(f"SSP: {ssp_path}")
    print(f"CSV: {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
