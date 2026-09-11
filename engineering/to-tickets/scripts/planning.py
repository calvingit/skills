"""Batch graph creation, reconciliation, and recovery commands."""

from __future__ import annotations

import copy
import json
import re
import shutil
from pathlib import Path
from typing import Any

from ticket_graph.authority import authority_index, authority_fingerprint, bind_authority
from ticket_graph.contracts import CURRENT_SCHEMA_VERSION, TICKET_ID_RE, envelope, invalid_field, non_empty_string, problem, validate_shape, validate_string_list, validate_ticket
from ticket_graph.graph import public_ticket, validate_graph
from ticket_graph.store import acquire_write_lock, atomic_copy, commit_graph_transaction, release_lock, validated_snapshot


def slugify(title: object) -> str:
    if not isinstance(title, str):
        return "ticket"
    return re.sub(r"[^\w]+", "-", title.strip().lower(), flags=re.UNICODE).strip("-") or "ticket"


def create_batch(task_dir: Path, request: dict[str, Any]) -> tuple[dict[str, object], int]:
    descriptor, _, lock_problems = acquire_write_lock(task_dir)
    if lock_problems:
        return envelope("create-batch", ok=False, problems=lock_problems), 1
    try:
        if (task_dir / ".ticket-graph-transaction").exists():
            return envelope("create-batch", ok=False, problems=[problem("recovery", "recovery_required", "An unfinished graph transaction requires recovery.")]), 1
        if not task_dir.is_dir() or not (task_dir / "SPEC.md").is_file():
            return envelope("create-batch", ok=False, problems=[problem("authority", "missing_spec", "A task directory with SPEC.md is required.")]), 1
        tickets_dir = task_dir / "tickets"
        tickets_dir.mkdir(exist_ok=True)
        if any(tickets_dir.iterdir()):
            return envelope("create-batch", ok=False, problems=[problem("graph", "graph_already_exists", "create-batch requires an empty tickets directory.")]), 1
        request_problems = validate_shape(request, {"tickets"}, path="<request>", ticket_id=None, field="")
        candidates = request.get("tickets")
        if request_problems or not isinstance(candidates, list) or not candidates:
            if not request_problems:
                request_problems.append(invalid_field("<request>", None, "tickets", "tickets must be a non-empty array."))
            return envelope("create-batch", ok=False, problems=request_problems), 1
        candidate_fields = {"key", "title", "covers", "referenced_design_decisions", "what_to_build", "constraints", "delivery_acceptance", "dependencies"}
        keys: list[str] = []
        for index, candidate in enumerate(candidates):
            issues = validate_shape(candidate, candidate_fields, path="<request>", ticket_id=None, field=f"tickets[{index}]")
            request_problems.extend(issues)
            if not issues and isinstance(candidate, dict):
                key = candidate["key"]
                if not non_empty_string(key) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", key):
                    request_problems.append(invalid_field("<request>", None, f"tickets[{index}].key", "Candidate key is invalid."))
                else:
                    keys.append(key)
        if len(keys) != len(set(keys)):
            request_problems.append(problem("contract", "duplicate_candidate_key", "Candidate keys must be unique."))
        if request_problems:
            return envelope("create-batch", ok=False, problems=request_problems), 1
        ids = {key: f"T{index:03d}" for index, key in enumerate(keys, start=1)}
        tickets: list[dict[str, Any]] = []
        created: list[dict[str, str]] = []
        for candidate in candidates:
            dependencies = candidate["dependencies"]
            if not validate_string_list(dependencies) or any(value not in ids for value in dependencies):
                request_problems.append(problem("graph", "unknown_candidate_dependency", f"Candidate {candidate['key']} has an unknown dependency."))
                continue
            ticket_id = ids[candidate["key"]]
            relative = f"tickets/{ticket_id}-{slugify(candidate['title'])}.json"
            ticket = {
                "schema_version": CURRENT_SCHEMA_VERSION,
                "id": ticket_id,
                "title": candidate["title"],
                "covers": candidate["covers"],
                "referenced_design_decisions": candidate["referenced_design_decisions"],
                "what_to_build": candidate["what_to_build"],
                "constraints": candidate["constraints"],
                "delivery_acceptance": candidate["delivery_acceptance"],
                "dependencies": [ids[value] for value in dependencies],
                "lifecycle": {"phase": "open"},
                "execution": {"attempt_sequence": 0, "evidence": {}, "blocker": None, "current_attempt": None, "reopen_context": None},
                "supersession": None,
                "_path": relative,
            }
            bind_authority(task_dir, ticket, "Confirmed initial delivery split.")
            request_problems.extend(validate_ticket(public_ticket(ticket), relative))
            tickets.append(ticket)
            created.append({"key": candidate["key"], "id": ticket_id, "path": relative})
        if request_problems:
            return envelope("create-batch", ok=False, problems=request_problems), 1
        authority, authority_problems = authority_index(task_dir)
        graph_problems, _ = validate_graph(tickets, authority, has_hld=(task_dir / "HLD.md").is_file())
        problems = authority_problems + graph_problems
        if problems:
            return envelope("create-batch", ok=False, problems=problems), 1
        transaction_problems = commit_graph_transaction(task_dir, tickets, "create-batch")
        if transaction_problems:
            return envelope("create-batch", ok=False, problems=transaction_problems), 1
        _, graph, committed_problems = validated_snapshot(task_dir)
        return envelope("create-batch", ok=not committed_problems, result={"created": created}, graph=graph, problems=committed_problems), (0 if not committed_problems else 1)
    finally:
        release_lock(descriptor)


def reconcile_batch(
    task_dir: Path, request: dict[str, Any]
) -> tuple[dict[str, object], int]:
    descriptor, _, lock_problems = acquire_write_lock(task_dir)
    if lock_problems:
        return envelope("reconcile-batch", ok=False, problems=lock_problems), 1
    try:
        tickets, graph, current_problems = validated_snapshot(task_dir)
        if not tickets:
            return envelope("reconcile-batch", ok=False, graph=graph, problems=current_problems), 1
        request_problems = validate_shape(
            request,
            {"reason", "operations"},
            path="<request>",
            ticket_id=None,
            field="",
        )
        operations = request.get("operations")
        if not non_empty_string(request.get("reason")):
            request_problems.append(invalid_field("<request>", None, "reason", "Reconciliation reason must be non-empty."))
        if not isinstance(operations, list) or not operations:
            request_problems.append(invalid_field("<request>", None, "operations", "operations must be a non-empty array."))
        if request_problems:
            return envelope("reconcile-batch", ok=False, graph=graph, problems=request_problems), 1

        source_fingerprint = authority_fingerprint(task_dir)
        if any(ticket["lifecycle"]["phase"] == "in_progress" for ticket in tickets):
            # Reconciliation is one shared-task transaction. Callers stop workers
            # and block active attempts before changing any task authority.
            return envelope("reconcile-batch", ok=False, graph=graph, problems=[problem("transition", "active_attempts", "Stop workers and block active attempts before reconciliation.")]), 1
        next_id = max((int(ticket["id"][1:]) for ticket in tickets), default=0) + 1
        create_operations = [
            operation
            for operation in operations
            if isinstance(operation, dict) and operation.get("operation") == "create"
        ]
        create_keys = [operation.get("key") for operation in create_operations]
        invalid_create_keys = any(not non_empty_string(key) for key in create_keys)
        if invalid_create_keys or len(create_keys) != len(set(create_keys)):
            request_problems.append(problem("contract", "invalid_candidate_key", "Reconciliation create keys must be unique non-empty strings."))
            return envelope("reconcile-batch", ok=False, graph=graph, problems=request_problems), 1
        ids_by_key = {
            key: f"T{next_id + index:03d}" for index, key in enumerate(create_keys)
        }
        by_id = {ticket["id"]: copy.deepcopy(ticket) for ticket in tickets}
        created: list[dict[str, str]] = []
        updated: set[str] = set()
        superseded: set[str] = set()
        retained: set[str] = set()

        def resolve(reference: object) -> str | None:
            if not isinstance(reference, str):
                return None
            if reference in ids_by_key:
                return ids_by_key[reference]
            return reference if TICKET_ID_RE.fullmatch(reference) else None

        contract_fields = {
            "title",
            "covers",
            "referenced_design_decisions",
            "what_to_build",
            "constraints",
            "delivery_acceptance",
        }
        new_contract_fields = contract_fields | {"dependencies"}
        for index, operation in enumerate(operations):
            operation_field = f"operations[{index}]"
            if not isinstance(operation, dict) or not non_empty_string(operation.get("operation")):
                request_problems.append(invalid_field("<request>", None, operation_field, "Each operation must be an object with an operation name."))
                continue
            name = operation["operation"]
            if name == "create":
                shape_problems = validate_shape(operation, {"operation", "key", "ticket"}, path="<request>", ticket_id=None, field=operation_field)
                request_problems.extend(shape_problems)
                contract = operation.get("ticket")
                contract_problems = validate_shape(contract, new_contract_fields, path="<request>", ticket_id=None, field=f"{operation_field}.ticket")
                request_problems.extend(contract_problems)
                if shape_problems or contract_problems or not isinstance(contract, dict):
                    continue
                dependencies = contract["dependencies"]
                if not validate_string_list(dependencies):
                    request_problems.append(invalid_field("<request>", None, f"{operation_field}.ticket.dependencies", "dependencies must contain unique references."))
                    continue
                resolved_dependencies = [resolve(value) for value in dependencies]
                if any(value is None or (value not in by_id and value not in ids_by_key.values()) for value in resolved_dependencies):
                    request_problems.append(problem("graph", "unknown_reconciliation_dependency", f"Create operation {operation['key']} has an unknown dependency."))
                    continue
                ticket_id = ids_by_key[operation["key"]]
                relative = f"tickets/{ticket_id}-{slugify(contract['title'])}.json"
                ticket = {
                    "schema_version": CURRENT_SCHEMA_VERSION,
                    "id": ticket_id,
                    "title": contract["title"],
                    "covers": contract["covers"],
                    "referenced_design_decisions": contract["referenced_design_decisions"],
                    "what_to_build": contract["what_to_build"],
                    "constraints": contract["constraints"],
                    "delivery_acceptance": contract["delivery_acceptance"],
                    "dependencies": resolved_dependencies,
                    "lifecycle": {"phase": "open"},
                    "execution": {"attempt_sequence": 0, "evidence": {}, "blocker": None, "current_attempt": None, "reopen_context": None},
                    "supersession": None,
                    "_path": relative,
                }
                by_id[ticket_id] = ticket
                created.append({"key": operation["key"], "id": ticket_id, "path": relative})
            elif name == "update_contract":
                shape_problems = validate_shape(operation, {"operation", "ticket_id", "changes"}, path="<request>", ticket_id=None, field=operation_field)
                request_problems.extend(shape_problems)
                ticket_id = operation.get("ticket_id")
                changes = operation.get("changes")
                ticket = by_id.get(ticket_id) if isinstance(ticket_id, str) else None
                if shape_problems or ticket is None or not isinstance(changes, dict) or not changes or not set(changes) <= contract_fields:
                    request_problems.append(problem("transition", "invalid_contract_update", "Contract update requires an existing ticket and supported non-empty changes.", ticket_id=ticket_id if isinstance(ticket_id, str) else None))
                    continue
                if ticket["lifecycle"]["phase"] != "open" or ticket["execution"]["current_attempt"] is not None or ticket["execution"]["evidence"]:
                    request_problems.append(problem("transition", "invalid_contract_update", "Only an unstarted open ticket without evidence may be updated in place.", ticket_id=ticket_id))
                    continue
                for field, value in changes.items():
                    ticket[field] = value
                updated.add(ticket_id)
            elif name == "supersede":
                allowed = {"operation", "ticket_id", "replacement", "reason", "worker_stopped"}
                required = {"operation", "ticket_id", "replacement", "reason"}
                missing = required - operation.keys()
                unknown = operation.keys() - allowed
                for field in sorted(missing):
                    request_problems.append(problem("contract", "missing_field", f"Required field is missing: {operation_field}.{field}"))
                for field in sorted(unknown):
                    request_problems.append(problem("contract", "unknown_field", f"Unknown field: {operation_field}.{field}"))
                ticket_id = operation.get("ticket_id")
                ticket = by_id.get(ticket_id) if isinstance(ticket_id, str) else None
                replacement = resolve(operation.get("replacement")) if operation.get("replacement") is not None else None
                if ticket is None or ticket["lifecycle"]["phase"] == "superseded" or not non_empty_string(operation.get("reason")):
                    request_problems.append(problem("transition", "invalid_supersession", "Supersession requires an existing active ticket and reason.", ticket_id=ticket_id if isinstance(ticket_id, str) else None))
                    continue
                if operation.get("replacement") is not None and replacement is None:
                    request_problems.append(problem("graph", "invalid_supersession_replacement", "Replacement reference is invalid.", ticket_id=ticket_id))
                    continue
                if ticket["lifecycle"]["phase"] == "in_progress" and operation.get("worker_stopped") is not True:
                    request_problems.append(problem("transition", "active_worker_not_stopped", "An in_progress ticket requires confirmed worker stop before supersession.", ticket_id=ticket_id))
                    continue
                ticket["lifecycle"]["phase"] = "superseded"
                ticket["execution"]["current_attempt"] = None
                ticket["execution"]["blocker"] = None
                ticket["supersession"] = {"reason": operation["reason"], "replacement_ticket_id": replacement}
                superseded.add(ticket_id)
            elif name == "replace_dependency":
                shape_problems = validate_shape(operation, {"operation", "ticket_id", "from", "to"}, path="<request>", ticket_id=None, field=operation_field)
                request_problems.extend(shape_problems)
                ticket_id = operation.get("ticket_id")
                ticket = by_id.get(ticket_id) if isinstance(ticket_id, str) else None
                old = resolve(operation.get("from"))
                new = resolve(operation.get("to"))
                if shape_problems or ticket is None or old not in ticket["dependencies"] or new is None:
                    request_problems.append(problem("graph", "invalid_dependency_replacement", "Dependency replacement requires an existing edge and valid target.", ticket_id=ticket_id if isinstance(ticket_id, str) else None))
                    continue
                ticket["dependencies"] = [new if value == old else value for value in ticket["dependencies"]]
                updated.add(ticket_id)
            elif name == "retain_contract":
                shape = validate_shape(operation, {"operation", "ticket_id", "reason", "expected_authority"}, path="<request>", ticket_id=None, field=operation_field)
                request_problems.extend(shape)
                ticket_id = operation.get("ticket_id")
                ticket = by_id.get(ticket_id) if isinstance(ticket_id, str) else None
                if shape or ticket is None or ticket["lifecycle"]["phase"] == "superseded" or not non_empty_string(operation.get("reason")) or operation.get("expected_authority") != source_fingerprint:
                    request_problems.append(problem("authority", "invalid_retention", "Retention needs a current authority fingerprint and an explicit unchanged-contract/evidence judgement.", ticket_id=ticket_id))
                    continue
                retained.add(ticket_id)
                bind_authority(task_dir, ticket, operation["reason"])
            else:
                request_problems.append(problem("contract", "unsupported_reconciliation_operation", f"Unsupported reconciliation operation: {name}"))

        for ticket_id in updated | {item["id"] for item in created}:
            ticket = by_id[ticket_id]
            if ticket["lifecycle"]["phase"] == "done":
                request_problems.append(problem("transition", "completed_contract_changed", "Do not rewrite a completed ticket or its dependency contract; create a correction ticket.", ticket_id=ticket_id))
            else:
                # Evidence from a previous interrupted/blocked attempt is not
                # silently revalidated by a dependency or contract update.
                ticket["execution"]["evidence"] = {}
                bind_authority(task_dir, ticket, request["reason"])
        prospective = list(by_id.values())
        for ticket in prospective:
            request_problems.extend(validate_ticket(public_ticket(ticket), ticket["_path"]))
        if request_problems:
            return envelope("reconcile-batch", ok=False, graph=graph, problems=request_problems), 1
        authority, authority_problems = authority_index(task_dir)
        graph_problems, _ = validate_graph(
            prospective, authority, has_hld=(task_dir / "HLD.md").is_file()
        )
        problems = authority_problems + graph_problems
        if problems:
            return envelope("reconcile-batch", ok=False, graph=graph, problems=problems), 1
        if authority_fingerprint(task_dir) != source_fingerprint:
            return envelope("reconcile-batch", ok=False, graph=graph, problems=[problem("authority", "upstream_changed", "Authority changed during reconciliation.")]), 1
        transaction_problems = commit_graph_transaction(task_dir, prospective, "reconcile-batch")
        if transaction_problems:
            return envelope("reconcile-batch", ok=False, graph=graph, problems=transaction_problems), 1
        _, committed_graph, committed_problems = validated_snapshot(task_dir)
        return (
            envelope(
                "reconcile-batch",
                ok=not committed_problems,
                result={"created": created, "updated": sorted(updated), "superseded": sorted(superseded), "retained": sorted(retained)},
                graph=committed_graph,
                problems=committed_problems,
            ),
            0 if not committed_problems else 1,
        )
    finally:
        release_lock(descriptor)
