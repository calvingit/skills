"""Filesystem storage, locking, transaction, and recovery for execution graphs.

One graph is stored in two places on purpose: the stable contract in
``tickets/*.md`` and the ephemeral runtime progress in ``.loop/state.json``.
Readers always see them merged; writers either replace the state file alone
(ordinary progress) or switch both stores inside one recoverable transaction
(contract revision).
"""

from __future__ import annotations

import fcntl
import json
import os
import shutil
from pathlib import Path
from typing import Any

from . import runtime
from .authority import authority_index, authority_current, authority_fingerprint
from .contracts import problem, validate_contract
from .frontmatter import FrontmatterError
from .graph import graph_projection, validate_graph
from .ticket_markdown import RUNTIME_KEY, TicketFormatError, parse_ticket, render_ticket

STATE_RELATIVE = runtime.STATE_FILE


def transaction_path_allowed(relative: str) -> bool:
    """Files a graph transaction may switch: the tickets and the runtime state."""
    if ".." in Path(relative).parts:
        return False
    return relative == STATE_RELATIVE or relative.startswith("tickets/")


def load_contracts(task_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Parse and validate ticket contracts without reading runtime state."""
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
    markdown_paths = sorted(tickets_dir.glob("*.md"))
    for path in sorted(tickets_dir.glob("*.json")):
        problems.append(problem("contract", "unsupported_ticket_format",
            "v4 stores Markdown tickets only. Finish and archive legacy JSON tasks with their own tooling.",
            path=path.relative_to(task_dir).as_posix()))
    for path in markdown_paths:
        relative = path.relative_to(task_dir).as_posix()
        try:
            value, body = parse_ticket(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as exc:
            problems.append(problem("contract", "unreadable_ticket", str(exc), path=relative))
            continue
        except FrontmatterError as exc:
            problems.append(problem("contract", "invalid_frontmatter", str(exc), path=relative))
            continue
        except TicketFormatError as exc:
            problems.append(problem("contract", exc.code, exc.detail, path=relative))
            continue
        contract_problems = validate_contract(value, relative)
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
        value["_body"] = body
        tickets.append(value)
    if not tickets and not problems:
        problems.append(problem("contract", "no_tickets", "tickets/ contains no Markdown tickets."))
    tickets.sort(key=lambda ticket: int(ticket["id"][1:]))
    return tickets, problems


def load_graph(task_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Load ticket contracts together with their current runtime progress."""
    tickets, problems = load_contracts(task_dir)
    if problems:
        return [], problems
    state, state_problems = runtime.load_state(task_dir)
    problems = state_problems + runtime.attach_runtime(tickets, state)
    if problems:
        return [], problems
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
        tickets, authority, has_solution=(task_dir / "SOLUTION.md").is_file()
    )
    graph_problems = authority_problems + graph_problems
    graph = graph_projection(tickets, valid=not graph_problems, coverage=coverage)
    stale = [ticket["id"] for ticket in tickets if ticket["runtime"]["phase"] != "superseded" and not authority_current(task_dir, ticket)]
    graph["authority_fingerprint"] = authority_fingerprint(task_dir)
    graph["stale_authority"] = stale
    graph["delivery_ready"] = graph["all_active_done"] and not stale and not graph_problems
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


def serialize_ticket(path: Path, ticket: dict[str, Any]) -> None:
    """Write the contract of a ticket; runtime progress belongs to state.json."""
    contract = {key: value for key, value in ticket.items() if key != RUNTIME_KEY}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_ticket(contract, ticket.get("_body")), encoding="utf-8")


def commit_graph_transaction(
    task_dir: Path,
    tickets: list[dict[str, Any]],
    operation: str,
    state: dict[str, Any],
) -> list[dict[str, str]]:
    """Stage, validate and switch Markdown contracts together with runtime state."""
    transaction = task_dir / ".ticket-graph-transaction"
    staging = transaction / "staging"
    backup = transaction / "backup"
    switching = False
    try:
        runtime.ensure_loop(task_dir)
        transaction.mkdir()
        (staging / "tickets").mkdir(parents=True)
        (backup / "tickets").mkdir(parents=True)
        for authority_name in ("SPEC.md", "ACCEPTANCE.md", "SOLUTION.md"):
            source = task_dir / authority_name
            if source.is_file():
                shutil.copy2(source, staging / authority_name)
        original_files = sorted(
            [path.relative_to(task_dir).as_posix() for path in (task_dir / "tickets").glob("*.md")]
            + ([STATE_RELATIVE] if (task_dir / STATE_RELATIVE).is_file() else [])
        )
        target_files = sorted([ticket["_path"] for ticket in tickets] + [STATE_RELATIVE])
        for relative in original_files:
            destination = backup / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(task_dir / relative, destination)
        for ticket in tickets:
            serialize_ticket(staging / ticket["_path"], ticket)
        staged_state = staging / STATE_RELATIVE
        staged_state.parent.mkdir(parents=True, exist_ok=True)
        staged_state.write_text(runtime.render_state(state), encoding="utf-8")
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
        switching = True
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
    except TicketFormatError as exc:
        shutil.rmtree(transaction, ignore_errors=True)
        return [problem("contract", exc.code, exc.detail)]
    except OSError as exc:
        # No live files have changed if staging fails before the switch.
        if not switching:
            shutil.rmtree(transaction, ignore_errors=True)
        return [problem("storage", "transaction_failed", str(exc), path=transaction.name)]


def atomic_copy(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.recovery.tmp")
    shutil.copy2(source, temporary)
    os.replace(temporary, target)
