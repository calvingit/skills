"""Validate ticket write-scope metadata; execution remains with the caller."""
from pathlib import PurePosixPath

def validate_scope(scope: list[str]) -> None:
    if not isinstance(scope, list) or not scope or any(
        not isinstance(item, str) or not item.strip()
        or PurePosixPath(item).is_absolute() or ".." in PurePosixPath(item).parts
        for item in scope
    ):
        raise ValueError("Write scope must contain non-empty workspace-relative paths.")
