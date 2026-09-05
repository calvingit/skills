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


def violations(capability: str, scope: list[str], changed_paths: list[str]) -> list[str]:
    allowed = allowed_scope(capability, scope)
    problems: list[str] = []
    for path in changed_paths:
        normalized = PurePosixPath(path).as_posix()
        if normalized in GRAPH_PATHS or normalized.startswith("tickets/") or normalized.startswith(".loop/"):
            problems.append(normalized)
            continue
        if capability != "implement" or not any(normalized == item or normalized.startswith(item.rstrip("/") + "/") for item in allowed):
            problems.append(normalized)
    return sorted(set(problems))
