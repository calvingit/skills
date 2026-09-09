"""Capability write-scope policy and post-run diff checks."""

from __future__ import annotations

from pathlib import PurePosixPath

GRAPH_PATHS = {"SPEC.md", "ACCEPTANCE.md", "HLD.md"}


def contains(scope: list[str], path: str) -> bool:
    return any(item == "." or path == item.rstrip("/") or path.startswith(item.rstrip("/") + "/") for item in scope)


def allowed_scope(capability: str, scope: list[str]) -> list[str]:
    if (
        capability == "implement"
        and isinstance(scope, list)
        and scope
        and all(isinstance(item, str) and item.strip() and not PurePosixPath(item).is_absolute() and ".." not in PurePosixPath(item).parts for item in scope)
    ):
        return list(scope)
    if capability in {"verify", "review"} and isinstance(scope, list) and not scope:
        return []
    raise ValueError("capability has an invalid write scope")


def violations(
    capability: str,
    scope: list[str],
    changed_paths: list[str],
    *,
    protected_paths: set[str] | None = None,
    temporary_paths: list[str] | None = None,
) -> list[str]:
    allowed = allowed_scope(capability, scope)
    protected = protected_paths or set()
    temporary = temporary_paths or []
    problems: list[str] = []
    for path in changed_paths:
        normalized = PurePosixPath(path).as_posix()
        if normalized in protected:
            problems.append(normalized)
            continue
        is_temporary = any(normalized == item.rstrip("/") or normalized.startswith(item.rstrip("/") + "/") for item in temporary)
        parts = PurePosixPath(normalized).parts
        if PurePosixPath(normalized).name in GRAPH_PATHS or "tickets" in parts[:-1] or (".loop" in parts and not is_temporary):
            problems.append(normalized)
            continue
        if capability != "implement" and not is_temporary:
            problems.append(normalized)
            continue
        if capability == "implement" and not contains(allowed, normalized):
            problems.append(normalized)
    return sorted(set(problems))
