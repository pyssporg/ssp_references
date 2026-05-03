#!/usr/bin/env python3

from __future__ import annotations

import os
import sys
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(os.environ.get("SSP_REFERENCES_REPO_ROOT", Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from workflow.model import ModelMetaData
from workflow.simulation import SimulationConfig, run_standard_model_simulation


def main() -> int:
    model = ModelMetaData(MODEL_DIR)
    config = SimulationConfig(start_time=0.0, stop_time=1.0, interval=0.01)
    payload = run_standard_model_simulation(model, config=config, include_references=False)
    print(f"{model.name}: ran 2 simulations and wrote {len(payload['comparisons'])} comparisons")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
