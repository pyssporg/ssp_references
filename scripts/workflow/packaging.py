from __future__ import annotations

import tempfile
import zipfile
from contextlib import contextmanager
from pathlib import Path

FIXED_GENERATION_DATE_AND_TIME = "1970-01-01T00:00:00Z"


@contextmanager
def materialize_fmu_archive(source_path: Path, archive_name: str):
    if source_path.is_file():
        yield source_path
        return

    with tempfile.TemporaryDirectory() as temp_dir:
        archive_path = Path(temp_dir) / archive_name
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(source_path.rglob("*")):
                if path.is_dir():
                    continue
                archive.write(path, arcname=path.relative_to(source_path))
        yield archive_path
