"""Read-only Git and task fingerprints for delivery progress tracking."""
from __future__ import annotations
import hashlib
import subprocess
from pathlib import Path

def _workspace_status(workspace_root: Path) -> dict[str, str] | None:
    """Return a complete git status probe, including ignored files."""
    result = subprocess.run(
        [
            "git",
            "-C",
            str(workspace_root),
            "status",
            "--porcelain=v1",
            "-uall",
            "--ignored=matching",
            "-z",
        ],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    status: dict[str, str] = {}
    entries = result.stdout.decode("utf-8", errors="surrogateescape").split("\0")
    index = 0
    while index < len(entries):
        entry = entries[index]
        index += 1
        if not entry or len(entry) < 3 or entry[2] != " ":
            continue
        state, relative = entry[:2], entry[3:]
        if state[0] in {"R", "C"} or state[1] in {"R", "C"}:
            status[relative] = state
            if index < len(entries) and entries[index]:
                status[entries[index]] = state
                index += 1
        elif state == "!!" and relative.endswith("/"):
            ignored_root = workspace_root / relative.rstrip("/")
            expanded = False
            try:
                for path in ignored_root.rglob("*"):
                    if path.is_file() or path.is_symlink():
                        status[path.relative_to(workspace_root).as_posix()] = state
                        expanded = True
            except OSError:
                return None
            if not expanded:
                status[relative] = state
        else:
            status[relative] = state
    tracked = subprocess.run(
        ["git", "-C", str(workspace_root), "ls-files", "-z"],
        capture_output=True,
        check=False,
    )
    if tracked.returncode != 0:
        return None
    for relative_bytes in tracked.stdout.split(b"\0"):
        if relative_bytes:
            relative = relative_bytes.decode("utf-8", errors="surrogateescape")
            status.setdefault(relative, "  ")
    return status


def _workspace_snapshot(workspace_root: Path) -> dict[str, tuple[str, str | None]] | None:
    status = _workspace_status(workspace_root)
    if status is None:
        return None
    snapshot: dict[str, tuple[str, str | None]] = {}
    for relative, state in status.items():
        path = workspace_root / relative
        try:
            digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        except (OSError, UnicodeError):
            digest = None
        snapshot[relative] = (state, digest)
    return snapshot


def _workspace_revision(workspace_root: Path) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(workspace_root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def _graph_files(task_dir: Path) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for name in ("SPEC.md", "ACCEPTANCE.md", "HLD.md"):
        path = task_dir / name
        if path.is_file():
            files[name] = path.read_bytes()
    for path in sorted((task_dir / "tickets").glob("*.json")):
        files[path.relative_to(task_dir).as_posix()] = path.read_bytes()
    return files
