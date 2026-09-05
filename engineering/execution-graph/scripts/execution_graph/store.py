"""Filesystem storage, locking, transaction, and recovery for execution graphs."""

from __future__ import annotations

import fcntl
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from .authority import authority_index
from .contracts import problem, validate_shape, validate_string_list, validate_ticket
from .graph import graph_projection, public_ticket, validate_graph

def load_graph(task_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    problems: list[dict[str, str]] = []
    tickets_dir = task_dir / "tickets"
    tickets: list[dict[str, Any]] = []
    if not task_dir.is_dir():
        return [], [problem("contract", "missing_task_directory", "Task directory does not exist.")]
    if not (task_dir / "SPEC.md").is_file():
        problems.append(problem("authority", "missing_spec", "SPEC.md was not found."))
    if not tickets_dir.is_dir():
        problems.append(problem("contract", "missing_tickets_directory", "tickets/ was not found."))
        return [], problems
    markdown = sorted(path.relative_to(task_dir).as_posix() for path in tickets_dir.glob("*.md"))
    for relative in markdown:
        problems.append(
            problem(
                "contract",
                "unsupported_markdown_ticket",
                "Markdown tickets are not supported by the JSON graph protocol.",
                path=relative,
            )
        )
    for path in sorted(tickets_dir.glob("*.json")):
        relative = path.relative_to(task_dir).as_posix()
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            problems.append(problem("contract", "invalid_json", str(exc), path=relative))
            continue
        if not isinstance(value, dict):
            problems.append(
                problem("contract", "invalid_ticket_document", "Ticket must be a JSON object.", path=relative)
            )
            continue
        contract_problems = validate_ticket(value, relative)
        ticket_id = value.get("id")
        if isinstance(ticket_id, str) and not (
            path.stem == ticket_id or path.stem.startswith(ticket_id + "-")
        ):
            contract_problems.append(
                problem(
                    "contract",
                    "ticket_filename_mismatch",
                    "Ticket filename must begin with its immutable ID.",
                    ticket_id=ticket_id,
                    path=relative,
                )
            )
        problems.extend(contract_problems)
        if contract_problems:
            continue
        value["_path"] = relative
        tickets.append(value)
    if not tickets and not markdown:
        problems.append(problem("contract", "no_tickets", "tickets/ contains no JSON tickets."))
    tickets.sort(key=lambda ticket: int(ticket["id"][1:]))
    return tickets, problems


def validated_snapshot(
    task_dir: Path,
    *,
    allow_transaction: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, object], list[dict[str, str]]]:
    transaction = task_dir / ".ticket-graph-transaction"
    if transaction.exists() and not allow_transaction:
        return [], {}, [
            problem(
                "recovery",
                "recovery_required",
                "An unfinished graph transaction requires explicit recovery.",
                path=transaction.name,
            )
        ]
    tickets, problems = load_graph(task_dir)
    if problems:
        return [], {}, problems
    authority, authority_problems = authority_index(task_dir)
    graph_problems, coverage = validate_graph(
        tickets, authority, has_hld=(task_dir / "HLD.md").is_file()
    )
    graph_problems = authority_problems + graph_problems
    graph = graph_projection(tickets, valid=not graph_problems, coverage=coverage)
    return tickets, graph, graph_problems


def acquire_write_lock(task_dir: Path) -> tuple[int | None, Path, list[dict[str, str]]]:
    path = task_dir
    try:
        descriptor = os.open(path, os.O_RDONLY)
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return None, path, [problem("storage", "write_locked", "Another graph operation holds the task lock.", path=str(path))]
    except OSError as exc:
        return None, path, [problem("storage", "lock_failed", str(exc), path=str(path))]
    return descriptor, path, []


def acquire_read_lock(task_dir: Path) -> tuple[int | None, Path, list[dict[str, str]]]:
    path = task_dir
    try:
        descriptor = os.open(path, os.O_RDONLY)
        fcntl.flock(descriptor, fcntl.LOCK_SH)
    except OSError as exc:
        return None, path, [problem("storage", "lock_failed", str(exc), path=str(path))]
    return descriptor, path, []


def release_lock(descriptor: int | None) -> None:
    if descriptor is not None:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def atomic_write_ticket(task_dir: Path, ticket: dict[str, Any]) -> list[dict[str, str]]:
    target = task_dir / ticket["_path"]
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=target.parent,
            prefix=f".{target.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary_name = temporary.name
            json.dump(public_ticket(ticket), temporary, ensure_ascii=False, indent=2)
            temporary.write("\n")
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_name, target)
    except OSError as exc:
        if temporary_name is not None:
            try:
                Path(temporary_name).unlink()
            except FileNotFoundError:
                pass
        return [problem("storage", "write_failed", str(exc), ticket_id=ticket.get("id"), path=ticket.get("_path"))]
    return []


def serialize_ticket(path: Path, ticket: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(public_ticket(ticket), handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def commit_graph_transaction(
    task_dir: Path, tickets: list[dict[str, Any]], operation: str
) -> list[dict[str, str]]:
    transaction = task_dir / ".ticket-graph-transaction"
    staging = transaction / "staging"
    backup = transaction / "backup"
    try:
        transaction.mkdir()
        (staging / "tickets").mkdir(parents=True)
        (backup / "tickets").mkdir(parents=True)
        for authority_name in ("SPEC.md", "HLD.md"):
            source = task_dir / authority_name
            if source.is_file():
                shutil.copy2(source, staging / authority_name)
        original_files = sorted(
            path.relative_to(task_dir).as_posix()
            for path in (task_dir / "tickets").glob("*.json")
        )
        target_files = sorted(ticket["_path"] for ticket in tickets)
        for relative in original_files:
            destination = backup / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(task_dir / relative, destination)
        for ticket in tickets:
            serialize_ticket(staging / ticket["_path"], ticket)
        manifest = {
            "operation": operation,
            "state": "prepared",
            "original_files": original_files,
            "target_files": target_files,
        }
        (transaction / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        _, _, staging_problems = validated_snapshot(staging, allow_transaction=True)
        if staging_problems:
            shutil.rmtree(transaction)
            return staging_problems
        manifest["state"] = "switching"
        (transaction / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        for relative in target_files:
            target = task_dir / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name(f".{target.name}.transaction.tmp")
            shutil.copy2(staging / relative, temporary)
            os.replace(temporary, target)
        _, _, committed_problems = validated_snapshot(task_dir, allow_transaction=True)
        if committed_problems:
            return committed_problems
        shutil.rmtree(transaction)
        return []
    except FileExistsError:
        return [problem("recovery", "recovery_required", "An unfinished graph transaction already exists.", path=transaction.name)]
    except OSError as exc:
        return [problem("storage", "transaction_failed", str(exc), path=transaction.name)]


def atomic_copy(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.recovery.tmp")
    shutil.copy2(source, temporary)
    os.replace(temporary, target)


def read_raw_tickets(
    task_dir: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    problems: list[dict[str, str]] = []
    transaction = task_dir / ".ticket-graph-transaction"
    if transaction.exists():
        return [], [problem("recovery", "recovery_required", "An unfinished graph transaction requires recovery.")]
    tickets_dir = task_dir / "tickets"
    if not task_dir.is_dir() or not (task_dir / "SPEC.md").is_file():
        return [], [problem("authority", "missing_spec", "A task directory with SPEC.md is required.")]
    if not tickets_dir.is_dir():
        return [], [problem("contract", "missing_tickets_directory", "tickets/ was not found.")]
    markdown = sorted(tickets_dir.glob("*.md"))
    if markdown:
        return [], [problem("contract", "unsupported_markdown_ticket", "Migration accepts JSON tickets only.", path=markdown[0].name)]
    tickets: list[dict[str, Any]] = []
    for path in sorted(tickets_dir.glob("*.json")):
        relative = path.relative_to(task_dir).as_posix()
        try:
            ticket = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            problems.append(problem("contract", "invalid_json", str(exc), path=relative))
            continue
        if not isinstance(ticket, dict):
            problems.append(problem("contract", "invalid_ticket_document", "Ticket must be a JSON object.", path=relative))
            continue
        version = ticket.get("schema_version")
        if not isinstance(version, int) or isinstance(version, bool) or version < 0:
            problems.append(invalid_field(relative, ticket.get("id") if isinstance(ticket.get("id"), str) else None, "schema_version", "schema_version must be a non-negative integer."))
            continue
        ticket["_path"] = relative
        tickets.append(ticket)
    if not tickets and not problems:
        problems.append(problem("contract", "no_tickets", "tickets/ contains no JSON tickets."))
    return tickets, problems
