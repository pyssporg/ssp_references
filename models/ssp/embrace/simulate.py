#!/usr/bin/env python3

from __future__ import annotations

import os
import sys
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(os.environ.get("SSP_REFERENCES_REPO_ROOT", Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from workflow.comparison import compare_available_results
from workflow.model import ModelMetaData
from workflow.simulation import SimulationVariant, run_simulation_variants


def main() -> int:
    model = ModelMetaData(MODEL_DIR)
    variants = [
        SimulationVariant(name="omsimulator_current", engine="omsimulator", version="current"),
        SimulationVariant(name="ssp4sim_current", engine="ssp4sim", version="current"),
    ]
    artifacts = run_simulation_variants(model, variants)
    payload = compare_available_results(model, window=artifacts[0].window, include_references=False)
    print(f"{model.name}: ran {len(variants)} variants and wrote {len(payload['comparisons'])} comparisons")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
