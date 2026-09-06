from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any
from uuid import uuid4


def save(root: Path, *, result: dict[str, Any], stdout: str, stderr: str, returncode: int | None) -> Path:
    directory = root / ".loop" / "worker-runs"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{uuid4().hex}.json"
    temporary: str | None = None
    artifact = {"artifact_version": 1, "result": result, "raw": {"stdout": stdout, "stderr": stderr, "returncode": returncode}}
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=directory, delete=False) as handle:
            temporary = handle.name
            json.dump(artifact, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except OSError:
        if temporary:
            Path(temporary).unlink(missing_ok=True)
        raise
    return path
