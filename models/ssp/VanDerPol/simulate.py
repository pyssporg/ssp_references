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
    config = SimulationConfig()
    payload = run_standard_model_simulation(model, config=config)
    print(f"{model.name}: ran 2 simulations and wrote {len(payload['comparisons'])} comparisons")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
