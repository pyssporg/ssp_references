#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent
REPO_ROOT = MODEL_DIR.parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from workflow_common import setup_directory


if __name__ == "__main__":
    setup_directory(MODEL_DIR)
