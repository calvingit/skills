"""CLI parsing and JSON emission for the execution graph public seam."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from .batch import create_batch, reconcile_batch, recover_transaction
from .contracts import emit, envelope, problem
from .lifecycle import mutate_ticket
from .migrations import migrate_graph
from .queries import inspect, list_tickets, show_ticket


def argument_failure(operation: str, detail: str) -> int:
    emit(envelope(operation, ok=False, problems=[problem("contract", "invalid_arguments", detail)]))
    return 2


def read_request(source: str) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
    try:
        text = sys.stdin.read() if source == "-" else Path(source).read_text(encoding="utf-8")
        value = json.loads(text)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return None, [problem("contract", "invalid_request_json", str(exc), path=source)]
    if not isinstance(value, dict):
        return None, [problem("contract", "invalid_request", "Mutation request must be a JSON object.", path=source)]
    return value, []


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    operation = arguments[0] if arguments else "unknown"
    if operation == "inspect":
        if len(arguments) != 2:
            return argument_failure(operation, "Usage: ticket_graph.py inspect <task-dir>")
        payload, exit_code = inspect(Path(arguments[1]).expanduser().resolve())
    elif operation == "show":
        if len(arguments) != 3:
            return argument_failure(operation, "Usage: ticket_graph.py show <task-dir> <ticket-id>")
        payload, exit_code = show_ticket(Path(arguments[1]).expanduser().resolve(), arguments[2])
    elif operation == "list":
        if len(arguments) < 2 or (len(arguments) - 2) % 2:
            return argument_failure(operation, "Usage: ticket_graph.py list <task-dir> [--phase <phase>] [--readiness <ready|blocked>]")
        phase: str | None = None
        readiness: str | None = None
        for name, value in zip(arguments[2::2], arguments[3::2]):
            if name == "--phase" and value in {"open", "in_progress", "done", "superseded"}: phase = value
            elif name == "--readiness" and value in {"ready", "blocked"}: readiness = value
            else: return argument_failure(operation, f"Unsupported list filter: {name} {value}")
        payload, exit_code = list_tickets(Path(arguments[1]).expanduser().resolve(), phase=phase, readiness=readiness)
    elif operation in {"start", "retry", "block", "unblock", "complete", "reopen"}:
        if len(arguments) != 5 or arguments[3] != "--input": return argument_failure(operation, f"Usage: ticket_graph.py {operation} <task-dir> <ticket-id> --input <path|->")
        request, request_problems = read_request(arguments[4])
        if request_problems or request is None:
            emit(envelope(operation, ok=False, problems=request_problems)); return 2
        payload, exit_code = mutate_ticket(operation, Path(arguments[1]).expanduser().resolve(), arguments[2], request)
    elif operation in {"create-batch", "reconcile-batch"}:
        if len(arguments) != 4 or arguments[2] != "--input": return argument_failure(operation, f"Usage: ticket_graph.py {operation} <task-dir> --input <path|->")
        request, request_problems = read_request(arguments[3])
        if request_problems or request is None:
            emit(envelope(operation, ok=False, problems=request_problems)); return 2
        command = create_batch if operation == "create-batch" else reconcile_batch
        payload, exit_code = command(Path(arguments[1]).expanduser().resolve(), request)
    elif operation == "recover":
        if len(arguments) != 3: return argument_failure(operation, "Usage: ticket_graph.py recover <task-dir> <rollback|commit>")
        payload, exit_code = recover_transaction(Path(arguments[1]).expanduser().resolve(), arguments[2])
    elif operation == "migrate":
        if len(arguments) not in {2, 3} or (len(arguments) == 3 and arguments[2] != "--check"): return argument_failure(operation, "Usage: ticket_graph.py migrate <task-dir> [--check]")
        payload, exit_code = migrate_graph(Path(arguments[1]).expanduser().resolve(), check_only=len(arguments) == 3)
    else:
        return argument_failure(operation, "Supported commands: inspect, list, show, start, retry, block, unblock, complete, reopen, create-batch, reconcile-batch, recover, migrate")
    emit(payload)
    return exit_code
