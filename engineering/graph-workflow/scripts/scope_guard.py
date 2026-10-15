"""Validate ticket write-scope metadata; execution remains with the caller."""
from pathlib import PurePosixPath

def validate_scope(scope: list[str]) -> None:
    if not isinstance(scope, list) or not scope or any(
        not isinstance(item, str) or not item.strip()
        or PurePosixPath(item).is_absolute() or ".." in PurePosixPath(item).parts
        for item in scope
    ):
        raise ValueError("Write scope must contain non-empty workspace-relative paths.")


def _covers(pattern: str, other: str) -> bool:
    """Whether one expected-write entry can touch the other's area."""
    base = pattern.rstrip("*").rstrip("/")
    target = other.rstrip("*").rstrip("/")
    if not base:
        return True
    return target == base or target.startswith(base + "/")


def overlap(left: list[str], right: list[str]) -> tuple[str, str] | None:
    """First pair of expected write areas that may touch the same files."""
    for pattern in left:
        for other in right:
            if _covers(pattern, other) or _covers(other, pattern):
                return (pattern, other)
    return None
