"""Shared JSON contracts and runtime validation for execution graphs."""

from __future__ import annotations

import json
import re
import sys
from typing import Any

CURRENT_SCHEMA_VERSION = 1
ACTIVE_PHASES = {"open", "in_progress", "done"}
SPEC_REQUIREMENT_RE = re.compile(r"^\d+\.\s+\*\*(R\d+)\*\*\s+[—–-]")
SPEC_ACCEPTANCE_RE = re.compile(r"^-\s+\*\*(AC\d+)\*\*\s+[—–-]")
HLD_DECISION_RE = re.compile(r"^-\s+\*\*(D\d+)\*\*\s+[—–-]")
TICKET_ID_RE = re.compile(r"^T[0-9]{3,}$")
LOCAL_ACCEPTANCE_RE = re.compile(r"^AC[0-9]+$")
REQUIREMENT_ID_RE = re.compile(r"^R[0-9]+$")
DESIGN_ID_RE = re.compile(r"^D[0-9]+$")
TICKET_FIELDS = {
    "schema_version", "id", "title", "covers", "design_decisions",
    "what_to_build", "constraints", "acceptance_criteria", "dependencies",
    "lifecycle", "execution", "supersession",
}
RECEIPT_FIELDS = {
    "schema_version", "outcome", "ticket_id", "current_attempt",
    "landed_changes", "acceptance_evidence", "verification",
    "simplification", "review", "blocker", "unverified",
}

def problem(
    category: str,
    code: str,
    detail: str,
    *,
    ticket_id: str | None = None,
    path: str | None = None,
    field: str | None = None,
) -> dict[str, str]:
    item = {"category": category, "code": code, "detail": detail}
    if ticket_id is not None:
        item["ticket_id"] = ticket_id
    if path is not None:
        item["path"] = path
    if field is not None:
        item["field"] = field
    return item


def envelope(
    operation: str,
    *,
    ok: bool,
    result: object | None = None,
    graph: object | None = None,
    problems: list[dict[str, str]] | None = None,
) -> dict[str, object]:
    return {
        "ok": ok,
        "operation": operation,
        "result": {} if result is None else result,
        "graph": {} if graph is None else graph,
        "problems": [] if problems is None else problems,
    }


def emit(payload: dict[str, object]) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def validate_shape(
    value: object,
    expected: set[str],
    *,
    path: str,
    ticket_id: str | None,
    field: str,
) -> list[dict[str, str]]:
    if not isinstance(value, dict):
        return [
            problem(
                "contract",
                "invalid_field",
                f"{field} must be an object.",
                ticket_id=ticket_id,
                path=path,
                field=field,
            )
        ]
    problems: list[dict[str, str]] = []
    for name in sorted(expected - value.keys()):
        nested = f"{field}.{name}" if field else name
        problems.append(
            problem(
                "contract",
                "missing_field",
                f"Required field is missing: {nested}",
                ticket_id=ticket_id,
                path=path,
                field=nested,
            )
        )
    for name in sorted(value.keys() - expected):
        nested = f"{field}.{name}" if field else name
        problems.append(
            problem(
                "contract",
                "unknown_field",
                f"Unknown field: {nested}",
                ticket_id=ticket_id,
                path=path,
                field=nested,
            )
        )
    return problems


def non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_string_list(
    value: object,
    *,
    pattern: re.Pattern[str] | None = None,
    require_items: bool = False,
) -> bool:
    return (
        isinstance(value, list)
        and (not require_items or bool(value))
        and all(non_empty_string(item) and (pattern is None or pattern.fullmatch(item)) for item in value)
        and len(value) == len(set(value))
    )


def invalid_field(
    path: str, ticket_id: str | None, field: str, detail: str
) -> dict[str, str]:
    return problem(
        "contract",
        "invalid_field",
        detail,
        ticket_id=ticket_id,
        path=path,
        field=field,
    )


def validate_summary_items(
    value: object,
    fields: set[str],
    *,
    path: str,
    ticket_id: str | None,
    field: str,
) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return [invalid_field(path, ticket_id, field, f"{field} must be an array.")]
    problems: list[dict[str, str]] = []
    for index, item in enumerate(value):
        item_field = f"{field}[{index}]"
        shape_problems = validate_shape(
            item, fields, path=path, ticket_id=ticket_id, field=item_field
        )
        problems.extend(shape_problems)
        if shape_problems or not isinstance(item, dict):
            continue
        for name in fields:
            if name == "exit_code":
                if not isinstance(item[name], int) or isinstance(item[name], bool):
                    problems.append(invalid_field(path, ticket_id, f"{item_field}.{name}", "exit_code must be an integer."))
            elif not non_empty_string(item[name]):
                problems.append(invalid_field(path, ticket_id, f"{item_field}.{name}", f"{name} must be a non-empty string."))
    return problems


def validate_worker_receipt(receipt: object) -> list[dict[str, str]]:
    path = "<worker-receipt>"
    ticket_id = receipt.get("ticket_id") if isinstance(receipt, dict) and isinstance(receipt.get("ticket_id"), str) else None
    problems = validate_shape(receipt, RECEIPT_FIELDS, path=path, ticket_id=ticket_id, field="")
    if problems or not isinstance(receipt, dict):
        return problems
    version = receipt["schema_version"]
    if version != CURRENT_SCHEMA_VERSION:
        code = "unsupported_schema_version" if isinstance(version, int) and not isinstance(version, bool) else "invalid_field"
        problems.append(problem("contract", code, f"Worker receipt schema_version must be {CURRENT_SCHEMA_VERSION}.", ticket_id=ticket_id, path=path, field="schema_version"))
    if not isinstance(receipt["outcome"], str) or receipt["outcome"] not in {
        "completed",
        "blocked",
        "interrupted",
        "failed",
    }:
        problems.append(invalid_field(path, ticket_id, "outcome", "Unsupported worker outcome."))
    if not isinstance(receipt["ticket_id"], str) or not TICKET_ID_RE.fullmatch(receipt["ticket_id"]):
        problems.append(invalid_field(path, ticket_id, "ticket_id", "ticket_id must be an immutable ticket ID."))
    if not isinstance(receipt["current_attempt"], int) or isinstance(receipt["current_attempt"], bool) or receipt["current_attempt"] < 1:
        problems.append(invalid_field(path, ticket_id, "current_attempt", "current_attempt must be a positive integer."))
    problems.extend(validate_summary_items(receipt["landed_changes"], {"path", "summary"}, path=path, ticket_id=ticket_id, field="landed_changes"))
    problems.extend(validate_summary_items(receipt["verification"], {"command", "exit_code", "summary"}, path=path, ticket_id=ticket_id, field="verification"))

    evidence = receipt["acceptance_evidence"]
    evidence_ids: list[str] = []
    if not isinstance(evidence, list):
        problems.append(invalid_field(path, ticket_id, "acceptance_evidence", "acceptance_evidence must be an array."))
    else:
        for index, item in enumerate(evidence):
            item_field = f"acceptance_evidence[{index}]"
            shape_problems = validate_shape(item, {"acceptance_id", "result", "summary"}, path=path, ticket_id=ticket_id, field=item_field)
            problems.extend(shape_problems)
            if shape_problems or not isinstance(item, dict):
                continue
            if not isinstance(item["acceptance_id"], str) or not LOCAL_ACCEPTANCE_RE.fullmatch(item["acceptance_id"]):
                problems.append(invalid_field(path, ticket_id, f"{item_field}.acceptance_id", "acceptance_id must be a local AC ID."))
            else:
                evidence_ids.append(item["acceptance_id"])
            if (
                not isinstance(item["result"], str)
                or item["result"] not in {"passed", "not_verified"}
                or not non_empty_string(item["summary"])
            ):
                problems.append(invalid_field(path, ticket_id, item_field, "Receipt evidence requires a supported result and summary."))
        if len(evidence_ids) != len(set(evidence_ids)):
            problems.append(problem("contract", "duplicate_acceptance_evidence", "Receipt acceptance evidence IDs must be unique.", ticket_id=ticket_id, path=path))

    simplification = receipt["simplification"]
    simplification_problems = validate_shape(simplification, {"result"}, path=path, ticket_id=ticket_id, field="simplification")
    problems.extend(simplification_problems)
    if (
        not simplification_problems
        and isinstance(simplification, dict)
        and (
            not isinstance(simplification["result"], str)
            or simplification["result"] not in {"completed", "no_change", "blocked"}
        )
    ):
        problems.append(invalid_field(path, ticket_id, "simplification.result", "Unsupported simplification result."))

    review = receipt["review"]
    review_problems = validate_shape(review, {"standards", "spec", "hld"}, path=path, ticket_id=ticket_id, field="review")
    problems.extend(review_problems)
    if not review_problems and isinstance(review, dict):
        if (
            not isinstance(review["standards"], str)
            or review["standards"] not in {"pass", "failed"}
            or not isinstance(review["spec"], str)
            or review["spec"] not in {"pass", "failed"}
            or not isinstance(review["hld"], str)
            or review["hld"] not in {"pass", "failed", "not_applicable"}
        ):
            problems.append(invalid_field(path, ticket_id, "review", "Receipt review contains an unsupported result."))

    blocker = receipt["blocker"]
    if blocker is not None:
        blocker_problems = validate_shape(blocker, {"category", "reason", "release_condition"}, path=path, ticket_id=ticket_id, field="blocker")
        problems.extend(blocker_problems)
        if not blocker_problems and isinstance(blocker, dict):
            if (
                not isinstance(blocker["category"], str)
                or blocker["category"]
                not in {"requirement", "design", "dependency", "environment", "permission", "external"}
                or not non_empty_string(blocker["reason"])
                or not non_empty_string(blocker["release_condition"])
            ):
                problems.append(invalid_field(path, ticket_id, "blocker", "Receipt blocker has invalid content."))
    if not validate_string_list(receipt["unverified"]):
        problems.append(invalid_field(path, ticket_id, "unverified", "unverified must contain unique non-empty strings."))
    return problems


def validate_ticket(ticket: dict[str, Any], path: str) -> list[dict[str, str]]:
    ticket_id = ticket.get("id") if isinstance(ticket.get("id"), str) else None
    problems = validate_shape(ticket, TICKET_FIELDS, path=path, ticket_id=ticket_id, field="")
    if problems:
        return problems

    if ticket["schema_version"] != CURRENT_SCHEMA_VERSION:
        problems.append(
            problem(
                "contract",
                "unsupported_schema_version",
                f"Expected schema version {CURRENT_SCHEMA_VERSION}.",
                ticket_id=ticket_id,
                path=path,
                field="schema_version",
            )
        )
    if not isinstance(ticket["schema_version"], int) or isinstance(ticket["schema_version"], bool):
        problems.append(invalid_field(path, ticket_id, "schema_version", "schema_version must be an integer."))
    if not non_empty_string(ticket["id"]) or not TICKET_ID_RE.fullmatch(ticket["id"]):
        problems.append(invalid_field(path, ticket_id, "id", "id must match T followed by at least three digits."))
    for name in ("title", "what_to_build"):
        if not non_empty_string(ticket[name]):
            problems.append(invalid_field(path, ticket_id, name, f"{name} must be a non-empty string."))

    covers = ticket["covers"]
    problems.extend(
        validate_shape(
            covers,
            {"requirements", "spec_acceptance"},
            path=path,
            ticket_id=ticket_id,
            field="covers",
        )
    )
    if isinstance(covers, dict) and {"requirements", "spec_acceptance"} <= covers.keys():
        if not validate_string_list(covers["requirements"], pattern=REQUIREMENT_ID_RE):
            problems.append(invalid_field(path, ticket_id, "covers.requirements", "requirements must contain unique R IDs."))
        if not validate_string_list(covers["spec_acceptance"], pattern=LOCAL_ACCEPTANCE_RE):
            problems.append(invalid_field(path, ticket_id, "covers.spec_acceptance", "spec_acceptance must contain unique AC IDs."))

    if not validate_string_list(ticket["design_decisions"], pattern=DESIGN_ID_RE):
        problems.append(invalid_field(path, ticket_id, "design_decisions", "design_decisions must contain unique D IDs."))
    if not validate_string_list(ticket["constraints"], require_items=True):
        problems.append(invalid_field(path, ticket_id, "constraints", "constraints must contain non-empty unique strings."))
    if not validate_string_list(ticket["dependencies"], pattern=TICKET_ID_RE):
        problems.append(invalid_field(path, ticket_id, "dependencies", "dependencies must contain unique ticket IDs."))

    acceptance = ticket["acceptance_criteria"]
    acceptance_ids: list[str] = []
    if not isinstance(acceptance, list) or not acceptance:
        problems.append(invalid_field(path, ticket_id, "acceptance_criteria", "acceptance_criteria must be a non-empty array."))
    else:
        for index, item in enumerate(acceptance):
            item_field = f"acceptance_criteria[{index}]"
            shape_problems = validate_shape(
                item,
                {"id", "description"},
                path=path,
                ticket_id=ticket_id,
                field=item_field,
            )
            problems.extend(shape_problems)
            if shape_problems or not isinstance(item, dict):
                continue
            if not non_empty_string(item["id"]) or not LOCAL_ACCEPTANCE_RE.fullmatch(item["id"]):
                problems.append(invalid_field(path, ticket_id, f"{item_field}.id", "Acceptance ID must match AC followed by digits."))
            else:
                acceptance_ids.append(item["id"])
            if not non_empty_string(item["description"]):
                problems.append(invalid_field(path, ticket_id, f"{item_field}.description", "Acceptance description must be non-empty."))
        if len(acceptance_ids) != len(set(acceptance_ids)):
            problems.append(problem("contract", "duplicate_acceptance_id", "Ticket acceptance IDs must be unique.", ticket_id=ticket_id, path=path, field="acceptance_criteria"))

    lifecycle = ticket["lifecycle"]
    lifecycle_problems = validate_shape(
        lifecycle, {"phase"}, path=path, ticket_id=ticket_id, field="lifecycle"
    )
    problems.extend(lifecycle_problems)
    phase: str | None = None
    if not lifecycle_problems and isinstance(lifecycle, dict):
        phase = lifecycle["phase"]
        if not isinstance(phase, str) or phase not in {
            "open",
            "in_progress",
            "done",
            "superseded",
        }:
            problems.append(invalid_field(path, ticket_id, "lifecycle.phase", "Unsupported lifecycle phase."))

    execution = ticket["execution"]
    execution_fields = {"attempt_sequence", "evidence", "blocker", "current_attempt", "reopen_context"}
    execution_problems = validate_shape(
        execution, execution_fields, path=path, ticket_id=ticket_id, field="execution"
    )
    problems.extend(execution_problems)
    if not execution_problems and isinstance(execution, dict):
        sequence = execution["attempt_sequence"]
        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 0:
            problems.append(invalid_field(path, ticket_id, "execution.attempt_sequence", "attempt_sequence must be a non-negative integer."))

        evidence = execution["evidence"]
        if not isinstance(evidence, dict):
            problems.append(invalid_field(path, ticket_id, "execution.evidence", "evidence must be an object keyed by local AC ID."))
        else:
            for acceptance_id, entry in evidence.items():
                entry_field = f"execution.evidence.{acceptance_id}"
                if acceptance_id not in acceptance_ids:
                    problems.append(problem("graph", "unknown_evidence_acceptance", f"Evidence references unknown local Acceptance ID: {acceptance_id}", ticket_id=ticket_id, path=path, field=entry_field))
                shape_problems = validate_shape(entry, {"result", "summary"}, path=path, ticket_id=ticket_id, field=entry_field)
                problems.extend(shape_problems)
                if not shape_problems and isinstance(entry, dict):
                    if entry["result"] != "passed" or not non_empty_string(entry["summary"]):
                        problems.append(invalid_field(path, ticket_id, entry_field, "Stored evidence requires result passed and a non-empty summary."))

        blocker = execution["blocker"]
        if blocker is not None:
            shape_problems = validate_shape(blocker, {"category", "reason", "release_condition"}, path=path, ticket_id=ticket_id, field="execution.blocker")
            problems.extend(shape_problems)
            if not shape_problems and isinstance(blocker, dict):
                if (
                    not isinstance(blocker["category"], str)
                    or blocker["category"]
                    not in {"requirement", "design", "dependency", "environment", "permission", "external"}
                ):
                    problems.append(invalid_field(path, ticket_id, "execution.blocker.category", "Unsupported execution blocker category."))
                if not non_empty_string(blocker["reason"]) or not non_empty_string(blocker["release_condition"]):
                    problems.append(invalid_field(path, ticket_id, "execution.blocker", "Blocker reason and release_condition must be non-empty."))

        current_attempt = execution["current_attempt"]
        if current_attempt is not None and not isinstance(current_attempt, dict):
            problems.append(invalid_field(path, ticket_id, "execution.current_attempt", "current_attempt must be an object or null."))
        elif isinstance(current_attempt, dict):
            attempt_field = "execution.current_attempt"
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
                if not isinstance(number, int) or isinstance(number, bool) or number < 1 or number != sequence:
                    problems.append(invalid_field(path, ticket_id, f"{attempt_field}.number", "Attempt number must be positive and equal attempt_sequence."))
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
        reopen = execution["reopen_context"]
        if reopen is not None and (
            not isinstance(phase, str) or phase not in {"open", "in_progress"}
        ):
            problems.append(problem("graph", "unexpected_reopen_context", "reopen_context is only valid before a reopened ticket completes.", ticket_id=ticket_id, path=path))
        if reopen is not None:
            reopen_problems = validate_shape(reopen, {"review_finding", "invalidated_acceptance"}, path=path, ticket_id=ticket_id, field="execution.reopen_context")
            problems.extend(reopen_problems)
            if not reopen_problems and isinstance(reopen, dict):
                if not non_empty_string(reopen["review_finding"]) or not validate_string_list(reopen["invalidated_acceptance"], pattern=LOCAL_ACCEPTANCE_RE, require_items=True):
                    problems.append(invalid_field(path, ticket_id, "execution.reopen_context", "Reopen context requires a finding and unique invalidated local AC IDs."))
                elif not set(reopen["invalidated_acceptance"]) <= set(acceptance_ids):
                    problems.append(problem("graph", "unknown_reopen_acceptance", "Reopen context references an unknown local Acceptance ID.", ticket_id=ticket_id, path=path))

    supersession = ticket["supersession"]
    if phase == "superseded" and supersession is None:
        problems.append(problem("graph", "missing_supersession", "A superseded ticket requires lineage.", ticket_id=ticket_id, path=path))
    if phase != "superseded" and supersession is not None:
        problems.append(problem("graph", "unexpected_supersession", "Only a superseded ticket may carry supersession lineage.", ticket_id=ticket_id, path=path))
    if supersession is not None:
        supersession_problems = validate_shape(supersession, {"reason", "replacement_ticket_id"}, path=path, ticket_id=ticket_id, field="supersession")
        problems.extend(supersession_problems)
        if not supersession_problems and isinstance(supersession, dict):
            replacement = supersession["replacement_ticket_id"]
            if not non_empty_string(supersession["reason"]) or (replacement is not None and (not isinstance(replacement, str) or not TICKET_ID_RE.fullmatch(replacement))):
                problems.append(invalid_field(path, ticket_id, "supersession", "Supersession requires a reason and nullable replacement ticket ID."))

    return problems
