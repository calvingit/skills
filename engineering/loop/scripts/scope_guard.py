"""Capability write-scope policy and post-run diff checks."""

from __future__ import annotations

from pathlib import PurePosixPath

GRAPH_PATHS = {"SPEC.md", "HLD.md"}


def allowed_scope(capability: str, scope: list[str]) -> list[str]:
    if (
        capability == "implement"
        and isinstance(scope, list)
        and scope
        and all(isinstance(item, str) and item.strip() for item in scope)
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
        if normalized in GRAPH_PATHS or normalized.startswith("tickets/") or (normalized.startswith(".loop/") and not is_temporary):
            problems.append(normalized)
            continue
        if capability != "implement" and not is_temporary:
            problems.append(normalized)
            continue
        if capability == "implement" and not any(normalized == item or normalized.startswith(item.rstrip("/") + "/") for item in allowed):
            problems.append(normalized)
    return sorted(set(problems))
