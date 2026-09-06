"""Explicit version-to-version migration planning and execution."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .authority import authority_index
from .contracts import CURRENT_SCHEMA_VERSION, envelope, problem, validate_ticket
from .graph import public_ticket, validate_graph
from .store import (
    acquire_read_lock, acquire_write_lock, commit_graph_transaction,
    read_raw_tickets, release_lock, validated_snapshot,
)

MIGRATIONS: dict[int, Callable[[dict[str, Any]], dict[str, Any]]] = {}

def migration_plan(version: int) -> tuple[list[dict[str, int]], list[dict[str, str]]]:
    if version > CURRENT_SCHEMA_VERSION:
        return [], [problem("contract", "unknown_schema_version", f"Schema version {version} is newer than supported version {CURRENT_SCHEMA_VERSION}.")]
    plan: list[dict[str, int]] = []
    for current in range(version, CURRENT_SCHEMA_VERSION):
        if current not in MIGRATIONS:
            return [], [problem("contract", "unsupported_migration_path", f"No explicit migration is registered from version {current} to {current + 1}.")]
        plan.append({"from": current, "to": current + 1})
    return plan, []


def migrate_graph_unlocked(
    task_dir: Path, *, check_only: bool
) -> tuple[dict[str, object], int]:
    tickets, read_problems = read_raw_tickets(task_dir)
    if read_problems:
        return envelope("migrate", ok=False, problems=read_problems), 1
    versions = sorted({ticket["schema_version"] for ticket in tickets})
    if len(versions) != 1:
        problems = [problem("contract", "mixed_schema_versions", "All tickets must have one schema version before migration.")]
        return envelope("migrate", ok=False, problems=problems), 1
    plan, plan_problems = migration_plan(versions[0])
    if plan_problems:
        return envelope("migrate", ok=False, problems=plan_problems), 1
    result = {
        "current_version": CURRENT_SCHEMA_VERSION,
        "source_version": versions[0],
        "plan": plan,
        "migration_required": bool(plan),
    }
    if check_only:
        if not plan:
            _, graph, current_problems = validated_snapshot(task_dir)
            return envelope("migrate", ok=not current_problems, result=result, graph=graph, problems=current_problems), 0 if not current_problems else 1
        return envelope("migrate", ok=True, result=result), 0
    if not plan:
        _, graph, current_problems = validated_snapshot(task_dir)
        return envelope("migrate", ok=not current_problems, result={**result, "migrated": False}, graph=graph, problems=current_problems), 0 if not current_problems else 1

    descriptor, _, lock_problems = acquire_write_lock(task_dir)
    if lock_problems:
        return envelope("migrate", ok=False, problems=lock_problems), 1
    try:
        locked_tickets, locked_read_problems = read_raw_tickets(task_dir)
        if locked_read_problems:
            return envelope("migrate", ok=False, problems=locked_read_problems), 1
        locked_versions = sorted({ticket["schema_version"] for ticket in locked_tickets})
        if len(locked_versions) != 1:
            problems = [
                problem(
                    "contract",
                    "mixed_schema_versions",
                    "All tickets must have one schema version before migration.",
                )
            ]
            return envelope("migrate", ok=False, problems=problems), 1
        locked_plan, locked_plan_problems = migration_plan(locked_versions[0])
        if locked_plan_problems:
            return envelope("migrate", ok=False, problems=locked_plan_problems), 1
        if locked_versions != versions or locked_plan != plan:
            problems = [
                problem(
                    "storage",
                    "migration_state_changed",
                    "Graph schema state changed before the exclusive migration lock was acquired.",
                )
            ]
            return envelope("migrate", ok=False, problems=problems), 1
        migrated = locked_tickets
        for step in locked_plan:
            migrate = MIGRATIONS[step["from"]]
            migrated = [
                {**migrate(public_ticket(ticket)), "_path": ticket["_path"]}
                for ticket in migrated
            ]
        validation_problems = [
            item
            for ticket in migrated
            for item in validate_ticket(public_ticket(ticket), ticket["_path"])
        ]
        authority, authority_problems = authority_index(task_dir)
        graph_problems, _ = validate_graph(
            migrated, authority, has_hld=(task_dir / "HLD.md").is_file()
        )
        problems = validation_problems + authority_problems + graph_problems
        if problems:
            return envelope("migrate", ok=False, problems=problems), 1
        transaction_problems = commit_graph_transaction(task_dir, migrated, "migrate")
        if transaction_problems:
            return envelope("migrate", ok=False, problems=transaction_problems), 1
        _, graph, committed_problems = validated_snapshot(task_dir)
        return envelope("migrate", ok=not committed_problems, result={**result, "migrated": True}, graph=graph, problems=committed_problems), 0 if not committed_problems else 1
    finally:
        release_lock(descriptor)


def migrate_graph(
    task_dir: Path, *, check_only: bool
) -> tuple[dict[str, object], int]:
    if not check_only:
        return migrate_graph_unlocked(task_dir, check_only=False)
    descriptor, _, lock_problems = acquire_read_lock(task_dir)
    if lock_problems:
        return envelope("migrate", ok=False, problems=lock_problems), 1
    try:
        return migrate_graph_unlocked(task_dir, check_only=True)
    finally:
        release_lock(descriptor)
