#!/usr/bin/env python3

from __future__ import annotations

import os
import sys
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(os.environ["SSP_REFERENCES_REPO_ROOT"])
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from workflow.setup import build_ssp_from_local_resources, setup_directory


if __name__ == "__main__":
    setup_directory(MODEL_DIR, ssp_builder=build_ssp_from_local_resources)
