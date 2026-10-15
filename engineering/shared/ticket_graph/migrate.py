"""One-off local migration from v3 Markdown tickets to v4 contract + runtime state.

v3 kept ``lifecycle`` and ``execution`` inside each ticket file. v4 stores the
stable contract in the ticket and the same execution facts in
``.loop/state.json``. This conversion keeps ticket IDs, contracts, dependencies
and confirmed execution records; what it cannot confirm it reports instead of
inventing, and it never claims a completion the old record does not show.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import frontmatter, runtime
from .authority import authority_index
from .contracts import CURRENT_SCHEMA_VERSION, envelope, problem, validate_contract
from .graph import validate_graph
from .frontmatter import FrontmatterError
from .store import STATE_RELATIVE, acquire_write_lock, commit_graph_transaction, release_lock, validated_snapshot
from .ticket_markdown import TicketFormatError, parse_body, split_document

V3_VERSION = 3
V3_FRONTMATTER_FIELDS = (
    "schema_version", "id", "covers", "referenced_design_decisions", "dependencies",
    "lifecycle", "execution", "supersession",
)


def parse_v3_ticket(text: str) -> tuple[dict[str, Any], dict[str, Any], str]:
    """Split a v3 ticket document into its v4 contract, runtime entry and body."""
    head, body = split_document(text)
    meta = frontmatter.loads(head)
    if meta.get("schema_version") != V3_VERSION:
        raise TicketFormatError("unsupported_schema_version", f"Expected a v3 ticket, found schema_version {meta.get('schema_version')!r}.")
    lifecycle = meta.get("lifecycle")
    execution = meta.get("execution")
    if not isinstance(lifecycle, dict) or not isinstance(execution, dict):
        raise TicketFormatError("invalid_frontmatter", "A v3 ticket requires lifecycle and execution objects.")
    ticket = {key: value for key, value in meta.items() if key in V3_FRONTMATTER_FIELDS}
    ticket.update(parse_body(body))
    ticket["schema_version"] = CURRENT_SCHEMA_VERSION
    ticket.pop("lifecycle")
    ticket.pop("execution")
    if ticket.get("supersession") is None:
        ticket.pop("supersession")
    entry: dict[str, Any] = {"phase": lifecycle.get("phase", "open")}
    attempt = execution.get("attempt_sequence", 0)
    entry["attempt"] = attempt
    for name in ("authority", "blocker", "current_attempt", "reopen_context", "review"):
        if execution.get(name) is not None:
            entry[name] = execution[name]
    evidence = execution.get("evidence") or {}
    if evidence:
        # v3 recorded no attempt with each judgement; the ticket's recorded
        # attempt is the only attempt it can belong to, and the caller is told.
        entry["evidence"] = {
            acceptance_id: {"attempt": attempt, "summary": item["summary"]}
            for acceptance_id, item in evidence.items()
            if isinstance(item, dict) and isinstance(item.get("summary"), str)
        }
        if len(entry["evidence"]) != len(evidence):
            raise TicketFormatError("unmigratable_execution_record", "Evidence entries need a summary to be carried over.")
    return ticket, entry, body


def migrate_v3(task_dir: Path) -> tuple[dict[str, object], int]:
    descriptor, _, lock_problems = acquire_write_lock(task_dir)
    if lock_problems:
        return envelope("migrate-v3", ok=False, problems=lock_problems), 1
    try:
        if (task_dir / ".ticket-graph-transaction").exists():
            return envelope("migrate-v3", ok=False, problems=[problem("recovery", "recovery_required", "An unfinished graph transaction requires recovery.")]), 1
        if (task_dir / STATE_RELATIVE).is_file():
            return envelope("migrate-v3", ok=False, problems=[problem("storage", "runtime_state_present", "Runtime state already exists; migrate only a graph that still stores execution records in its tickets.", path=STATE_RELATIVE)]), 1
        tickets_dir = task_dir / "tickets"
        if not tickets_dir.is_dir():
            return envelope("migrate-v3", ok=False, problems=[problem("contract", "missing_tickets_directory", "tickets/ was not found.")]), 1
        problems: list[dict[str, str]] = []
        tickets: list[dict[str, Any]] = []
        for path in sorted(tickets_dir.glob("*.json")):
            problems.append(problem("contract", "unsupported_ticket_format", "migrate-v3 converts v3 Markdown tickets only.", path=path.relative_to(task_dir).as_posix()))
        for path in sorted(tickets_dir.glob("*.md")):
            relative = path.relative_to(task_dir).as_posix()
            try:
                ticket, entry, body = parse_v3_ticket(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError) as exc:
                problems.append(problem("contract", "unreadable_ticket", str(exc), path=relative))
                continue
            except FrontmatterError as exc:
                problems.append(problem("contract", "invalid_frontmatter", str(exc), path=relative))
                continue
            except TicketFormatError as exc:
                problems.append(problem("contract", exc.code, exc.detail, path=relative))
                continue
            ticket_id = ticket.get("id")
            if isinstance(ticket_id, str) and not (path.stem == ticket_id or path.stem.startswith(ticket_id + "-")):
                problems.append(problem("contract", "ticket_filename_mismatch", "Ticket filename must begin with its immutable ID.", ticket_id=ticket_id, path=relative))
                continue
            ticket["runtime"] = entry
            problems.extend(validate_contract(ticket, relative))
            problems.extend(runtime.validate_entry(entry, ticket, STATE_RELATIVE, ticket_id if isinstance(ticket_id, str) else None))
            ticket["_path"] = relative
            ticket["_body"] = body
            tickets.append(ticket)
        if not tickets and not problems:
            problems.append(problem("contract", "no_tickets", "tickets/ contains no Markdown tickets."))
        if problems:
            return envelope("migrate-v3", ok=False, problems=problems), 1
        authority, authority_problems = authority_index(task_dir)
        graph_problems, _ = validate_graph(tickets, authority, has_solution=(task_dir / "SOLUTION.md").is_file())
        problems = authority_problems + graph_problems
        if problems:
            return envelope("migrate-v3", ok=False, problems=problems), 1
        transaction_problems = commit_graph_transaction(task_dir, tickets, "migrate-v3", runtime.state_from(tickets))
        if transaction_problems:
            return envelope("migrate-v3", ok=False, problems=transaction_problems), 1
        _, graph, committed_problems = validated_snapshot(task_dir)
        return (
            envelope(
                "migrate-v3",
                ok=not committed_problems,
                result={
                    "migrated": [ticket["id"] for ticket in tickets],
                    "notes": ["Evidence attempt numbers use each ticket's recorded attempt; v3 stored none."],
                },
                graph=graph,
                problems=committed_problems,
            ),
            0 if not committed_problems else 1,
        )
    finally:
        release_lock(descriptor)
