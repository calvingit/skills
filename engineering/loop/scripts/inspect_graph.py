#!/usr/bin/env python3
"""Inspect a Loop task graph without changing any files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


ALLOWED_STATUSES = {"ready", "blocked", "in_progress", "done", "superseded"}
ACTIVE_STATUSES = ALLOWED_STATUSES - {"superseded"}
NONE_MARKERS = ("none", "n/a", "not applicable", "无", "没有")
HEADING_RE = re.compile(r"^##\s+(.+?)\s*$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
MD_PATH_RE = re.compile(r"(?<![\w])([\w./-]+\.md)(?![\w])", re.IGNORECASE)
NUMERIC_ID_RE = re.compile(r"^(\d+)(?:[-_ ]|$)")
CHECKLIST_RE = re.compile(r"^\s*[-*+]\s+\[([ xX])\]\s+(AC[\w.-]*)\s+[—–-]\s+(.+?)\s*$", re.IGNORECASE)
EVIDENCE_RE = re.compile(r"^\s*[-*+]\s+(AC[\w.-]*)\s+[—–-]\s+passed\s+[—–-]\s+(.+?)\s*$", re.IGNORECASE)
DESIGN_DECL_RE = re.compile(r"^\s*[-*+]\s+\*{0,2}(D\d+)\*{0,2}\s+[—–-]", re.IGNORECASE)
DESIGN_REF_RE = re.compile(r"\b(D\d+)\b", re.IGNORECASE)
REQUIRED_SECTIONS = (
    "specification",
    "what to build",
    "constraints",
    "acceptance criteria",
    "blocked by",
    "execution evidence",
    "execution blocker",
)


@dataclass
class Ticket:
    file: Path
    relative: str
    numeric_id: str | None
    status: str | None
    blocked_lines: list[str]
    acceptance: dict[str, bool]
    execution_evidence: set[str]
    has_execution_blocker: bool
    design_decisions: set[str]
    dependency_tokens: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)


def problem(code: str, detail: str, ticket: str | None = None) -> dict[str, str]:
    item = {"code": code, "detail": detail}
    if ticket is not None:
        item["ticket"] = ticket
    return item


def section_map(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        match = HEADING_RE.match(line)
        if match:
            current = match.group(1).strip().lower()
            sections.setdefault(current, [])
        elif current is not None:
            sections[current].append(line)
    return sections


def first_value(lines: Iterable[str]) -> str | None:
    for line in lines:
        value = line.strip().lstrip("-*+ ").strip().strip("`").lower()
        if value:
            return value.split()[0]
    return None


def is_none_line(line: str) -> bool:
    value = line.strip().lstrip("-*+ ").strip().lower()
    return any(value == marker or value.startswith(marker + " ") or value.startswith(marker + "(") for marker in NONE_MARKERS)


def acceptance_items(lines: Iterable[str]) -> tuple[dict[str, bool], set[str], list[str]]:
    items: dict[str, bool] = {}
    duplicates: set[str] = set()
    unparsed: list[str] = []
    for line in lines:
        value = line.strip()
        if not value:
            continue
        match = CHECKLIST_RE.match(line)
        if match:
            acceptance_id = match.group(2).upper()
            if acceptance_id in items:
                duplicates.add(acceptance_id)
            else:
                items[acceptance_id] = match.group(1).lower() == "x"
        else:
            unparsed.append(value)
    return items, duplicates, unparsed


def evidence_items(lines: Iterable[str]) -> tuple[set[str], set[str], list[str]]:
    items: set[str] = set()
    duplicates: set[str] = set()
    unparsed: list[str] = []
    for line in lines:
        value = line.strip()
        if not value or is_none_line(value):
            continue
        plain = value.lstrip("-*+ ").strip().lower()
        if plain in {"pending", "待补充", "待填写"}:
            continue
        match = EVIDENCE_RE.match(line)
        if match:
            acceptance_id = match.group(1).upper()
            evidence = match.group(2).strip().lower()
            if evidence in {"pending", "待补充", "待填写"}:
                unparsed.append(value)
            elif acceptance_id in items:
                duplicates.add(acceptance_id)
            else:
                items.add(acceptance_id)
        else:
            unparsed.append(value)
    return items, duplicates, unparsed


def has_meaningful_content(lines: Iterable[str]) -> bool:
    for line in lines:
        value = line.strip()
        if not value or is_none_line(value):
            continue
        plain = value.lstrip("-*+ ").strip().lower()
        if plain in {"pending", "待补充", "待填写"}:
            continue
        return True
    return False


def dependency_tokens(lines: list[str]) -> tuple[list[str], list[str]]:
    tokens: set[str] = set()
    unparsed: list[str] = []
    for line in lines:
        value = line.strip()
        if not value or is_none_line(value):
            continue

        found: set[str] = set()
        for target in LINK_RE.findall(value):
            clean = target.split("#", 1)[0].split("?", 1)[0].strip(" <>\"")
            if clean.lower().endswith(".md"):
                found.add(Path(clean).name)
        for target in MD_PATH_RE.findall(value):
            found.add(Path(target.split("#", 1)[0]).name)

        if not found:
            plain = value.lstrip("-*+ ").strip()
            match = re.match(r"(?i)(?:ticket\s*)?#?(\d+)\b", plain)
            if match:
                found.add(match.group(1))

        if found:
            tokens.update(found)
        else:
            unparsed.append(value)
    return sorted(tokens), unparsed


def ticket_sort_key(ticket: Ticket) -> tuple[int, int | str, str]:
    if ticket.numeric_id is not None:
        return (0, int(ticket.numeric_id), ticket.relative)
    return (1, ticket.relative, ticket.relative)


def canonical_cycle(nodes: list[str]) -> tuple[str, ...]:
    core = nodes[:-1]
    rotations = [tuple(core[i:] + core[:i]) for i in range(len(core))]
    best = min(rotations)
    return best + (best[0],)


def find_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    state: dict[str, int] = {}
    stack: list[str] = []
    cycles: set[tuple[str, ...]] = set()

    def visit(node: str) -> None:
        state[node] = 1
        stack.append(node)
        for dependency in graph.get(node, []):
            if state.get(dependency, 0) == 0:
                visit(dependency)
            elif state.get(dependency) == 1:
                start = stack.index(dependency)
                cycles.add(canonical_cycle(stack[start:] + [dependency]))
        stack.pop()
        state[node] = 2

    for node in sorted(graph):
        if state.get(node, 0) == 0:
            visit(node)
    return [list(cycle) for cycle in sorted(cycles)]


def fatal(task_dir: Path, code: str, detail: str) -> int:
    payload = {
        "task_dir": str(task_dir),
        "valid": False,
        "problems": [problem(code, detail)],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 2


def inspect(task_dir: Path) -> tuple[dict[str, object], int]:
    spec = task_dir / "SPEC.md"
    hld = task_dir / "HLD.md"
    tickets_dir = task_dir / "tickets"
    if not task_dir.is_dir():
        return {}, fatal(task_dir, "missing_task_directory", "Task directory does not exist.")
    if not spec.is_file():
        return {}, fatal(task_dir, "missing_spec", "SPEC.md was not found.")
    if not tickets_dir.is_dir():
        return {}, fatal(task_dir, "missing_tickets_directory", "tickets/ was not found.")

    files = sorted(path for path in tickets_dir.glob("*.md") if path.is_file())
    if not files:
        return {}, fatal(task_dir, "no_tickets", "tickets/ contains no Markdown tickets.")

    problems: list[dict[str, str]] = []
    hld_decisions: set[str] = set()
    if hld.is_file():
        try:
            hld_sections = section_map(hld.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as exc:
            problems.append(problem("unreadable_hld", str(exc)))
        else:
            decision_ids = [
                match.group(1).upper()
                for line in hld_sections.get("design decisions", [])
                if (match := DESIGN_DECL_RE.match(line))
            ]
            duplicates = sorted(
                decision_id
                for decision_id, count in Counter(decision_ids).items()
                if count > 1
            )
            hld_decisions = set(decision_ids)
            if not hld_decisions:
                problems.append(problem("missing_hld_decisions", "HLD.md has no D IDs in Design Decisions."))
            if duplicates:
                problems.append(problem("duplicate_hld_decision", f"HLD decision IDs are duplicated: {', '.join(duplicates)}"))

    tickets: list[Ticket] = []
    for path in files:
        relative = path.relative_to(task_dir).as_posix()
        try:
            sections = section_map(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as exc:
            problems.append(problem("unreadable_ticket", str(exc), relative))
            continue

        numeric_match = NUMERIC_ID_RE.match(path.stem)
        numeric_id = numeric_match.group(1) if numeric_match else None
        for section in REQUIRED_SECTIONS:
            if section not in sections:
                problems.append(problem(f"missing_{section.replace(' ', '_')}", f"Ticket has no {section.title()} section.", relative))

        status_lines = sections.get("status", [])
        status = first_value(status_lines)
        blocked_lines = sections.get("blocked by", [])
        acceptance, duplicate_acceptance, unparsed_acceptance = acceptance_items(sections.get("acceptance criteria", []))
        execution_evidence, duplicate_evidence, unparsed_evidence = evidence_items(sections.get("execution evidence", []))
        design_lines = sections.get("high-level design", [])
        design_decisions = {
            match.upper()
            for line in design_lines
            for match in DESIGN_REF_RE.findall(line)
        }
        ticket = Ticket(
            path,
            relative,
            numeric_id,
            status,
            blocked_lines,
            acceptance,
            execution_evidence,
            has_meaningful_content(sections.get("execution blocker", [])),
            design_decisions,
        )
        ticket.dependency_tokens, unparsed = dependency_tokens(blocked_lines)
        tickets.append(ticket)

        if numeric_id is None:
            problems.append(problem("missing_numeric_id", "Filename must start with a numeric ticket ID.", relative))
        if hld.is_file() and "high-level design" not in sections:
            problems.append(problem("missing_high_level_design", "Ticket has no High-Level Design section.", relative))
        if design_decisions and not hld.is_file():
            problems.append(problem("missing_hld", "Ticket references HLD decisions but HLD.md was not found.", relative))
        unknown_decisions = design_decisions - hld_decisions
        if hld.is_file() and unknown_decisions:
            problems.append(problem("unknown_hld_decision", f"Ticket references unknown HLD decisions: {', '.join(sorted(unknown_decisions))}", relative))
        if "high-level design" in sections and not design_decisions and not any(is_none_line(line) for line in design_lines):
            problems.append(problem("unparsed_hld_reference", "High-Level Design must list D IDs or None.", relative))
        if status is None:
            problems.append(problem("missing_status", "Ticket has no usable Status section.", relative))
        elif status not in ALLOWED_STATUSES:
            problems.append(problem("invalid_status", f"Unsupported status: {status}", relative))
        if "acceptance criteria" in sections and not acceptance:
            problems.append(problem("missing_acceptance_items", "Acceptance criteria has no usable checklist items.", relative))
        if duplicate_acceptance:
            problems.append(problem("duplicate_acceptance_id", f"Acceptance IDs are duplicated: {', '.join(sorted(duplicate_acceptance))}", relative))
        for line in unparsed_acceptance:
            problems.append(problem("unparsed_acceptance_item", f"Could not parse acceptance entry: {line}", relative))
        if duplicate_evidence:
            problems.append(problem("duplicate_execution_evidence", f"Execution evidence IDs are duplicated: {', '.join(sorted(duplicate_evidence))}", relative))
        unknown_evidence = execution_evidence - acceptance.keys()
        if unknown_evidence:
            problems.append(problem("execution_evidence_for_unknown_acceptance", f"Execution evidence references unknown Acceptance IDs: {', '.join(sorted(unknown_evidence))}", relative))
        for line in unparsed_evidence:
            problems.append(problem("unparsed_execution_evidence", f"Could not parse execution evidence: {line}", relative))
        if status == "done":
            unchecked = {acceptance_id for acceptance_id, checked in acceptance.items() if not checked}
            if unchecked:
                problems.append(problem("done_with_unchecked_acceptance", "Done ticket has unchecked acceptance criteria.", relative))
            missing_evidence = acceptance.keys() - execution_evidence
            if missing_evidence:
                problems.append(problem("done_without_acceptance_evidence", f"Done ticket has no execution evidence for: {', '.join(sorted(missing_evidence))}", relative))
        if status in {"ready", "in_progress", "done"} and ticket.has_execution_blocker:
            problems.append(problem("active_execution_blocker", f"{status} ticket still has an execution blocker.", relative))
        for line in unparsed:
            problems.append(problem("unparsed_dependency", f"Could not resolve dependency entry: {line}", relative))

    tickets.sort(key=ticket_sort_key)
    by_relative = {ticket.relative: ticket for ticket in tickets}
    by_basename: dict[str, list[Ticket]] = {}
    by_numeric: dict[str, list[Ticket]] = {}
    for ticket in tickets:
        by_basename.setdefault(ticket.file.name, []).append(ticket)
        if ticket.numeric_id is not None:
            by_numeric.setdefault(ticket.numeric_id, []).append(ticket)

    for numeric_id, matches in sorted(by_numeric.items(), key=lambda item: int(item[0])):
        if len(matches) > 1:
            paths = ", ".join(ticket.relative for ticket in matches)
            problems.append(problem("duplicate_numeric_id", f"Ticket ID {numeric_id} is used by: {paths}"))

    for ticket in tickets:
        resolved: set[str] = set()
        for token in ticket.dependency_tokens:
            candidates = by_basename.get(Path(token).name, []) if token.lower().endswith(".md") else by_numeric.get(token, [])
            if not candidates:
                problems.append(problem("dangling_dependency", f"Dependency does not exist: {token}", ticket.relative))
                continue
            if len(candidates) > 1:
                problems.append(problem("ambiguous_dependency", f"Dependency is ambiguous: {token}", ticket.relative))
                continue
            target = candidates[0]
            if target.relative == ticket.relative:
                problems.append(problem("self_dependency", "Ticket depends on itself.", ticket.relative))
            else:
                resolved.add(target.relative)
        ticket.dependencies = sorted(resolved)

    for ticket in tickets:
        for dependency in ticket.dependencies:
            target = by_relative[dependency]
            if target.status == "superseded":
                problems.append(problem("dependency_on_superseded", f"Dependency points to superseded ticket: {dependency}", ticket.relative))

    graph = {
        ticket.relative: [
            dependency
            for dependency in ticket.dependencies
            if by_relative[dependency].status in ACTIVE_STATUSES
        ]
        for ticket in tickets
        if ticket.status in ACTIVE_STATUSES
    }
    for cycle in find_cycles(graph):
        problems.append(problem("dependency_cycle", " -> ".join(cycle)))

    frontier: list[str] = []
    dependency_releasable: list[str] = []
    blocked: list[dict[str, object]] = []
    for ticket in tickets:
        if ticket.status not in ACTIVE_STATUSES:
            continue
        pending = [dependency for dependency in ticket.dependencies if by_relative[dependency].status != "done"]
        if ticket.status == "ready":
            if pending:
                problems.append(problem("ready_with_unfinished_dependencies", f"Unfinished dependencies: {', '.join(pending)}", ticket.relative))
            else:
                frontier.append(ticket.relative)
        elif ticket.status in {"in_progress", "done"} and pending:
            problems.append(problem(f"{ticket.status}_with_unfinished_dependencies", f"Unfinished dependencies: {', '.join(pending)}", ticket.relative))
        elif ticket.status == "blocked":
            blocked.append(
                {
                    "ticket": ticket.relative,
                    "blocked_by": ticket.dependencies,
                    "pending": pending,
                    "execution_blocker": ticket.has_execution_blocker,
                }
            )
            if not pending:
                dependency_releasable.append(ticket.relative)

    active = [ticket.relative for ticket in tickets if ticket.status in ACTIVE_STATUSES]
    status_counts = Counter(ticket.status or "missing" for ticket in tickets)
    payload: dict[str, object] = {
        "task_dir": str(task_dir),
        "hld": "HLD.md" if hld.is_file() else None,
        "hld_decisions": sorted(hld_decisions),
        "valid": not problems,
        "status_counts": dict(sorted(status_counts.items())),
        "active": active,
        "frontier": frontier,
        "dependency_releasable": dependency_releasable,
        "in_progress": [ticket.relative for ticket in tickets if ticket.status == "in_progress"],
        "blocked": blocked,
        "done": [ticket.relative for ticket in tickets if ticket.status == "done"],
        "superseded": [ticket.relative for ticket in tickets if ticket.status == "superseded"],
        "all_active_done": bool(active) and all(by_relative[path].status == "done" for path in active),
        "problems": problems,
    }
    return payload, 0 if not problems else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a Loop SPEC.md + tickets/ execution graph.")
    parser.add_argument("task_dir", type=Path, help="Directory containing SPEC.md and tickets/")
    args = parser.parse_args()
    task_dir = args.task_dir.expanduser().resolve()
    payload, exit_code = inspect(task_dir)
    if payload:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
