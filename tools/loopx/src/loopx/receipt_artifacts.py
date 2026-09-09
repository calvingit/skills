"""Atomic task-local capability receipt artifacts."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any
from uuid import uuid4

from .graph.execution_graph.contracts import TICKET_ID_RE

CAPABILITIES = {"implement", "verify", "review", "aggregate"}


def _path(root: Path, ticket_id: str, attempt: int, capability: str) -> Path:
    if not TICKET_ID_RE.fullmatch(ticket_id) or not isinstance(attempt, int) or isinstance(attempt, bool) or attempt < 1 or capability not in CAPABILITIES:
        raise ValueError("invalid receipt identity")
    path = root / ".loop" / "receipts" / ticket_id / f"attempt-{attempt}" / f"{capability}.json"
    if not path.resolve().is_relative_to(root.resolve()) or any(parent.is_symlink() for parent in (path, *path.parents) if parent != root and parent.is_relative_to(root)):
        raise ValueError("receipt artifact must remain inside the task directory without symlinks")
    return path


def save(
    root: Path,
    *,
    ticket_id: str,
    attempt: int,
    capability: str,
    payload: dict[str, Any],
    agent_instance_id: str | None = None,
) -> Path:
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    instance_id = agent_instance_id or uuid4().hex
    path = _path(root, ticket_id, attempt, capability)
    path.parent.mkdir(parents=True, exist_ok=True)
    artifact = {
        "artifact_version": 1,
        "ticket_id": ticket_id,
        "current_attempt": attempt,
        "capability": capability,
        "agent_instance_id": instance_id,
        "payload": payload,
    }
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
            temporary_name = handle.name
            json.dump(artifact, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except OSError:
        if temporary_name:
            Path(temporary_name).unlink(missing_ok=True)
        raise
    return path


def load(root: Path, *, ticket_id: str, attempt: int, capability: str) -> dict[str, Any]:
    path = _path(root, ticket_id, attempt, capability)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"unable to read receipt artifact: {exc}") from exc
    if not isinstance(value, dict) or value.get("artifact_version") != 1:
        raise ValueError("unsupported receipt artifact")
    if value.get("ticket_id") != ticket_id or value.get("current_attempt") != attempt or value.get("capability") != capability:
        raise ValueError("receipt artifact identity mismatch")
    if not isinstance(value.get("agent_instance_id"), str) or not value["agent_instance_id"]:
        raise ValueError("receipt artifact is missing agent_instance_id")
    if not isinstance(value.get("payload"), dict):
        raise ValueError("receipt artifact payload must be an object")
    return value
