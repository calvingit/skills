"""Task-local runtime state: current execution progress of a ticket graph.

Tickets are contracts. Lifecycle, attempts, evidence, blockers and authority are
ephemeral progress and live here, under the task's Git-ignored ``.loop/``. The
state file keeps current judgement and the index needed to locate evidence; full
reports stay as ordinary files next to it.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

from .contracts import (
    ENTRY_FIELDS,
    ENTRY_REQUIRED_FIELDS,
    EVIDENCE_FIELDS,
    EVIDENCE_REQUIRED_FIELDS,
    LOCAL_ACCEPTANCE_RE,
    RUNTIME_SCHEMA_VERSION,
    invalid_field,
    non_empty_string,
    problem,
    validate_contract,
    validate_shape,
    validate_string_list,
)

STATE_DIRECTORY = ".loop"
STATE_FILE = ".loop/state.json"
IGNORE_CONTENT = "# Local execution progress and reports; never tracked.\n*\n"
PHASES = ("open", "in_progress", "done", "superseded")
FINGERPRINT_RE = re.compile(r"[0-9a-f]{64}")


def state_path(task_dir: Path) -> Path:
    return task_dir / STATE_FILE


def fresh_entry() -> dict[str, Any]:
    """A ticket that has never been claimed: open, no attempt, no evidence."""
    return {"phase": "open", "attempt": 0}


def validate_entry(
    entry: object,
    contract: dict[str, Any],
    path: str,
    ticket_id: str | None,
) -> list[dict[str, str]]:
    """Validate one runtime entry against the contract it belongs to."""
    problems = validate_shape(
        entry,
        ENTRY_FIELDS,
        path=path,
        ticket_id=ticket_id,
        field="runtime",
        required=ENTRY_REQUIRED_FIELDS,
    )
    if problems or not isinstance(entry, dict):
        return problems

    acceptance_ids = [
        item["id"]
        for item in contract.get("delivery_acceptance", [])
        if isinstance(item, dict) and non_empty_string(item.get("id", ""))
    ] if isinstance(contract.get("delivery_acceptance"), list) else []

    phase = entry.get("phase")
    if not isinstance(phase, str) or phase not in PHASES:
        problems.append(invalid_field(path, ticket_id, "runtime.phase", "Unsupported lifecycle phase."))
    attempt = entry.get("attempt", 0)
    if not isinstance(attempt, int) or isinstance(attempt, bool) or attempt < 0:
        problems.append(invalid_field(path, ticket_id, "runtime.attempt", "attempt must be a non-negative integer."))

    if "review" in entry and not non_empty_string(entry["review"]):
        problems.append(invalid_field(path, ticket_id, "runtime.review", "Review must be a non-empty string."))

    authority = entry.get("authority")
    if authority is not None:
        errors = validate_shape(authority, {"fingerprint", "reason"}, path=path, ticket_id=ticket_id, field="runtime.authority")
        problems.extend(errors)
        if not errors and isinstance(authority, dict) and (
            not isinstance(authority["fingerprint"], str)
            or not FINGERPRINT_RE.fullmatch(authority["fingerprint"])
            or not non_empty_string(authority["reason"])
        ):
            problems.append(invalid_field(path, ticket_id, "runtime.authority", "Authority requires a SHA-256 fingerprint and a reconciliation reason."))

    evidence = entry.get("evidence", {})
    if not isinstance(evidence, dict):
        problems.append(invalid_field(path, ticket_id, "runtime.evidence", "evidence must be an object keyed by local AC ID."))
    else:
        for acceptance_id, item in evidence.items():
            entry_field = f"runtime.evidence.{acceptance_id}"
            if acceptance_id not in acceptance_ids:
                problems.append(problem("graph", "unknown_evidence_acceptance", f"Evidence references unknown local Acceptance ID: {acceptance_id}", ticket_id=ticket_id, path=path, field=entry_field))
            shape_problems = validate_shape(
                item, EVIDENCE_FIELDS, path=path, ticket_id=ticket_id, field=entry_field,
                required=EVIDENCE_REQUIRED_FIELDS,
            )
            problems.extend(shape_problems)
            if not shape_problems and isinstance(item, dict):
                number = item["attempt"]
                if not isinstance(number, int) or isinstance(number, bool) or number < 1 or (isinstance(attempt, int) and number > attempt):
                    problems.append(invalid_field(path, ticket_id, f"{entry_field}.attempt", "Evidence must record the attempt that established it."))
                if not non_empty_string(item["summary"]):
                    problems.append(invalid_field(path, ticket_id, entry_field, "Stored evidence requires a non-empty summary of what was observed."))

    blocker = entry.get("blocker")
    if blocker is not None:
        shape_problems = validate_shape(blocker, {"category", "reason", "release_condition"}, path=path, ticket_id=ticket_id, field="runtime.blocker")
        problems.extend(shape_problems)
        if not shape_problems and isinstance(blocker, dict):
            if (
                not isinstance(blocker["category"], str)
                or blocker["category"]
                not in {"requirement", "design", "dependency", "environment", "permission", "external"}
            ):
                problems.append(invalid_field(path, ticket_id, "runtime.blocker.category", "Unsupported execution blocker category."))
            if not non_empty_string(blocker["reason"]) or not non_empty_string(blocker["release_condition"]):
                problems.append(invalid_field(path, ticket_id, "runtime.blocker", "Blocker reason and release_condition must be non-empty."))

    current_attempt = entry.get("current_attempt")
    if current_attempt is not None and not isinstance(current_attempt, dict):
        problems.append(invalid_field(path, ticket_id, "runtime.current_attempt", "current_attempt must be an object."))
    elif isinstance(current_attempt, dict):
        attempt_field = "runtime.current_attempt"
        attempt_problems = validate_shape(
            current_attempt,
            {"number", "baseline", "existing_changes", "allowed_write_scope"},
            path=path,
            ticket_id=ticket_id,
            field=attempt_field,
        )
        problems.extend(attempt_problems)
        if not attempt_problems:
            number = current_attempt["number"]
            if not isinstance(number, int) or isinstance(number, bool) or number < 1 or number != attempt:
                problems.append(invalid_field(path, ticket_id, f"{attempt_field}.number", "Attempt number must be positive and equal runtime.attempt."))
            baseline = current_attempt["baseline"]
            baseline_problems = validate_shape(baseline, {"reference", "staged", "unstaged", "untracked"}, path=path, ticket_id=ticket_id, field=f"{attempt_field}.baseline")
            problems.extend(baseline_problems)
            if not baseline_problems and isinstance(baseline, dict):
                if not non_empty_string(baseline["reference"]):
                    problems.append(invalid_field(path, ticket_id, f"{attempt_field}.baseline.reference", "Baseline reference must be non-empty."))
                for name in ("staged", "unstaged", "untracked"):
                    if not validate_string_list(baseline[name]):
                        problems.append(invalid_field(path, ticket_id, f"{attempt_field}.baseline.{name}", "Baseline paths must be unique non-empty strings."))
            existing = current_attempt["existing_changes"]
            existing_problems = validate_shape(existing, {"included", "excluded"}, path=path, ticket_id=ticket_id, field=f"{attempt_field}.existing_changes")
            problems.extend(existing_problems)
            if not existing_problems and isinstance(existing, dict):
                for name in ("included", "excluded"):
                    if not validate_string_list(existing[name]):
                        problems.append(invalid_field(path, ticket_id, f"{attempt_field}.existing_changes.{name}", "Existing-change paths must be unique non-empty strings."))
            if not validate_string_list(current_attempt["allowed_write_scope"]):
                problems.append(invalid_field(path, ticket_id, f"{attempt_field}.allowed_write_scope", "allowed_write_scope must contain unique non-empty strings."))

    reopen = entry.get("reopen_context")
    if reopen is not None:
        reopen_problems = validate_shape(reopen, {"review_finding", "invalidated_acceptance"}, path=path, ticket_id=ticket_id, field="runtime.reopen_context")
        problems.extend(reopen_problems)
        if not reopen_problems and isinstance(reopen, dict):
            if not non_empty_string(reopen["review_finding"]) or not validate_string_list(reopen["invalidated_acceptance"], pattern=LOCAL_ACCEPTANCE_RE, require_items=True):
                problems.append(invalid_field(path, ticket_id, "runtime.reopen_context", "Reopen context requires a finding and unique invalidated local AC IDs."))
            elif not set(reopen["invalidated_acceptance"]) <= set(acceptance_ids):
                problems.append(problem("graph", "unknown_reopen_acceptance", "Reopen context references an unknown local Acceptance ID.", ticket_id=ticket_id, path=path))

    if phase == "in_progress" and current_attempt is None:
        problems.append(problem("graph", "missing_current_attempt", "An in_progress ticket requires current_attempt.", ticket_id=ticket_id, path=path))
    if phase != "in_progress" and current_attempt is not None:
        problems.append(problem("graph", "unexpected_current_attempt", "Only an in_progress ticket may keep current_attempt.", ticket_id=ticket_id, path=path))
    if isinstance(phase, str) and phase in {"in_progress", "done"} and blocker is not None:
        problems.append(problem("graph", "active_execution_blocker", f"A {phase} ticket cannot keep an execution blocker.", ticket_id=ticket_id, path=path))
    if phase == "superseded" and blocker is not None:
        problems.append(problem("graph", "superseded_execution_state", "A superseded ticket cannot keep an execution blocker.", ticket_id=ticket_id, path=path))
    if phase == "done" and isinstance(evidence, dict):
        missing = sorted(set(acceptance_ids) - evidence.keys())
        if missing:
            problems.append(problem("graph", "done_without_acceptance_evidence", f"Done ticket has no evidence for: {', '.join(missing)}", ticket_id=ticket_id, path=path))
    if reopen is not None and phase not in {"open", "in_progress"}:
        problems.append(problem("graph", "unexpected_reopen_context", "reopen_context is only valid before a reopened ticket completes.", ticket_id=ticket_id, path=path))
    supersession = contract.get("supersession")
    if phase == "superseded" and supersession is None:
        problems.append(problem("graph", "missing_supersession", "A superseded ticket requires lineage.", ticket_id=ticket_id, path=path))
    if phase != "superseded" and supersession is not None:
        problems.append(problem("graph", "unexpected_supersession", "Only a superseded ticket may carry supersession lineage.", ticket_id=ticket_id, path=path))
    return problems


def load_state(task_dir: Path) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
    """Read .loop/state.json. A missing file is reported against the tickets."""
    path = state_path(task_dir)
    if not path.is_file():
        return None, []
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return None, [problem("storage", "invalid_runtime_state", str(exc), path=STATE_FILE)]
    problems = validate_shape(
        state,
        {"schema_version", "tickets"},
        path=STATE_FILE,
        ticket_id=None,
        field="",
    )
    if problems or not isinstance(state, dict):
        return None, problems
    if state["schema_version"] != RUNTIME_SCHEMA_VERSION:
        return None, [
            problem(
                "storage",
                "unsupported_runtime_state_version",
                f"Expected runtime state version {RUNTIME_SCHEMA_VERSION}.",
                path=STATE_FILE,
                field="schema_version",
            )
        ]
    if not isinstance(state["tickets"], dict):
        return None, [invalid_field(STATE_FILE, None, "tickets", "tickets must be an object keyed by ticket ID.")]
    return state, []


def attach_runtime(
    tickets: list[dict[str, Any]], state: dict[str, Any] | None
) -> list[dict[str, str]]:
    """Give every ticket its current runtime entry, or fail with a clear gap."""
    if state is None:
        return [
            problem(
                "storage",
                "missing_runtime_state",
                "Tickets exist but .loop/state.json is missing, so recorded progress cannot be assumed. "
                "Re-initialize explicitly only after confirming that progress is lost.",
                path=STATE_FILE,
            )
        ]
    entries = state["tickets"]
    problems: list[dict[str, str]] = []
    for ticket in tickets:
        entry = entries.get(ticket["id"])
        if entry is None:
            problems.append(
                problem(
                    "storage",
                    "missing_runtime_state",
                    f"No runtime state entry for ticket {ticket['id']}; progress cannot be assumed.",
                    ticket_id=ticket["id"],
                    path=STATE_FILE,
                )
            )
            continue
        ticket["runtime"] = entry
        problems.extend(validate_entry(entry, ticket, STATE_FILE, ticket["id"]))
    for ticket_id in sorted(set(entries) - {ticket["id"] for ticket in tickets}):
        problems.append(
            problem(
                "storage",
                "unknown_state_ticket",
                f"Runtime state references a ticket that does not exist: {ticket_id}",
                ticket_id=ticket_id,
                path=STATE_FILE,
            )
        )
    return problems


def state_from(tickets: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": RUNTIME_SCHEMA_VERSION,
        "tickets": {ticket["id"]: ticket["runtime"] for ticket in tickets},
    }


def ensure_loop(task_dir: Path) -> None:
    """Create .loop/ with its own ignore rule; the project's rules may not cover it."""
    directory = task_dir / STATE_DIRECTORY
    directory.mkdir(parents=True, exist_ok=True)
    ignore = directory / ".gitignore"
    if not ignore.is_file():
        ignore.write_text(IGNORE_CONTENT, encoding="utf-8")


def _atomic_write(path: Path, text: str) -> list[dict[str, str]]:
    temporary_name: str | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary_name = temporary.name
            temporary.write(text)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_name, path)
    except OSError as exc:
        if temporary_name is not None:
            try:
                Path(temporary_name).unlink()
            except FileNotFoundError:
                pass
        return [problem("storage", "write_failed", str(exc), path=str(path.name))]
    return []


def render_state(state: dict[str, Any]) -> str:
    """Canonical bytes of the state file, so identical progress has one form."""
    return json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def write_state(task_dir: Path, state: dict[str, Any]) -> list[dict[str, str]]:
    """Replace the whole state file atomically, one ticket graph at a time."""
    ensure_loop(task_dir)
    return _atomic_write(state_path(task_dir), render_state(state))


def update_entry(task_dir: Path, ticket_id: str, entry: dict[str, Any]) -> list[dict[str, str]]:
    """Replace one ticket's runtime entry. Callers hold the task write lock."""
    state, problems = load_state(task_dir)
    if problems or state is None:
        return problems or [
            problem("storage", "missing_runtime_state", "No runtime state to update.", ticket_id=ticket_id, path=STATE_FILE)
        ]
    state["tickets"][ticket_id] = entry
    return write_state(task_dir, state)


def validate_ticket(ticket: dict[str, Any], path: str) -> list[dict[str, str]]:
    """Validate a contract together with its current runtime entry."""
    problems = validate_contract(ticket, path)
    entry = ticket.get("runtime")
    problems.extend(
        validate_entry(entry, ticket, path, ticket.get("id") if isinstance(ticket.get("id"), str) else None)
    )
    return problems
