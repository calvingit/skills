"""Pure execution-graph validation and projections."""

from __future__ import annotations

from collections import Counter
from typing import Any

from .contracts import ACTIVE_PHASES, problem

def find_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []
    cycles: set[tuple[str, ...]] = set()

    def canonical(nodes: list[str]) -> tuple[str, ...]:
        core = nodes[:-1]
        rotations = [tuple(core[index:] + core[:index]) for index in range(len(core))]
        best = min(rotations)
        return best + (best[0],)

    def visit(node: str) -> None:
        visiting.add(node)
        stack.append(node)
        for dependency in graph.get(node, []):
            if dependency in visiting:
                start = stack.index(dependency)
                cycles.add(canonical(stack[start:] + [dependency]))
            elif dependency not in visited:
                visit(dependency)
        stack.pop()
        visiting.remove(node)
        visited.add(node)

    for node in sorted(graph):
        if node not in visited:
            visit(node)
    return [list(cycle) for cycle in sorted(cycles)]


def validate_graph(
    tickets: list[dict[str, Any]],
    authority: dict[str, set[str]],
    *,
    has_hld: bool,
) -> tuple[list[dict[str, str]], dict[str, list[str]]]:
    problems: list[dict[str, str]] = []
    by_id: dict[str, dict[str, Any]] = {}
    counts = Counter(ticket["id"] for ticket in tickets)
    for ticket_id, count in sorted(counts.items()):
        if count > 1:
            problems.append(problem("graph", "duplicate_ticket_id", f"Ticket ID is duplicated: {ticket_id}", ticket_id=ticket_id))
    for ticket in tickets:
        by_id.setdefault(ticket["id"], ticket)

    for ticket in tickets:
        ticket_id = ticket["id"]
        path = ticket["_path"]
        for requirement in ticket["covers"]["requirements"]:
            if requirement not in authority["requirements"]:
                problems.append(problem("authority", "unknown_requirement", f"Ticket references unknown SPEC requirement: {requirement}", ticket_id=ticket_id, path=path))
        for acceptance_id in ticket["covers"]["spec_acceptance"]:
            if acceptance_id not in authority["spec_acceptance"]:
                problems.append(problem("authority", "unknown_spec_acceptance", f"Ticket references unknown SPEC Acceptance ID: {acceptance_id}", ticket_id=ticket_id, path=path))
        if ticket["design_decisions"] and not has_hld:
            problems.append(problem("authority", "missing_hld", "Ticket references design decisions but HLD.md was not found.", ticket_id=ticket_id, path=path))
        for decision in ticket["design_decisions"]:
            if decision not in authority["design_decisions"]:
                problems.append(problem("authority", "unknown_design_decision", f"Ticket references unknown HLD decision: {decision}", ticket_id=ticket_id, path=path))
        if not ticket["covers"]["requirements"] and not ticket["covers"]["spec_acceptance"] and not ticket["design_decisions"]:
            problems.append(problem("graph", "missing_delivery_coverage", "Ticket must cover a SPEC R/AC or an HLD D ID.", ticket_id=ticket_id, path=path))

        for dependency in ticket["dependencies"]:
            if dependency == ticket_id:
                problems.append(problem("graph", "self_dependency", "Ticket depends on itself.", ticket_id=ticket_id, path=path))
                continue
            target = by_id.get(dependency)
            if target is None:
                problems.append(problem("graph", "dangling_dependency", f"Dependency does not exist: {dependency}", ticket_id=ticket_id, path=path))
            elif target["lifecycle"]["phase"] == "superseded":
                problems.append(problem("graph", "dependency_on_superseded", f"Dependency points to superseded ticket: {dependency}", ticket_id=ticket_id, path=path))
        if ticket["lifecycle"]["phase"] in {"in_progress", "done"}:
            unfinished = [dependency for dependency in ticket["dependencies"] if dependency in by_id and by_id[dependency]["lifecycle"]["phase"] != "done"]
            if unfinished:
                problems.append(problem("graph", "active_with_unfinished_dependencies", f"{ticket['lifecycle']['phase']} ticket has unfinished dependencies: {', '.join(unfinished)}", ticket_id=ticket_id, path=path))
        supersession = ticket["supersession"]
        if isinstance(supersession, dict) and supersession["replacement_ticket_id"] is not None:
            replacement_id = supersession["replacement_ticket_id"]
            replacement = by_id.get(replacement_id)
            if replacement_id == ticket_id or replacement is None or replacement["lifecycle"]["phase"] == "superseded":
                problems.append(problem("graph", "invalid_supersession_replacement", f"Supersession replacement must resolve to a different active ticket: {replacement_id}", ticket_id=ticket_id, path=path))

    active = [ticket for ticket in tickets if ticket["lifecycle"]["phase"] in ACTIVE_PHASES]
    coverage = {
        "requirements": sorted(authority["requirements"] - {value for ticket in active for value in ticket["covers"]["requirements"]}),
        "spec_acceptance": sorted(authority["spec_acceptance"] - {value for ticket in active for value in ticket["covers"]["spec_acceptance"]}),
        "design_decisions": sorted(authority["design_decisions"] - {value for ticket in active for value in ticket["design_decisions"]}),
    }
    for kind, missing in coverage.items():
        if missing:
            problems.append(problem("authority", "coverage_gap", f"Active graph does not cover {kind}: {', '.join(missing)}", field=kind))

    dependency_graph = {
        ticket["id"]: [dependency for dependency in ticket["dependencies"] if dependency in by_id and by_id[dependency]["lifecycle"]["phase"] in ACTIVE_PHASES]
        for ticket in active
    }
    for cycle in find_cycles(dependency_graph):
        problems.append(problem("graph", "dependency_cycle", " -> ".join(cycle)))
    return problems, coverage


def blocked_reasons(ticket: dict[str, Any], by_id: dict[str, dict[str, Any]]) -> list[dict[str, object]]:
    reasons: list[dict[str, object]] = []
    for dependency in ticket["dependencies"]:
        target = by_id.get(dependency)
        if target is None or target["lifecycle"]["phase"] != "done":
            reasons.append({"source": "dependency", "ticket_id": dependency})
    blocker = ticket["execution"]["blocker"]
    if blocker is not None:
        reasons.append({"source": "execution", **blocker})
    return reasons


def graph_projection(
    tickets: list[dict[str, Any]], *, valid: bool = True, coverage: dict[str, list[str]] | None = None
) -> dict[str, object]:
    by_id = {ticket["id"]: ticket for ticket in tickets}
    frontier: list[str] = []
    blocked: list[dict[str, object]] = []
    for ticket in tickets:
        if ticket["lifecycle"]["phase"] != "open":
            continue
        reasons = blocked_reasons(ticket, by_id)
        if reasons:
            blocked.append({"ticket_id": ticket["id"], "reasons": reasons})
        else:
            frontier.append(ticket["id"])

    active = [ticket for ticket in tickets if ticket["lifecycle"]["phase"] in ACTIVE_PHASES]
    return {
        "valid": valid,
        "frontier": frontier,
        "blocked": blocked,
        "in_progress": [
            ticket["id"] for ticket in tickets if ticket["lifecycle"]["phase"] == "in_progress"
        ],
        "done": [ticket["id"] for ticket in tickets if ticket["lifecycle"]["phase"] == "done"],
        "superseded": [
            ticket["id"] for ticket in tickets if ticket["lifecycle"]["phase"] == "superseded"
        ],
        "coverage_gaps": coverage
        if coverage is not None
        else {"requirements": [], "spec_acceptance": [], "design_decisions": []},
        "all_active_done": bool(active)
        and all(ticket["lifecycle"]["phase"] == "done" for ticket in active),
    }


def ticket_readiness(
    ticket: dict[str, Any], by_id: dict[str, dict[str, Any]]
) -> tuple[str | None, list[dict[str, object]]]:
    if ticket["lifecycle"]["phase"] != "open":
        return None, []
    reasons = blocked_reasons(ticket, by_id)
    return ("blocked" if reasons else "ready"), reasons


def public_ticket(ticket: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in ticket.items() if not key.startswith("_")}
