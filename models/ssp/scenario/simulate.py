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
from workflow.simulation import SimulationConfig, simulate_oms, simulate_ssp4sim


def main() -> int:
    model = ModelMetaData(MODEL_DIR)
    config = SimulationConfig()
    artifacts = [
        simulate_oms(model, name="omsimulator_current", config=config),
        simulate_ssp4sim(model, name="ssp4sim_current", config=config),
    ]
    payload = compare_available_results(model, window=artifacts[0].window, include_references=False)
    print(f"{model.name}: ran {len(artifacts)} simulations and wrote {len(payload['comparisons'])} comparisons")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
