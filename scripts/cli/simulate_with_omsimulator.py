#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPTS_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPTS_ROOT))

from workflow.simulator import simulate_with_omsimulator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run an SSP with OMSimulator and export MAT/CSV results."
    )
    parser.add_argument("ssp", type=Path, help="Path to the SSP archive.")
    parser.add_argument("--result-mat", type=Path, required=True, help="MAT result output path.")
    parser.add_argument("--result-csv", type=Path, required=True, help="CSV result output path.")
    parser.add_argument("--start-time", type=float, required=True, help="Simulation start time.")
    parser.add_argument("--stop-time", type=float, required=True, help="Simulation stop time.")
    parser.add_argument("--interval", type=float, required=True, help="Result logging interval.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result_csv = simulate_with_omsimulator(
        args.ssp,
        result_mat=args.result_mat,
        result_csv=args.result_csv,
        start_time=args.start_time,
        stop_time=args.stop_time,
        interval=args.interval,
    )
    print(result_csv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
