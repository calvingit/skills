"""Normal single-ticket lifecycle command transitions."""
from __future__ import annotations
import copy
from pathlib import Path
from typing import Any
from .authority import authority_index, authority_current, bind_authority
from .contracts import envelope, invalid_field, non_empty_string, problem, validate_shape, validate_string_list, validate_summary_items, validate_ticket
from .graph import public_ticket, ticket_readiness, validate_graph
from .store import acquire_write_lock, atomic_write_ticket, release_lock, validated_snapshot
from ...scope_guard import validate_scope

def transition_failure(ticket: dict[str, Any], code: str, detail: str):
    return None, [problem("transition", code, detail, ticket_id=ticket["id"], path=ticket["_path"])]

def apply_start(ticket, request, by_id):
    if ticket["lifecycle"]["phase"] != "open" or ticket_readiness(ticket, by_id)[0] != "ready":
        return transition_failure(ticket, "ticket_not_ready", "start requires an open ticket with computed ready readiness.")
    issues=validate_shape(request,{"baseline","existing_changes","allowed_write_scope"},path="<request>",ticket_id=ticket["id"],field="")
    if issues: return None,issues
    if not validate_string_list(request["allowed_write_scope"], require_items=True):
        return None, [invalid_field("<request>", ticket["id"], "allowed_write_scope", "start requires a non-empty allowed_write_scope.")]
    try:
        validate_scope(request["allowed_write_scope"])
    except ValueError as exc:
        return None, [invalid_field("<request>", ticket["id"], "allowed_write_scope", str(exc))]
    candidate=copy.deepcopy(ticket); number=candidate["execution"]["attempt_sequence"]+1
    candidate["lifecycle"]["phase"]="in_progress"; candidate["execution"]["attempt_sequence"]=number
    candidate["execution"]["current_attempt"]={"number":number,"baseline":request["baseline"],"existing_changes":request["existing_changes"],"allowed_write_scope":request["allowed_write_scope"]}
    issues=validate_ticket(public_ticket(candidate),candidate["_path"])
    return (None,issues) if issues else (candidate,[])

def apply_block(ticket, request):
    if ticket["lifecycle"]["phase"] != "in_progress": return transition_failure(ticket,"invalid_transition","block requires an in_progress ticket.")
    issues=validate_shape(request,{"blocker","evidence"},path="<request>",ticket_id=ticket["id"],field="")
    if issues: return None,issues
    if not isinstance(request["evidence"],dict): return None,[invalid_field("<request>",ticket["id"],"evidence","evidence must be an object.")]
    candidate=copy.deepcopy(ticket); candidate["lifecycle"]["phase"]="open"; candidate["execution"]["current_attempt"]=None; candidate["execution"]["blocker"]=request["blocker"]; candidate["execution"]["evidence"].update(request["evidence"])
    issues=validate_ticket(public_ticket(candidate),candidate["_path"])
    return (None,issues) if issues else (candidate,[])

def apply_unblock(ticket, request):
    if ticket["lifecycle"]["phase"] != "open" or ticket["execution"]["blocker"] is None: return transition_failure(ticket,"invalid_transition","unblock requires an open ticket with an execution blocker.")
    issues=validate_shape(request,{"release_evidence"},path="<request>",ticket_id=ticket["id"],field="")
    if issues: return None,issues
    if not non_empty_string(request["release_evidence"]): return None,[invalid_field("<request>",ticket["id"],"release_evidence","release_evidence must be a non-empty Loop-approved summary.")]
    candidate=copy.deepcopy(ticket); candidate["execution"]["blocker"]=None
    return candidate,[]

def apply_retry(ticket, request):
    if ticket["lifecycle"]["phase"] != "in_progress":
        return transition_failure(ticket, "invalid_transition", "retry requires an in_progress ticket.")
    issues = validate_shape(request, {"expected_attempt", "baseline", "existing_changes", "allowed_write_scope", "findings"}, path="<request>", ticket_id=ticket["id"], field="")
    if issues:
        return None, issues
    if (
        not isinstance(request["expected_attempt"], int)
        or isinstance(request["expected_attempt"], bool)
        or request["expected_attempt"] != ticket["execution"]["attempt_sequence"]
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
    number = candidate["execution"]["attempt_sequence"] + 1
    invalidated_acceptance = [item["id"] for item in ticket["acceptance_criteria"]]
    for acceptance_id in invalidated_acceptance:
        candidate["execution"]["evidence"].pop(acceptance_id, None)
    candidate["execution"]["attempt_sequence"] = number
    candidate["execution"]["current_attempt"] = {
        "number": number,
        "baseline": request["baseline"],
        "existing_changes": request["existing_changes"],
        "allowed_write_scope": request["allowed_write_scope"],
    }
    candidate["execution"]["reopen_context"] = {
        "review_finding": request["findings"],
        "invalidated_acceptance": invalidated_acceptance,
    }
    issues = validate_ticket(public_ticket(candidate), candidate["_path"])
    return (None, issues) if issues else (candidate, [])

def completion_problems(request, acceptance_ids):
    """Check recorded facts and the caller's decision, without interpreting review prose."""
    issues = validate_shape(request, {"evidence", "verification", "review", "approved", "unverified"},
                            path="<request>", ticket_id=None, field="")
    if issues:
        return issues
    if not isinstance(request["evidence"], dict):
        return [invalid_field("<request>", None, "evidence", "Evidence must be keyed by acceptance ID.")]
    issues = validate_summary_items(request["verification"], {"command", "exit_code", "summary"},
                                    path="<request>", ticket_id=None, field="verification")
    if issues:
        return issues
    if not non_empty_string(request["review"]):
        return [invalid_field("<request>", None, "review", "Include the original review as a non-empty string.")]
    if (request["approved"] is not True or request["unverified"] != []
            or not request["verification"] or any(item["exit_code"] != 0 for item in request["verification"])):
        return [problem("transition", "completion_gate_failed", "Completion requires caller approval, successful verification, and no unverified scope.")]
    if set(request["evidence"]) != set(acceptance_ids):
        return [problem("transition", "done_without_acceptance_evidence", "Evidence must cover exactly the current acceptance IDs.")]
    for entry in request["evidence"].values():
        issues = validate_shape(entry, {"result", "summary"}, path="<request>", ticket_id=None, field="evidence")
        if issues:
            return issues
        if entry["result"] != "passed" or not non_empty_string(entry["summary"]):
            return [problem("transition", "completion_gate_failed", "Each acceptance ID needs passed evidence and its source/result.")]
    return []


def apply_complete(ticket, request):
    if ticket["lifecycle"]["phase"] != "in_progress":
        return transition_failure(ticket, "invalid_transition", "complete requires an in_progress ticket.")
    if not isinstance(request, dict) or type(request.get("expected_attempt")) is not int or request["expected_attempt"] != ticket["execution"]["attempt_sequence"]:
        return transition_failure(ticket, "stale_attempt", "Complete expected_attempt must match the active attempt.")
    result = {key: value for key, value in request.items() if key != "expected_attempt"}
    issues = completion_problems(result, [item["id"] for item in ticket["acceptance_criteria"]])
    if issues:
        return None, issues
    candidate = copy.deepcopy(ticket)
    candidate["execution"]["evidence"] = request["evidence"]
    candidate["execution"]["review"] = request["review"]
    candidate["execution"]["current_attempt"] = None
    candidate["execution"]["blocker"] = None
    candidate["execution"]["reopen_context"] = None
    candidate["lifecycle"]["phase"] = "done"
    issues = validate_ticket(public_ticket(candidate), candidate["_path"])
    return (None, issues) if issues else (candidate, [])

def apply_reopen(ticket, request):
    if ticket["lifecycle"]["phase"] != "done": return transition_failure(ticket,"invalid_transition","reopen requires a done ticket.")
    issues=validate_shape(request,{"review_finding","invalidated_acceptance","upstream_unchanged"},path="<request>",ticket_id=ticket["id"],field="")
    if issues: return None,issues
    invalidated=request["invalidated_acceptance"]; acs={item["id"] for item in ticket["acceptance_criteria"]}
    if request["upstream_unchanged"] is not True or not non_empty_string(request["review_finding"]) or not validate_string_list(invalidated,require_items=True) or not set(invalidated)<=acs:
        return transition_failure(ticket,"invalid_reopen_request","Reopen requires an unchanged upstream contract, a finding, and known invalidated AC IDs.")
    candidate=copy.deepcopy(ticket); candidate["lifecycle"]["phase"]="open"
    candidate["execution"].pop("review", None)
    for ac in invalidated: candidate["execution"]["evidence"].pop(ac,None)
    candidate["execution"]["reopen_context"]={"review_finding":request["review_finding"],"invalidated_acceptance":invalidated}
    issues=validate_ticket(public_ticket(candidate),candidate["_path"])
    return (None,issues) if issues else (candidate,[])

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
            first_claim = operation == "start" and ticket["execution"]["attempt_sequence"] == 0 and "authority" not in ticket["execution"]
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
        authority,authority_issues=authority_index(task_dir); graph_issues,_=validate_graph(prospective,authority,has_hld=(task_dir/"HLD.md").is_file()); issues=authority_issues+graph_issues
        if issues and operation != "block":return envelope(operation,ok=False,graph=graph,problems=issues),1
        issues=atomic_write_ticket(task_dir,candidate)
        if issues:return envelope(operation,ok=False,graph=graph,problems=issues),1
        _,graph,issues=validated_snapshot(task_dir)
        if operation == "block":
            return envelope(operation, ok=True, result={"ticket": public_ticket(candidate), "remaining_problems": issues}, graph=graph, problems=[]), 0
        return envelope(operation,ok=not issues,result={"ticket":public_ticket(candidate)},graph=graph,problems=issues),(0 if not issues else 1)
    finally: release_lock(descriptor)
