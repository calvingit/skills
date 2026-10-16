"""Shared JSON contracts and runtime validation for execution graphs."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ACTIVE_PHASES = {"open", "in_progress", "done"}
SPEC_REQUIREMENT_RE = re.compile(r"^\d+\.\s+\*\*(R\d+)\*\*\s+[—–-]")
SPEC_ACCEPTANCE_RE = re.compile(r"^-\s+\*\*(AC\d+)\*\*\s+[—–-]")
# Accept the current template and the legacy form produced before the template
# was made explicit: ``- **D1** — ...`` and ``- **D1:** ...``.
SOLUTION_DECISION_RE = re.compile(r"^-\s+\*\*(D\d+)(?::\*\*|\*\*\s+[—–-])")
TICKET_ID_RE = re.compile(r"^T[0-9]{3,}$")
LOCAL_ACCEPTANCE_RE = re.compile(r"^AC[0-9]+$")
REQUIREMENT_ID_RE = re.compile(r"^R[0-9]+$")
DESIGN_ID_RE = re.compile(r"^D[0-9]+$")
# The shared schemas own field names and the storage versions.
SCHEMA = json.loads((Path(__file__).resolve().parents[1] / "ticket-schema.json").read_text())
RUNTIME_SCHEMA = json.loads((Path(__file__).resolve().parents[1] / "runtime-state-schema.json").read_text())
CURRENT_SCHEMA_VERSION = SCHEMA["properties"]["schema_version"]["const"]
RUNTIME_SCHEMA_VERSION = RUNTIME_SCHEMA["properties"]["schema_version"]["const"]
# The internal ticket object carries its contract plus the current runtime entry.
TICKET_FIELDS = set(SCHEMA["properties"]) | {"runtime"}
REQUIRED_FIELDS = set(SCHEMA["required"])
ENTRY_FIELDS = set(RUNTIME_SCHEMA["$defs"]["ticket_state"]["properties"])
ENTRY_REQUIRED_FIELDS = set(RUNTIME_SCHEMA["$defs"]["ticket_state"]["required"])
EVIDENCE_FIELDS = set(RUNTIME_SCHEMA["$defs"]["evidence"]["properties"])
EVIDENCE_REQUIRED_FIELDS = set(RUNTIME_SCHEMA["$defs"]["evidence"]["required"])


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
    required: set[str] | None = None,
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
    for name in sorted((expected if required is None else required) - value.keys()):
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
            elif name == "argv":
                if not isinstance(item[name], list) or not item[name] or any(not non_empty_string(value) for value in item[name]):
                    problems.append(invalid_field(path, ticket_id, f"{item_field}.{name}", "argv must be a non-empty string array."))
            elif not non_empty_string(item[name]):
                problems.append(invalid_field(path, ticket_id, f"{item_field}.{name}", f"{name} must be a non-empty string."))
    return problems


def validate_contract(ticket: dict[str, Any], path: str) -> list[dict[str, str]]:
    """Validate the stable delivery contract: frontmatter references and body."""
    ticket_id = ticket.get("id") if isinstance(ticket.get("id"), str) else None
    # A ticket from another storage version is never read as a v4 contract, and
    # one clear message is more useful than every field it does not share.
    if ticket.get("schema_version") != CURRENT_SCHEMA_VERSION:
        return [
            problem(
                "contract",
                "unsupported_schema_version",
                f"Expected schema version {CURRENT_SCHEMA_VERSION}; convert older graphs with create-graph migrate-v3.",
                ticket_id=ticket_id,
                path=path,
                field="schema_version",
            )
        ]
    problems = validate_shape(
        ticket, TICKET_FIELDS, path=path, ticket_id=ticket_id, field="", required=REQUIRED_FIELDS
    )
    if problems:
        return problems

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

    if not validate_string_list(ticket["referenced_design_decisions"], pattern=DESIGN_ID_RE):
        problems.append(invalid_field(path, ticket_id, "referenced_design_decisions", "referenced_design_decisions must contain unique D IDs."))
    if not validate_string_list(ticket["constraints"]):
        problems.append(invalid_field(path, ticket_id, "constraints", "constraints must be an array of non-empty unique strings."))
    if not validate_string_list(ticket["dependencies"], pattern=TICKET_ID_RE):
        problems.append(invalid_field(path, ticket_id, "dependencies", "dependencies must contain unique ticket IDs."))
    acceptance = ticket["delivery_acceptance"]
    acceptance_ids: list[str] = []
    if not isinstance(acceptance, list) or not acceptance:
        problems.append(invalid_field(path, ticket_id, "delivery_acceptance", "delivery_acceptance must be a non-empty array."))
    else:
        for index, item in enumerate(acceptance):
            item_field = f"delivery_acceptance[{index}]"
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
            problems.append(problem("contract", "duplicate_acceptance_id", "Ticket acceptance IDs must be unique.", ticket_id=ticket_id, path=path, field="delivery_acceptance"))

    # Supersession is a plan-revision fact of the contract, not execution state.
    supersession = ticket.get("supersession")
    if supersession is not None:
        supersession_problems = validate_shape(supersession, {"reason", "replacement_ticket_id"}, path=path, ticket_id=ticket_id, field="supersession")
        problems.extend(supersession_problems)
        if not supersession_problems and isinstance(supersession, dict):
            replacement = supersession["replacement_ticket_id"]
            if not non_empty_string(supersession["reason"]) or (replacement is not None and (not isinstance(replacement, str) or not TICKET_ID_RE.fullmatch(replacement))):
                problems.append(invalid_field(path, ticket_id, "supersession", "Supersession requires a reason and nullable replacement ticket ID."))

    return problems
