"""Read-only execution graph queries."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .contracts import envelope, problem
from .graph import blocked_reasons, public_ticket, ticket_readiness
from .store import acquire_read_lock, release_lock, validated_snapshot

def inspect(task_dir: Path) -> tuple[dict[str, object], int]:
    descriptor, _, lock_problems = acquire_read_lock(task_dir)
    if lock_problems:
        return envelope("inspect", ok=False, problems=lock_problems), 1
    try:
        _, graph, graph_problems = validated_snapshot(task_dir)
        return (
            envelope(
                "inspect",
                ok=not graph_problems,
                result={"task_dir": str(task_dir)},
                graph=graph,
                problems=graph_problems,
            ),
            0 if not graph_problems else 1,
        )
    finally:
        release_lock(descriptor)


def list_tickets(
    task_dir: Path, *, phase: str | None, readiness: str | None
) -> tuple[dict[str, object], int]:
    descriptor, _, lock_problems = acquire_read_lock(task_dir)
    if lock_problems:
        return envelope("list", ok=False, problems=lock_problems), 1
    try:
        tickets, graph, problems = validated_snapshot(task_dir)
        if problems:
            return envelope("list", ok=False, graph=graph, problems=problems), 1
        by_id = {ticket["id"]: ticket for ticket in tickets}
        summaries: list[dict[str, object]] = []
        for ticket in tickets:
            ticket_phase = ticket["lifecycle"]["phase"]
            ticket_ready, reasons = ticket_readiness(ticket, by_id)
            if phase is not None and ticket_phase != phase:
                continue
            if readiness is not None and ticket_ready != readiness:
                continue
            summaries.append(
                {
                    "id": ticket["id"],
                    "title": ticket["title"],
                    "phase": ticket_phase,
                    "readiness": ticket_ready,
                    "blocked_reasons": reasons,
                }
            )
        return envelope("list", ok=True, result={"tickets": summaries}, graph=graph), 0
    finally:
        release_lock(descriptor)


def show_ticket(task_dir: Path, ticket_id: str) -> tuple[dict[str, object], int]:
    descriptor, _, lock_problems = acquire_read_lock(task_dir)
    if lock_problems:
        return envelope("show", ok=False, problems=lock_problems), 1
    try:
        tickets, graph, problems = validated_snapshot(task_dir)
        if problems:
            return envelope("show", ok=False, graph=graph, problems=problems), 1
        by_id = {ticket["id"]: ticket for ticket in tickets}
        ticket = by_id.get(ticket_id)
        if ticket is None:
            return (
                envelope(
                    "show",
                    ok=False,
                    graph=graph,
                    problems=[
                        problem("graph", "unknown_ticket", f"Ticket does not exist: {ticket_id}", ticket_id=ticket_id)
                    ],
                ),
                1,
            )
        readiness, reasons = ticket_readiness(ticket, by_id)
        return (
            envelope(
                "show",
                ok=True,
                result={"ticket": public_ticket(ticket), "readiness": readiness, "blocked_reasons": reasons},
                graph=graph,
            ),
            0,
        )
    finally:
        release_lock(descriptor)
