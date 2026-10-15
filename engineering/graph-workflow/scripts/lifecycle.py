"""Normal single-ticket lifecycle command transitions.

Transitions change ``.loop/state.json`` only; the ticket contract file is never
rewritten by execution, so recorded progress never edits the delivery contract.
"""
from __future__ import annotations
import copy
from pathlib import Path
from typing import Any
from ticket_graph import runtime
from ticket_graph.authority import authority_index, authority_current, bind_authority
from ticket_graph.contracts import envelope, invalid_field, non_empty_string, problem, validate_shape, validate_string_list, validate_summary_items
from ticket_graph.graph import public_ticket, ticket_readiness, validate_graph
from ticket_graph.store import acquire_write_lock, load_contracts, release_lock, validated_snapshot
from scope_guard import overlap, validate_scope

SERIAL = "serial"
SWARM = "swarm"
DISPATCH_MODES = (SERIAL, SWARM)

def transition_failure(ticket: dict[str, Any], code: str, detail: str):
    return None, [problem("transition", code, detail, ticket_id=ticket["id"], path=ticket["_path"])]

def in_progress_tickets(by_id: dict[str, dict[str, Any]], ticket_id: str) -> list[dict[str, Any]]:
    return [
        other for other in by_id.values()
        if other["id"] != ticket_id and other["runtime"]["phase"] == "in_progress"
    ]

def dispatch_problems(ticket, scope, by_id, mode) -> list[dict[str, str]]:
    """Serial is the default strategy: one implementation worker at a time.

    Concurrent attempts need the user's explicit swarm choice, and even then a
    direct delivery dependency or overlapping expected write areas blocks them.
    """
    others = in_progress_tickets(by_id, ticket["id"])
    if not others:
        return []
    if mode != SWARM:
        return [problem(
            "dispatch", "parallel_dispatch_requires_swarm",
            "Another ticket already has an attempt in progress; serial execution allows one at a time. "
            "Only an explicit user request enables swarm.",
            ticket_id=ticket["id"],
        )]
    problems: list[dict[str, str]] = []
    for other in others:
        if other["id"] in ticket["dependencies"] or ticket["id"] in other["dependencies"]:
            problems.append(problem(
                "dispatch", "dependency_blocks_parallel_dispatch",
                f"Direct delivery dependency with in-progress ticket {other['id']}.",
                ticket_id=ticket["id"],
            ))
            continue
        conflict = overlap(scope, other["runtime"].get("current_attempt", {}).get("allowed_write_scope", []))
        if conflict:
            problems.append(problem(
                "dispatch", "write_scope_overlap",
                f"Expected write areas overlap with in-progress ticket {other['id']}: {conflict[0]} / {conflict[1]}.",
                ticket_id=ticket["id"],
            ))
    return problems

def validate_evidence(evidence) -> list[dict[str, str]]:
    """Each acceptance ID needs passed evidence and its source/result."""
    if not isinstance(evidence, dict):
        return [invalid_field("<request>", None, "evidence", "Evidence must be keyed by acceptance ID.")]
    problems: list[dict[str, str]] = []
    for acceptance_id, entry in evidence.items():
        field = f"evidence.{acceptance_id}"
        issues = validate_shape(entry, {"result", "summary"}, path="<request>", ticket_id=None, field=field)
        problems.extend(issues)
        if issues:
            continue
        if entry["result"] != "passed" or not non_empty_string(entry["summary"]):
            problems.append(problem("transition", "completion_gate_failed", "Each acceptance ID needs passed evidence and its source/result."))
    return problems

def normalize_evidence(evidence, attempt: int):
    """Store each judgement together with the attempt that established it.

    Callers reject the whole request on any problem, so a failed validation
    normalizes nothing instead of a partial result.
    """
    problems = validate_evidence(evidence)
    if problems:
        return problems, {}
    return [], {
        acceptance_id: {"attempt": attempt, "summary": entry["summary"]}
        for acceptance_id, entry in evidence.items()
    }

def apply_start(ticket, request, by_id):
    entry = ticket["runtime"]
    if entry["phase"] != "open" or ticket_readiness(ticket, by_id)[0] != "ready":
        return transition_failure(ticket, "ticket_not_ready", "start requires an open ticket with computed ready readiness.")
    fields = {"baseline", "existing_changes", "allowed_write_scope"}
    if isinstance(request, dict) and "mode" in request:
        fields.add("mode")
    issues=validate_shape(request,fields,path="<request>",ticket_id=ticket["id"],field="")
    if issues: return None,issues
    mode = request.get("mode", SERIAL)
    if mode not in DISPATCH_MODES:
        return None, [invalid_field("<request>", ticket["id"], "mode", "Execution mode must be serial or swarm.")]
    if not validate_string_list(request["allowed_write_scope"], require_items=True):
        return None, [invalid_field("<request>", ticket["id"], "allowed_write_scope", "start requires a non-empty allowed_write_scope.")]
    try:
        validate_scope(request["allowed_write_scope"])
    except ValueError as exc:
        return None, [invalid_field("<request>", ticket["id"], "allowed_write_scope", str(exc))]
    issues = dispatch_problems(ticket, request["allowed_write_scope"], by_id, mode)
    if issues:
        return None, issues
    candidate=copy.deepcopy(ticket); number=entry.get("attempt", 0)+1
    candidate["runtime"].pop("review", None)
    candidate["runtime"]["phase"]="in_progress"; candidate["runtime"]["attempt"]=number
    candidate["runtime"]["current_attempt"]={"number":number,"baseline":request["baseline"],"existing_changes":request["existing_changes"],"allowed_write_scope":request["allowed_write_scope"]}
    issues=runtime.validate_ticket(public_ticket(candidate),candidate["_path"])
    return (None,issues) if issues else (candidate,[])

def apply_block(ticket, request):
    if ticket["runtime"]["phase"] != "in_progress": return transition_failure(ticket,"invalid_transition","block requires an in_progress ticket.")
    issues=validate_shape(request,{"blocker","evidence"},path="<request>",ticket_id=ticket["id"],field="")
    if issues: return None,issues
    issues,evidence=normalize_evidence(request["evidence"],ticket["runtime"].get("attempt",0))
    if issues: return None,issues
    candidate=copy.deepcopy(ticket)
    candidate["runtime"]["phase"]="open"; candidate["runtime"].pop("current_attempt",None); candidate["runtime"]["blocker"]=request["blocker"]
    candidate["runtime"]["evidence"]={**candidate["runtime"].get("evidence",{}),**evidence}
    issues=runtime.validate_ticket(public_ticket(candidate),candidate["_path"])
    return (None,issues) if issues else (candidate,[])

def apply_unblock(ticket, request):
    if ticket["runtime"]["phase"] != "open" or ticket["runtime"].get("blocker") is None: return transition_failure(ticket,"invalid_transition","unblock requires an open ticket with an execution blocker.")
    issues=validate_shape(request,{"release_evidence"},path="<request>",ticket_id=ticket["id"],field="")
    if issues: return None,issues
    if not non_empty_string(request["release_evidence"]): return None,[invalid_field("<request>",ticket["id"],"release_evidence","release_evidence must be a non-empty Loop-approved summary.")]
    candidate=copy.deepcopy(ticket); candidate["runtime"].pop("blocker",None)
    return candidate,[]

def apply_retry(ticket, request):
    entry = ticket["runtime"]
    if entry["phase"] != "in_progress":
        return transition_failure(ticket, "invalid_transition", "retry requires an in_progress ticket.")
    if isinstance(request, dict) and "allowed_write_scope" not in request:
        # Expected change areas usually stay the same across a correction; inherit them.
        request = {**request, "allowed_write_scope": entry["current_attempt"]["allowed_write_scope"]}
    issues = validate_shape(request, {"expected_attempt", "baseline", "existing_changes", "allowed_write_scope", "findings"}, path="<request>", ticket_id=ticket["id"], field="")
    if issues:
        return None, issues
    if (
        not isinstance(request["expected_attempt"], int)
        or isinstance(request["expected_attempt"], bool)
        or request["expected_attempt"] != entry.get("attempt", 0)
    ):
        return transition_failure(ticket, "stale_attempt", "retry expected_attempt does not match the current attempt.")
    if not non_empty_string(request["findings"]):
        return None, [invalid_field("<request>", ticket["id"], "findings", "findings must be non-empty.")]
    if not validate_string_list(request["allowed_write_scope"], require_items=True):
        return None, [invalid_field("<request>", ticket["id"], "allowed_write_scope", "retry requires a non-empty allowed_write_scope.")]
    try:
        validate_scope(request["allowed_write_scope"])
    except ValueError as exc:
        return None, [invalid_field("<request>", ticket["id"], "allowed_write_scope", str(exc))]
    candidate = copy.deepcopy(ticket)
    number = entry.get("attempt", 0) + 1
    candidate["runtime"].pop("review", None)
    invalidated_acceptance = [item["id"] for item in ticket["delivery_acceptance"]]
    candidate["runtime"].pop("evidence", None)
    candidate["runtime"]["attempt"] = number
    candidate["runtime"]["current_attempt"] = {
        "number": number,
        "baseline": request["baseline"],
        "existing_changes": request["existing_changes"],
        "allowed_write_scope": request["allowed_write_scope"],
    }
    candidate["runtime"]["reopen_context"] = {
        "review_finding": request["findings"],
        "invalidated_acceptance": invalidated_acceptance,
    }
    issues = runtime.validate_ticket(public_ticket(candidate), candidate["_path"])
    return (None, issues) if issues else (candidate, [])

def completion_problems(request, acceptance_ids, *, final_delivery=False):
    """Check recorded facts and, for final delivery, explicit approval without interpreting prose."""
    fields = {"evidence", "verification"}
    if final_delivery:
        fields.update({"approved", "unverified", "review"})
    elif isinstance(request, dict) and "review" in request:
        fields.add("review")
    issues = validate_shape(request, fields,
                            path="<request>", ticket_id=None, field="")
    if issues:
        return issues
    if not isinstance(request["evidence"], dict):
        return [invalid_field("<request>", None, "evidence", "Evidence must be keyed by acceptance ID.")]
    issues = validate_summary_items(request["verification"], {"command", "exit_code", "summary"},
                                    path="<request>", ticket_id=None, field="verification")
    if issues:
        return issues
    if "review" in request and not non_empty_string(request["review"]):
        return [invalid_field("<request>", None, "review", "Include the original review as a non-empty string.")]
    if not request["verification"] or any(item["exit_code"] != 0 for item in request["verification"]):
        return [problem("transition", "completion_gate_failed", "Completion requires successful verification.")]
    if final_delivery and (request["approved"] is not True or request["unverified"] != []):
        return [problem("transition", "completion_gate_failed", "Final delivery requires caller approval and no unverified scope.")]
    if set(request["evidence"]) != set(acceptance_ids):
        return [problem("transition", "done_without_acceptance_evidence", "Evidence must cover exactly the current acceptance IDs.")]
    return validate_evidence(request["evidence"])


def apply_complete(ticket, request):
    entry = ticket["runtime"]
    if entry["phase"] != "in_progress":
        return transition_failure(ticket, "invalid_transition", "complete requires an in_progress ticket.")
    if not isinstance(request, dict) or type(request.get("expected_attempt")) is not int or request["expected_attempt"] != entry.get("attempt", 0):
        return transition_failure(ticket, "stale_attempt", "Complete expected_attempt must match the active attempt.")
    result = {key: value for key, value in request.items() if key != "expected_attempt"}
    issues = completion_problems(result, [item["id"] for item in ticket["delivery_acceptance"]])
    if issues:
        return None, issues
    candidate = copy.deepcopy(ticket)
    # completion_problems validated every entry; storing only stamps the attempt.
    candidate["runtime"]["evidence"] = {
        acceptance_id: {"attempt": entry["attempt"], "summary": item["summary"]}
        for acceptance_id, item in request["evidence"].items()
    }
    candidate["runtime"].pop("review", None)
    if "review" in request:
        candidate["runtime"]["review"] = request["review"]
    candidate["runtime"].pop("current_attempt", None)
    candidate["runtime"].pop("blocker", None)
    candidate["runtime"].pop("reopen_context", None)
    candidate["runtime"]["phase"] = "done"
    issues = runtime.validate_ticket(public_ticket(candidate), candidate["_path"])
    return (None, issues) if issues else (candidate, [])

def apply_reopen(ticket, request):
    if ticket["runtime"]["phase"] != "done": return transition_failure(ticket,"invalid_transition","reopen requires a done ticket.")
    issues=validate_shape(request,{"review_finding","invalidated_acceptance","upstream_unchanged"},path="<request>",ticket_id=ticket["id"],field="")
    if issues: return None,issues
    invalidated=request["invalidated_acceptance"]; acs={item["id"] for item in ticket["delivery_acceptance"]}
    if request["upstream_unchanged"] is not True or not non_empty_string(request["review_finding"]) or not validate_string_list(invalidated,require_items=True) or not set(invalidated)<=acs:
        return transition_failure(ticket,"invalid_reopen_request","Reopen requires an unchanged upstream contract, a finding, and known invalidated AC IDs.")
    candidate=copy.deepcopy(ticket); candidate["runtime"]["phase"]="open"
    candidate["runtime"].pop("review", None)
    evidence={key:value for key,value in candidate["runtime"].get("evidence",{}).items() if key not in invalidated}
    if evidence: candidate["runtime"]["evidence"]=evidence
    else: candidate["runtime"].pop("evidence",None)
    candidate["runtime"]["reopen_context"]={"review_finding":request["review_finding"],"invalidated_acceptance":invalidated}
    issues=runtime.validate_ticket(public_ticket(candidate),candidate["_path"])
    return (None,issues) if issues else (candidate,[])

def initialize_state(task_dir: Path, request):
    """Explicitly rebuild runtime state for the current tickets.

    Only for a task whose .loop/state.json was lost or is unreadable. The caller
    must first confirm that the recorded progress is gone: every ticket restarts
    as open with no attempt and no evidence, and nothing is assumed complete.
    """
    descriptor,_,issues=acquire_write_lock(task_dir)
    if issues:return envelope("init-state",ok=False,problems=issues),1
    try:
        if (task_dir / ".ticket-graph-transaction").exists():
            return envelope("init-state",ok=False,problems=[problem("recovery","recovery_required","An unfinished graph transaction requires recovery.")]),1
        tickets,problems=load_contracts(task_dir)
        if problems:return envelope("init-state",ok=False,problems=problems),1
        issues=validate_shape(request,{"reason"},path="<request>",ticket_id=None,field="")
        if issues or not non_empty_string(request.get("reason")):
            return envelope("init-state",ok=False,problems=[*issues,invalid_field("<request>",None,"reason","Initialization needs the confirmed reason progress is considered lost.")]),1
        state,state_problems=runtime.load_state(task_dir)
        if state is not None and not state_problems:
            return envelope("init-state",ok=False,problems=[problem("storage","runtime_state_present",
                "A readable .loop/state.json already exists; initializing would discard recorded progress. "
                "Delete it only after confirming that progress is lost.",path=runtime.STATE_FILE)]),1
        for ticket in tickets:
            ticket["runtime"]=runtime.fresh_entry()
        authority,authority_issues=authority_index(task_dir);graph_issues,_=validate_graph(tickets,authority,has_solution=(task_dir/"SOLUTION.md").is_file());issues=authority_issues+graph_issues
        if issues:return envelope("init-state",ok=False,problems=issues),1
        issues=runtime.write_state(task_dir,runtime.state_from(tickets))
        if issues:return envelope("init-state",ok=False,problems=issues),1
        _,graph,issues=validated_snapshot(task_dir)
        return envelope("init-state",ok=not issues,result={"initialized":[ticket["id"] for ticket in tickets],"reason":request["reason"]},graph=graph,problems=issues),(0 if not issues else 1)
    finally: release_lock(descriptor)

def mutate_ticket(operation, task_dir: Path, ticket_id: str, request):
    descriptor,_,issues=acquire_write_lock(task_dir)
    if issues:return envelope(operation,ok=False,problems=issues),1
    try:
        tickets,graph,issues=validated_snapshot(task_dir)
        if issues and (operation != "block" or not tickets):return envelope(operation,ok=False,graph=graph,problems=issues),1
        by_id={t["id"]:t for t in tickets}; ticket=by_id.get(ticket_id)
        if ticket is None:return envelope(operation,ok=False,graph=graph,problems=[problem("graph","unknown_ticket",f"Ticket does not exist: {ticket_id}",ticket_id=ticket_id)]),1
        if operation in {"start", "retry", "complete", "reopen"}:
            # An unexecuted, manually prepared ticket may bind on its first claim.
            first_claim = operation == "start" and ticket["runtime"].get("attempt", 0) == 0 and "authority" not in ticket["runtime"]
            if not first_claim and not authority_current(task_dir, ticket):
                return envelope(operation, ok=False, graph=graph, problems=[problem("authority", "upstream_changed", "Reconcile current requirements before execution or evidence reuse.", ticket_id=ticket_id)]), 1
            if operation == "start" and any(not authority_current(task_dir, by_id[dep]) for dep in ticket["dependencies"]):
                return envelope(operation, ok=False, graph=graph, problems=[problem("authority", "stale_dependency", "Dependency evidence needs reconciliation.", ticket_id=ticket_id)]), 1
        if operation=="start":candidate,issues=apply_start(ticket,request,by_id)
        elif operation=="retry":candidate,issues=apply_retry(ticket,request)
        elif operation=="block":candidate,issues=apply_block(ticket,request)
        elif operation=="unblock":candidate,issues=apply_unblock(ticket,request)
        elif operation=="complete":candidate,issues=apply_complete(ticket,request)
        elif operation=="reopen":candidate,issues=apply_reopen(ticket,request)
        else:candidate,issues=None,[problem("contract","unsupported_operation",f"Unsupported mutation: {operation}")]
        if issues or candidate is None:return envelope(operation,ok=False,graph=graph,problems=issues),1
        if operation == "start":
            bind_authority(task_dir, candidate, "Execution contract confirmed at start.")
        prospective=[candidate if x["id"]==ticket_id else x for x in tickets]
        authority,authority_issues=authority_index(task_dir); graph_issues,_=validate_graph(prospective,authority,has_solution=(task_dir/"SOLUTION.md").is_file()); issues=authority_issues+graph_issues
        if issues and operation != "block":return envelope(operation,ok=False,graph=graph,problems=issues),1
        issues=runtime.update_entry(task_dir,ticket_id,candidate["runtime"])
        if issues:return envelope(operation,ok=False,graph=graph,problems=issues),1
        _,graph,issues=validated_snapshot(task_dir)
        if operation == "block":
            return envelope(operation, ok=True, result={"ticket": public_ticket(candidate), "remaining_problems": issues}, graph=graph, problems=[]), 0
        return envelope(operation,ok=not issues,result={"ticket":public_ticket(candidate)},graph=graph,problems=issues),(0 if not issues else 1)
    finally: release_lock(descriptor)
