#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPTS_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPTS_ROOT))

from workflow.compare import compare_model_results
from workflow.config import MODELS_DIR
from workflow.model import ModelMetaData


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run OMSimulator and ssp4sim for one or more models and compare their results."
    )
    parser.add_argument("models", nargs="+", help="Model names under models/*/<model_name>.")
    parser.add_argument("--start-time", type=float, help="Override inferred start time.")
    parser.add_argument("--stop-time", type=float, help="Override inferred stop time.")
    parser.add_argument("--interval", type=float, help="Override inferred recording interval.")
    parser.add_argument(
        "--ssp4sim-app",
        help="Path to the ssp4sim sim_app binary. Defaults to SSP4SIM_SIM_APP or ../ssp4sim/build/public/ssp4sim_app/sim_app.",
    )
    return parser.parse_args()


def find_model_dir(model_name: str) -> Path:
    matches = sorted(MODELS_DIR.glob(f"*/{model_name}"))
    if not matches:
        raise FileNotFoundError(f"Model directory not found for {model_name}")
    if len(matches) > 1:
        raise RuntimeError(f"Ambiguous model name {model_name}: {matches}")
    return matches[0]


def main() -> int:
    args = parse_args()
    for model_name in args.models:
        model = ModelMetaData(find_model_dir(model_name))
        payload = compare_model_results(
            model,
            start_time=args.start_time,
            stop_time=args.stop_time,
            interval=args.interval,
            ssp4sim_app=args.ssp4sim_app,
        )
        summary = payload["summary"]
        print(
            f"{model.name}: compared {summary['common_signal_count']} common signals, "
            f"max_abs_error={summary['max_abs_error']:.6g}, "
            f"mean_abs_error={summary['mean_abs_error']:.6g}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
