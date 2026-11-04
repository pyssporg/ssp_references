"""Guards for artifact-based tool boundaries (ADR-006)."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_sysml_roundtrip_checker_does_not_import_model_libraries() -> None:
    source = (REPO_ROOT / "scripts" / "check_sysml_roundtrip.py").read_text(
        encoding="utf-8"
    )

    assert "import pyssp_sysml2" not in source
    assert "from pyssp_sysml2" not in source
    assert "import pyssp_standard" not in source
    assert "from pyssp_standard" not in source
