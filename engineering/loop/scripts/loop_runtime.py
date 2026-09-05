"""Single-ticket Loop runtime backed by the execution-graph CLI."""

from __future__ import annotations

import json
import hashlib
import os
import subprocess
import sys
import tempfile
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

GRAPH_CLI = Path(__file__).parents[2] / "execution-graph" / "scripts" / "ticket_graph.py"

if str(GRAPH_CLI.parent) not in sys.path:
    sys.path.insert(0, str(GRAPH_CLI.parent))

from execution_graph.contracts import TICKET_ID_RE, validate_worker_receipt  # noqa: E402
from .capability_adapter import CapabilityAdapter, CapabilitySession  # noqa: E402
from .cli_backend import BackendUnavailable, CliBackend  # noqa: E402
from .receipt_artifacts import save as save_capability_receipt  # noqa: E402
from .scope_guard import allowed_scope, violations as scope_violations  # noqa: E402


Worker = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True)
class RuntimeResult:
    """The independently accepted result of one runtime attempt."""

    outcome: str
    ticket_id: str
    attempt: int | None
    graph: dict[str, Any]
    receipt: dict[str, Any] | None = None
    problems: tuple[dict[str, str], ...] = ()
    session: CapabilitySession | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "outcome": self.outcome,
            "ticket_id": self.ticket_id,
            "attempt": self.attempt,
            "graph": self.graph,
            "receipt": self.receipt,
            "problems": list(self.problems),
        }


def _problem(code: str, detail: str) -> dict[str, str]:
    return {"category": "runtime", "code": code, "detail": detail}


def _graph(operation: str, task_dir: Path, ticket_id: str | None = None, request: dict[str, Any] | None = None) -> dict[str, Any]:
    arguments = [sys.executable, str(GRAPH_CLI), operation, str(task_dir)]
    if ticket_id is not None:
        arguments.append(ticket_id)
    if request is not None:
        arguments.extend(["--input", "-"])
    result = subprocess.run(
        arguments,
        input=json.dumps(request, ensure_ascii=False) if request is not None else None,
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {
            "ok": False,
            "graph": {},
            "problems": [_problem("invalid_cli_output", result.stdout or result.stderr)],
        }
    return payload


def _receipt_path(task_dir: Path, ticket_id: str, attempt: int) -> Path:
    if not TICKET_ID_RE.fullmatch(ticket_id) or not isinstance(attempt, int) or isinstance(attempt, bool) or attempt < 1:
        raise ValueError("Invalid receipt artifact identity")
    return task_dir / ".loop" / "receipts" / ticket_id / f"attempt-{attempt}.json"


def save_receipt(
    task_dir: Path,
    receipt: dict[str, Any],
    *,
    ticket_id: str,
    attempt: int,
    agent_instance_id: str | None = None,
) -> Path:
    """Validate and atomically save one raw receipt outside the graph."""
    problems = _receipt_problems(receipt, {"id": ticket_id, "acceptance_criteria": []}, attempt, check_acceptance_ids=False)
    if problems:
        raise ValueError("Invalid worker receipt: " + "; ".join(item["detail"] for item in problems))
    if agent_instance_id is None:
        agent_instance_id = uuid.uuid4().hex
    if not agent_instance_id:
        raise ValueError("agent_instance_id must be non-empty")
    path = _receipt_path(task_dir, ticket_id, attempt)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "artifact_version": 1,
        "ticket_id": ticket_id,
        "current_attempt": attempt,
        "agent_instance_id": agent_instance_id,
        "authority_fingerprint": _authority_fingerprint(task_dir),
        "receipt": receipt,
    }
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as temporary:
            temporary_name = temporary.name
            json.dump(payload, temporary, ensure_ascii=False, indent=2)
            temporary.write("\n")
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_name, path)
    except OSError:
        if temporary_name:
            Path(temporary_name).unlink(missing_ok=True)
        raise
    return path


def load_receipt_artifact(task_dir: Path, *, ticket_id: str, attempt: int) -> dict[str, Any]:
    """Read and validate one persisted receipt artifact."""
    path = _receipt_path(task_dir, ticket_id, attempt)
    try:
        artifact = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Unable to read receipt artifact {path}: {exc}") from exc
    if not isinstance(artifact, dict) or artifact.get("artifact_version") != 1:
        raise ValueError("Unsupported receipt artifact")
    if artifact.get("ticket_id") != ticket_id or artifact.get("current_attempt") != attempt:
        raise ValueError("Receipt artifact identity does not match the requested ticket attempt")
    if "authority_fingerprint" in artifact and (
        not isinstance(artifact["authority_fingerprint"], str) or not artifact["authority_fingerprint"]
    ):
        raise ValueError("Receipt artifact has an invalid authority fingerprint")
    receipt = artifact.get("receipt")
    if not isinstance(receipt, dict) or _receipt_problems(receipt, {"id": ticket_id, "acceptance_criteria": []}, attempt, check_acceptance_ids=False):
        raise ValueError("Receipt artifact contains an invalid receipt")
    if not isinstance(artifact.get("agent_instance_id"), str) or not artifact["agent_instance_id"]:
        raise ValueError("Receipt artifact is missing agent_instance_id")
    return artifact


def load_receipt(task_dir: Path, *, ticket_id: str, attempt: int) -> dict[str, Any]:
    return load_receipt_artifact(task_dir, ticket_id=ticket_id, attempt=attempt)["receipt"]


def _workspace_status(workspace_root: Path) -> dict[str, str] | None:
    """Return a complete git status probe, including ignored files."""
    result = subprocess.run(
        [
            "git",
            "-C",
            str(workspace_root),
            "status",
            "--porcelain=v1",
            "-uall",
            "--ignored=matching",
            "-z",
        ],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    status: dict[str, str] = {}
    entries = result.stdout.decode("utf-8", errors="surrogateescape").split("\0")
    index = 0
    while index < len(entries):
        entry = entries[index]
        index += 1
        if not entry or len(entry) < 3 or entry[2] != " ":
            continue
        state, relative = entry[:2], entry[3:]
        if state[0] in {"R", "C"} or state[1] in {"R", "C"}:
            status[relative] = state
            if index < len(entries) and entries[index]:
                status[entries[index]] = state
                index += 1
        elif state == "!!" and relative.endswith("/"):
            ignored_root = workspace_root / relative.rstrip("/")
            expanded = False
            try:
                for path in ignored_root.rglob("*"):
                    if path.is_file() or path.is_symlink():
                        status[path.relative_to(workspace_root).as_posix()] = state
                        expanded = True
            except OSError:
                return None
            if not expanded:
                status[relative] = state
        else:
            status[relative] = state
    tracked = subprocess.run(
        ["git", "-C", str(workspace_root), "ls-files", "-z"],
        capture_output=True,
        check=False,
    )
    if tracked.returncode != 0:
        return None
    for relative_bytes in tracked.stdout.split(b"\0"):
        if relative_bytes:
            relative = relative_bytes.decode("utf-8", errors="surrogateescape")
            status.setdefault(relative, "  ")
    return status


def _workspace_snapshot(workspace_root: Path) -> dict[str, tuple[str, str | None]] | None:
    status = _workspace_status(workspace_root)
    if status is None:
        return None
    snapshot: dict[str, tuple[str, str | None]] = {}
    for relative, state in status.items():
        path = workspace_root / relative
        try:
            digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        except (OSError, UnicodeError):
            digest = None
        snapshot[relative] = (state, digest)
    return snapshot


def _snapshot_changed(
    before: dict[str, tuple[str, str | None]],
    after: dict[str, tuple[str, str | None]],
) -> set[str]:
    return {
        path
        for path in set(before) | set(after)
        if before.get(path) != after.get(path)
    }


def _workspace_revision(workspace_root: Path) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(workspace_root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def _commit_ticket_changes(
    workspace_root: Path,
    ticket: dict[str, Any],
    changed_paths: set[str],
    before: dict[str, tuple[str, str | None]],
) -> None:
    """Commit only clean-baseline paths changed by the accepted ticket."""
    paths = sorted(path for path in changed_paths if path not in before or before[path][0] == "  ")
    if not paths:
        return
    add = subprocess.run(["git", "-C", str(workspace_root), "add", "-A", "--", *paths], capture_output=True, text=True, check=False)
    if add.returncode != 0:
        raise RuntimeError(add.stderr.strip() or "git add failed")
    staged = subprocess.run(["git", "-C", str(workspace_root), "diff", "--cached", "--quiet"], check=False)
    if staged.returncode == 0:
        return
    if staged.returncode != 1:
        raise RuntimeError("Unable to inspect staged ticket changes")
    title = str(ticket.get("title") or ticket["id"]).strip()
    commit = subprocess.run(
        ["git", "-C", str(workspace_root), "commit", "--only", "-m", f"feat(ticket): {ticket['id']} {title}", "--", *paths],
        capture_output=True,
        text=True,
        check=False,
    )
    if commit.returncode != 0:
        raise RuntimeError(commit.stderr.strip() or "git commit failed")


def _git_metadata_fingerprint(workspace_root: Path) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(workspace_root), "rev-parse", "--git-dir"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    git_dir = Path(result.stdout.strip())
    if not git_dir.is_absolute():
        git_dir = workspace_root / git_dir
    digest = hashlib.sha256()
    try:
        for path in sorted(item for item in git_dir.rglob("*") if item.is_file() and "/objects/" not in item.as_posix()):
            digest.update(path.relative_to(git_dir).as_posix().encode("utf-8", "surrogateescape"))
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
    except (OSError, UnicodeError):
        return None
    return digest.hexdigest()


def _workspace_baseline(workspace_root: Path) -> dict[str, Any]:
    status = _workspace_status(workspace_root) or {}
    return {
        "reference": f"git status at {workspace_root}",
        "staged": sorted(path for path, value in status.items() if value != "??" and value[0] != " "),
        "unstaged": sorted(path for path, value in status.items() if value != "??" and value[1] != " "),
        "untracked": sorted(path for path, value in status.items() if value == "??"),
    }


def _authority_fingerprint(task_dir: Path) -> str:
    digest = hashlib.sha256()
    for name in ("SPEC.md", "HLD.md"):
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        path = task_dir / name
        if path.is_file():
            digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _workspace_relative(workspace_root: Path, path: Path) -> str | None:
    try:
        return path.resolve().relative_to(workspace_root.resolve()).as_posix()
    except ValueError:
        return None


def _changed_paths(before: dict[str, str], after: dict[str, str]) -> list[str]:
    return sorted(
        path
        for path in set(before) | set(after)
        if before.get(path) != after.get(path)
    )


def _scope_contains(scope: list[str], path: str) -> bool:
    return any(path == item or path.startswith(item.rstrip("/") + "/") for item in scope)


def _graph_files(task_dir: Path) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for name in ("SPEC.md", "HLD.md"):
        path = task_dir / name
        if path.is_file():
            files[name] = path.read_bytes()
    for path in sorted((task_dir / "tickets").glob("*.json")):
        files[path.relative_to(task_dir).as_posix()] = path.read_bytes()
    return files


def _receipt_problems(receipt: object, ticket: dict[str, Any], attempt: int, *, check_acceptance_ids: bool = True) -> list[dict[str, str]]:
    problems = validate_worker_receipt(receipt)
    if problems or not isinstance(receipt, dict):
        return problems or [_problem("invalid_receipt", "Worker receipt must be a JSON object.")]
    if receipt["ticket_id"] != ticket["id"]:
        problems.append(_problem("receipt_ticket_mismatch", "Receipt ticket_id does not match the started ticket."))
    if receipt["current_attempt"] != attempt:
        problems.append(_problem("receipt_attempt_mismatch", "Receipt current_attempt does not match the started attempt."))
    if check_acceptance_ids:
        local_ids = {item["id"] for item in ticket["acceptance_criteria"]}
        evidence_ids = {item["acceptance_id"] for item in receipt["acceptance_evidence"]}
        unknown = evidence_ids - local_ids
        if unknown:
            problems.append(_problem("unknown_acceptance_evidence", f"Receipt references unknown local AC IDs: {', '.join(sorted(unknown))}."))
    return problems


def _normalized_evidence(receipt: dict[str, Any]) -> dict[str, dict[str, str]]:
    return {
        item["acceptance_id"]: {"result": "passed", "summary": item["summary"]}
        for item in receipt["acceptance_evidence"]
        if item["result"] == "passed"
    }


def _repair_findings(payload: object) -> str:
    if isinstance(payload, dict):
        for key in ("reason", "findings"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value
        review = payload.get("review")
        if isinstance(review, dict) and review:
            return "Review capability findings: " + json.dumps(review, ensure_ascii=False, sort_keys=True)
    return "Capability verification failed."


def reopen_ticket(
    task_dir: Path,
    ticket_id: str,
    *,
    review_finding: str,
    invalidated_acceptance: list[str],
) -> RuntimeResult:
    """Reopen a completed ticket through the graph contract after review."""
    shown = _graph("show", task_dir.resolve(), ticket_id)
    if not shown.get("ok"):
        return _result("failed", ticket_id, shown.get("graph", {}), problems=shown.get("problems", []))
    ticket = shown.get("result", {}).get("ticket", {})
    attempt = ticket.get("execution", {}).get("attempt_sequence") if isinstance(ticket, dict) else None
    try:
        artifact = load_receipt_artifact(task_dir.resolve(), ticket_id=ticket_id, attempt=attempt)
    except (TypeError, ValueError) as exc:
        return _result("failed", ticket_id, shown.get("graph", {}), problems=[_problem("missing_authority_snapshot", str(exc))])
    try:
        current_fingerprint = _authority_fingerprint(task_dir.resolve())
    except (OSError, UnicodeError) as exc:
        return _result("failed", ticket_id, shown.get("graph", {}), problems=[_problem("authority_unreadable", str(exc))])
    if artifact.get("authority_fingerprint") != current_fingerprint:
        return _result("failed", ticket_id, shown.get("graph", {}), problems=[_problem("upstream_changed", "SPEC.md or HLD.md changed since the completed attempt.")])
    reopened = _graph(
        "reopen",
        task_dir.resolve(),
        ticket_id,
        {
            "review_finding": review_finding,
            "invalidated_acceptance": invalidated_acceptance,
            "upstream_unchanged": True,
        },
    )
    return _result("reopened" if reopened.get("ok") else "failed", ticket_id, reopened.get("graph", {}), problems=reopened.get("problems", []))


def _result(outcome: str, ticket_id: str, graph: dict[str, Any], *, attempt: int | None = None, receipt: dict[str, Any] | None = None, problems: list[dict[str, str]] | None = None, session: CapabilitySession | None = None) -> RuntimeResult:
    return RuntimeResult(outcome, ticket_id, attempt, graph, receipt, tuple(problems or []), session)


def _completion_gate_problem(task_dir: Path, ticket: dict[str, Any], receipt: dict[str, Any]) -> dict[str, str] | None:
    evidence = _normalized_evidence(receipt)
    local_ids = {item["id"] for item in ticket["acceptance_criteria"]}
    if set(evidence) != local_ids or any(item["result"] != "passed" for item in receipt["acceptance_evidence"]):
        return _problem("completion_gate_failed", "Every local AC needs passed evidence before complete.")
    if not receipt["verification"] or any(item["exit_code"] != 0 for item in receipt["verification"]):
        return _problem("completion_gate_failed", "All receipt verification commands must exit 0.")
    has_hld = (task_dir / "HLD.md").is_file()
    if receipt["review"]["standards"] != "pass" or receipt["review"]["spec"] != "pass" or receipt["review"]["hld"] != ("pass" if has_hld else "not_applicable") or receipt["unverified"]:
        return _problem("completion_gate_failed", "Applicable reviews must pass and unverified must be empty.")
    return None


def _apply_receipt(task_dir: Path, started_ticket: dict[str, Any], started_graph: dict[str, Any], receipt: dict[str, Any], attempt: int) -> RuntimeResult:
    ticket_id = started_ticket["id"]
    evidence = _normalized_evidence(receipt)
    if receipt["outcome"] == "completed":
        gate_problem = _completion_gate_problem(task_dir, started_ticket, receipt)
        if gate_problem:
            return _result("failed", ticket_id, started_graph, attempt=attempt, receipt=receipt, problems=[gate_problem])
        completed = _graph("complete", task_dir, ticket_id, {"evidence": evidence, "verification": receipt["verification"], "reviews": receipt["review"], "unverified": receipt["unverified"]})
        return _result("completed" if completed.get("ok") else "failed", ticket_id, completed.get("graph", {}), attempt=attempt, receipt=receipt, problems=completed.get("problems", []))
    if receipt["outcome"] == "blocked" and receipt["blocker"] is not None:
        blocked = _graph("block", task_dir, ticket_id, {"blocker": receipt["blocker"], "evidence": evidence})
        return _result("blocked" if blocked.get("ok") else "failed", ticket_id, blocked.get("graph", {}), attempt=attempt, receipt=receipt, problems=blocked.get("problems", []))
    if receipt["outcome"] == "interrupted":
        return _result("interrupted", ticket_id, started_graph, attempt=attempt, receipt=receipt)
    return _result("failed", ticket_id, started_graph, attempt=attempt, receipt=receipt, problems=[_problem("worker_outcome_unhandled", "Only a completed receipt with a passing gate or a blocked receipt with a blocker can mutate the graph.")])


def _worker_request(task_dir: Path, started_ticket: dict[str, Any], existing_changes: dict[str, list[str]], scope: list[str], agent_instance_id: str) -> dict[str, Any]:
    dependency_evidence = []
    for dependency_id in started_ticket["dependencies"]:
        dependency = _graph("show", task_dir, dependency_id).get("result", {}).get("ticket", {})
        dependency_evidence.append({"ticket_id": dependency_id, "evidence": dependency.get("execution", {}).get("evidence", {})})
    return {
        "task_dir": str(task_dir),
        "spec": (task_dir / "SPEC.md").read_text(encoding="utf-8"),
        "hld": (task_dir / "HLD.md").read_text(encoding="utf-8") if (task_dir / "HLD.md").is_file() else None,
        "ticket": started_ticket,
        "attempt": started_ticket["execution"]["current_attempt"]["number"],
        "agent_instance_id": agent_instance_id,
        "dependencies": dependency_evidence,
        "existing_changes": existing_changes,
        "allowed_write_scope": scope,
    }


def dispatch_ready(
    task_dir: Path,
    worker: Worker,
    *,
    concurrency_limit: int = 1,
    isolation_proof: dict[str, bool] | None = None,
    workspace_root: Path | None = None,
    baseline: dict[str, Any] | None = None,
    existing_changes: dict[str, list[str]] | None = None,
    allowed_write_scope: list[str] | None = None,
    allowed_write_scopes: dict[str, list[str]] | None = None,
    commit_on_complete: bool = True,
) -> list[RuntimeResult]:
    """Dispatch the current frontier serially unless all isolation proofs pass."""
    task_dir = task_dir.resolve()
    ready_payload = _graph("list", task_dir)
    if not ready_payload.get("ok"):
        return [
            _result(
                "blocked",
                "",
                ready_payload.get("graph", {}),
                problems=ready_payload.get("problems", [_problem("graph_unavailable", "Unable to list ready tickets.")]),
            )
        ]
    candidates = [item for item in ready_payload.get("result", {}).get("tickets", []) if item.get("readiness") == "ready"]
    active_tickets = ready_payload.get("graph", {}).get("in_progress", [])
    if active_tickets and not isinstance(active_tickets, list):
        active_tickets = []
    if active_tickets:
        if len(active_tickets) > 1:
            return [_result("blocked", "", ready_payload.get("graph", {}), problems=[_problem("multiple_in_progress", "Multiple in-progress tickets require an explicit ticket_id to resume.")])]
        return [
            run_ticket(
                task_dir,
                worker,
                ticket_id=active_tickets[0],
                workspace_root=workspace_root,
                baseline=baseline,
                existing_changes=existing_changes,
                allowed_write_scope=(allowed_write_scopes or {}).get(active_tickets[0], allowed_write_scope),
                commit_on_complete=commit_on_complete,
            )
        ]
    if not candidates:
        return []
    # ponytail: shared workspace cannot attribute simultaneous writes to a worker; keep ticket dispatch serial until isolated worktrees exist.
    parallel = False
    if not parallel:
        return [
            run_ticket(
                task_dir,
                worker,
                ticket_id=item["id"],
                workspace_root=workspace_root,
                baseline=baseline,
                existing_changes=existing_changes,
                allowed_write_scope=(allowed_write_scopes or {}).get(item["id"], allowed_write_scope),
                commit_on_complete=commit_on_complete,
            )
            for item in candidates
        ]

    workspace_root = (workspace_root or Path.cwd()).resolve()
    current_baseline = baseline or _workspace_baseline(workspace_root)
    current_existing = existing_changes or {"included": [], "excluded": sorted(current_baseline.get("untracked", []))}
    started: list[tuple[dict[str, Any], int, str, list[str]]] = []
    for item in candidates[:concurrency_limit]:
        ticket_id = item["id"]
        scope = candidate_scopes[ticket_id]
        result = _graph("show", task_dir, ticket_id)
        ticket = result.get("result", {}).get("ticket")
        if not isinstance(ticket, dict):
            continue
        started_payload = _graph("start", task_dir, ticket_id, {"baseline": current_baseline, "existing_changes": current_existing, "allowed_write_scope": scope})
        if started_payload.get("ok"):
            started_ticket = started_payload["result"]["ticket"]
            started.append((started_ticket, started_ticket["execution"]["current_attempt"]["number"], uuid.uuid4().hex, scope))
    if len(started) < 2:
        results: list[RuntimeResult] = []
        started_ids = {ticket["id"] for ticket, _, _, _ in started}
        for ticket, attempt, _, _ in started:
            blocked = _graph(
                "block",
                task_dir,
                ticket["id"],
                {
                    "blocker": {
                        "category": "environment",
                        "reason": "Parallel dispatch could not start every selected ticket.",
                        "release_condition": "The ready frontier can be started again.",
                    },
                    "evidence": {},
                },
            )
            results.append(_result("blocked" if blocked.get("ok") else "failed", ticket["id"], blocked.get("graph", {}), attempt=attempt, problems=blocked.get("problems", [])))
        results.extend(
            run_ticket(
                task_dir,
                worker,
                ticket_id=item["id"],
                workspace_root=workspace_root,
                baseline=current_baseline,
                existing_changes=current_existing,
                allowed_write_scope=(allowed_write_scopes or {}).get(item["id"], allowed_write_scope),
                commit_on_complete=commit_on_complete,
            )
            for item in candidates
            if item["id"] not in started_ids
        )
        return results

    graph_before_worker = _graph_files(task_dir)
    workspace_before_worker = _workspace_snapshot(workspace_root)
    revision_before_worker = _workspace_revision(workspace_root)
    metadata_before_worker = _git_metadata_fingerprint(workspace_root)
    if metadata_before_worker is None:
        return [_result("failed", ticket["id"], {}, attempt=attempt, problems=[_problem("workspace_probe_unavailable", "Loop could not fingerprint Git metadata before the worker ran.")]) for ticket, attempt, _, _ in started]
    requests = {
        ticket["id"]: _worker_request(task_dir, ticket, current_existing, scope, agent_id)
        for ticket, _, agent_id, scope in started
    }
    receipts: dict[str, dict[str, Any] | None] = {}
    with ThreadPoolExecutor(max_workers=min(concurrency_limit, len(started))) as executor:
        futures = {executor.submit(worker, request): ticket_id for ticket_id, request in requests.items()}
        for future in as_completed(futures):
            ticket_id = futures[future]
            try:
                value = future.result()
                receipts[ticket_id] = value if isinstance(value, dict) else None
            except Exception:
                receipts[ticket_id] = None

    if _graph_files(task_dir) != graph_before_worker or (
        revision_before_worker is not None and _workspace_revision(workspace_root) != revision_before_worker
    ) or metadata_before_worker is None or _git_metadata_fingerprint(workspace_root) != metadata_before_worker:
        return [_result("failed", ticket["id"], {}, attempt=attempt, problems=[_problem("worker_mutated_graph", "Parallel worker changed SPEC, HLD, or ticket JSON.")]) for ticket, attempt, _, _ in started]
    if workspace_before_worker is not None:
        after = _workspace_snapshot(workspace_root) or {}
        changed = _snapshot_changed(workspace_before_worker, after)
        if any(sum(_scope_contains(scope, path) for _, _, _, scope in started) != 1 for path in changed):
            return [_result("failed", ticket["id"], {}, attempt=attempt, problems=[_problem("write_scope_violation", "Parallel worker changed a path without an isolation proof.")]) for ticket, attempt, _, _ in started]

    results: list[RuntimeResult] = []
    for ticket, attempt, agent_id, _ in started:
        receipt = receipts.get(ticket["id"])
        if receipt is None:
            results.append(_result("failed", ticket["id"], {}, attempt=attempt, problems=[_problem("worker_failed", "Parallel worker did not return a receipt.")]))
            continue
        problems = _receipt_problems(receipt, ticket, attempt)
        if problems:
            results.append(_result("failed", ticket["id"], {}, attempt=attempt, receipt=receipt, problems=problems))
            continue
        try:
            save_receipt(task_dir, receipt, ticket_id=ticket["id"], attempt=attempt, agent_instance_id=agent_id)
        except (OSError, ValueError) as exc:
            results.append(_result("failed", ticket["id"], {}, attempt=attempt, receipt=receipt, problems=[_problem("receipt_artifact_failed", str(exc))]))
            continue
        if receipt["outcome"] == "failed":
            retry = _graph(
                "retry",
                task_dir,
                ticket["id"],
                {
                    "expected_attempt": attempt,
                    "baseline": _workspace_baseline(workspace_root),
                    "existing_changes": current_existing,
                    "allowed_write_scope": next(scope for started_ticket, _, _, scope in started if started_ticket["id"] == ticket["id"]),
                    "findings": _repair_findings(receipt),
                },
            )
            results.append(_result("retry" if retry.get("ok") else "failed", ticket["id"], retry.get("graph", {}), attempt=attempt, receipt=receipt, problems=retry.get("problems", [])))
        else:
            results.append(_apply_receipt(task_dir, ticket, {}, receipt, attempt))
    if len(started) < len(candidates):
        results.extend(
            dispatch_ready(
                task_dir,
                worker,
                concurrency_limit=concurrency_limit,
                isolation_proof=isolation_proof,
                workspace_root=workspace_root,
                baseline=current_baseline,
                existing_changes=current_existing,
                allowed_write_scope=allowed_write_scope,
                allowed_write_scopes=allowed_write_scopes,
                commit_on_complete=commit_on_complete,
            )
        )
    return results


def run_ticket(
    task_dir: Path,
    worker: Worker | None = None,
    *,
    adapter: CapabilityAdapter | None = None,
    ticket_id: str | None = None,
    workspace_root: Path | None = None,
    baseline: dict[str, Any] | None = None,
    existing_changes: dict[str, list[str]] | None = None,
    allowed_write_scope: list[str] | None = None,
    isolation_proof: dict[str, bool] | None = None,
    concurrency_limit: int = 1,
    adapter_session: CapabilitySession | None = None,
    provider: str | None = None,
    cli_session_dir: Path | None = None,
    cli_timeout: float | None = None,
    cli_heartbeat_file: Path | None = None,
    cli_heartbeat_timeout: float | None = None,
    cli_progress_timeout: float | None = None,
    commit_on_complete: bool = True,
) -> RuntimeResult:
    """Run the first ready ticket (or ``ticket_id``) through one serial attempt."""
    task_dir = task_dir.resolve()
    workspace_root = (workspace_root or Path.cwd()).resolve()
    inspected = _graph("inspect", task_dir)
    if not inspected.get("ok"):
        return _result("blocked", ticket_id or "", inspected.get("graph", {}), problems=inspected.get("problems", []))

    ready = _graph("list", task_dir)
    candidates = [item for item in ready.get("result", {}).get("tickets", []) if item.get("readiness") == "ready"]
    if ticket_id is not None:
        candidates = [item for item in candidates if item.get("id") == ticket_id]
    resuming = False
    if not candidates and ticket_id is None:
        active_tickets = ready.get("graph", {}).get("in_progress", [])
        if isinstance(active_tickets, list) and len(active_tickets) == 1:
            candidates = [{"id": active_tickets[0]}]
            resuming = True
        elif isinstance(active_tickets, list) and len(active_tickets) > 1:
            return _result("blocked", "", ready.get("graph", {}), problems=[_problem("multiple_in_progress", "Multiple in-progress tickets require an explicit ticket_id to resume.")])
    if not candidates and ticket_id is not None:
        resumed = _graph("show", task_dir, ticket_id)
        resumed_ticket = resumed.get("result", {}).get("ticket")
        if isinstance(resumed_ticket, dict) and resumed_ticket.get("lifecycle", {}).get("phase") == "in_progress":
            candidates = [{"id": ticket_id}]
            resuming = True
    if not candidates:
        return _result("blocked", ticket_id or "", ready.get("graph", {}), problems=[_problem("ticket_not_ready", "No requested or frontier ticket is ready.")])
    selected_id = candidates[0]["id"]
    shown = _graph("show", task_dir, selected_id)
    ticket = shown.get("result", {}).get("ticket")
    if not isinstance(ticket, dict):
        return _result("blocked", selected_id, shown.get("graph", {}), problems=shown.get("problems", []))

    requested_scope = allowed_write_scope
    if adapter is None and provider is not None:
        try:
            cli_backend = CliBackend(
                    provider,
                    workspace=workspace_root,
                    session_dir=cli_session_dir,
                    timeout=cli_timeout,
                    heartbeat_file=cli_heartbeat_file,
                    heartbeat_timeout=cli_heartbeat_timeout,
                    progress_timeout=cli_progress_timeout,
                )
            if not cli_backend.available():
                raise BackendUnavailable(f"CLI executable is unavailable: {provider}")
            adapter = CapabilityAdapter(cli_backend)
            adapter_session = adapter_session or CapabilitySession()
        except (BackendUnavailable, ValueError) as exc:
            return _result("failed", selected_id, ready.get("graph", {}), problems=[_problem("provider_unavailable", str(exc))])
    if worker is None and adapter is None:
        return _result("failed", selected_id, ready.get("graph", {}), problems=[_problem("missing_executor", "Either worker or adapter is required.")])

    if _workspace_snapshot(workspace_root) is None:
        return _result("failed", selected_id, ready.get("graph", {}), problems=[_problem("workspace_probe_unavailable", "Loop requires a Git workspace with a complete status probe before starting a worker.")])

    scope = requested_scope or []
    if resuming:
        persisted_scope = ticket.get("execution", {}).get("current_attempt", {}).get("allowed_write_scope")
        if not _scope_is_valid(persisted_scope):
            return _result("failed", selected_id, ready.get("graph", {}), problems=[_problem("invalid_persisted_scope", "The in-progress attempt has no valid allowed_write_scope.")])
        if requested_scope is not None and requested_scope != persisted_scope:
            return _result("failed", selected_id, ready.get("graph", {}), problems=[_problem("scope_mismatch", "A resumed attempt must reuse its persisted allowed_write_scope.")])
        scope = persisted_scope
    elif not _scope_is_valid(scope):
        return _result("failed", selected_id, ready.get("graph", {}), problems=[_problem("invalid_write_scope", "implement requires a non-empty write scope of non-empty paths.")])

    if resuming:
        persisted_attempt = ticket.get("execution", {}).get("current_attempt", {})
        current_baseline = persisted_attempt.get("baseline")
        current_existing = persisted_attempt.get("existing_changes")
        if not isinstance(current_baseline, dict) or not isinstance(current_existing, dict):
            return _result("failed", selected_id, ready.get("graph", {}), problems=[_problem("invalid_persisted_attempt", "The in-progress ticket has no usable persisted baseline or existing-change classification.")])
    else:
        current_baseline = baseline or _workspace_baseline(workspace_root)
        current_existing = existing_changes or {"included": [], "excluded": sorted(current_baseline.get("untracked", []))}
    if resuming:
        started = _graph("show", task_dir, selected_id)
        started_ticket = started.get("result", {}).get("ticket")
        if not isinstance(started_ticket, dict):
            return _result("failed", selected_id, started.get("graph", {}), problems=started.get("problems", []))
    else:
        started = _graph(
            "start",
            task_dir,
            selected_id,
            {"baseline": current_baseline, "existing_changes": current_existing, "allowed_write_scope": scope},
        )
        if not started.get("ok"):
            return _result("blocked", selected_id, started.get("graph", {}), problems=started.get("problems", []))
        started_ticket = started["result"]["ticket"]
    attempt = started_ticket["execution"]["current_attempt"]["number"]
    graph_before_worker = _graph_files(task_dir)
    workspace_before_worker = _workspace_snapshot(workspace_root)
    if workspace_before_worker is None:
        return _result("failed", selected_id, started.get("graph", {}), attempt=attempt, problems=[_problem("workspace_probe_unavailable", "Loop could not establish a complete workspace status after the graph transition.")])
    revision_before_worker = _workspace_revision(workspace_root)
    metadata_before_worker = _git_metadata_fingerprint(workspace_root)
    if metadata_before_worker is None:
        return _result("failed", selected_id, started.get("graph", {}), attempt=attempt, problems=[_problem("workspace_probe_unavailable", "Loop could not fingerprint Git metadata before the worker ran.")])
    agent_instance_id = uuid.uuid4().hex
    worker_request = _worker_request(task_dir, started_ticket, current_existing, scope, agent_instance_id)
    runtime_artifact_paths: set[str] = set()
    try:
        if adapter is not None:
            checkpoint_status = workspace_before_worker
            checkpoint_lock = threading.Lock()

            def checkpoint(capability_result: Any) -> None:
                nonlocal checkpoint_status
                with checkpoint_lock:
                    current_status = _workspace_snapshot(workspace_root)
                    if (
                        revision_before_worker is not None and _workspace_revision(workspace_root) != revision_before_worker
                    ) or _git_metadata_fingerprint(workspace_root) != metadata_before_worker:
                        raise ValueError("Worker changed the Git HEAD; Loop workers must not commit or rewrite history.")
                    if checkpoint_status is not None and current_status is not None:
                        changed = [path for path in _snapshot_changed(checkpoint_status, current_status) if path not in runtime_artifact_paths]
                        violations = scope_violations(capability_result.capability, scope if capability_result.capability == "implement" else [], changed)
                        if violations:
                            raise ValueError(f"{capability_result.capability} changed paths outside its scope: {', '.join(violations)}")
                    artifact_path = save_capability_receipt(task_dir, ticket_id=selected_id, attempt=attempt, capability=capability_result.capability, payload=capability_result.payload, agent_instance_id=capability_result.agent_instance_id)
                    relative_artifact = _workspace_relative(workspace_root, artifact_path)
                    if relative_artifact is not None:
                        runtime_artifact_paths.add(relative_artifact)
                    checkpoint_status = _workspace_snapshot(workspace_root)

            aggregate = adapter.run(
                worker_request,
                isolation_proof=isolation_proof,
                concurrency_limit=concurrency_limit,
                after_capability=checkpoint,
                session=adapter_session,
                keep_session=adapter_session is not None,
            )
            aggregate_path = save_capability_receipt(task_dir, ticket_id=selected_id, attempt=attempt, capability="aggregate", payload=aggregate)
            relative_aggregate = _workspace_relative(workspace_root, aggregate_path)
            if relative_aggregate is not None:
                runtime_artifact_paths.add(relative_aggregate)
            if _graph_files(task_dir) != graph_before_worker or (
                revision_before_worker is not None and _workspace_revision(workspace_root) != revision_before_worker
            ) or _git_metadata_fingerprint(workspace_root) != metadata_before_worker:
                if adapter_session is not None:
                    adapter.close_session(adapter_session)
                return _result("failed", selected_id, started.get("graph", {}), attempt=attempt, problems=[_problem("worker_mutated_graph", "Worker changed SPEC, HLD, or ticket JSON; graph remains owned by Loop.")])
            receipt = aggregate.get("receipt") if isinstance(aggregate, dict) else None
            capabilities = aggregate.get("capabilities", []) if isinstance(aggregate, dict) else []
            failed = next((item for item in capabilities if item.get("outcome") == "failed"), None)
            blocked = next((item for item in capabilities if item.get("outcome") == "blocked"), None)
            interrupted = next((item for item in capabilities if item.get("outcome") == "interrupted"), None)
            if interrupted is not None:
                if adapter_session is not None:
                    adapter.close_session(adapter_session)
                return _result("interrupted", selected_id, started.get("graph", {}), attempt=attempt, receipt=receipt)
            if blocked is not None:
                if adapter_session is not None:
                    adapter.close_session(adapter_session)
                blocker = blocked.get("payload", {}).get("blocker")
                if not isinstance(blocker, dict):
                    blocker = {"category": "environment", "reason": "Capability execution was interrupted or blocked.", "release_condition": "The capability runtime becomes available."}
                blocked_result = _graph("block", task_dir, selected_id, {"blocker": blocker, "evidence": {}})
                return _result("blocked" if blocked_result.get("ok") else "failed", selected_id, blocked_result.get("graph", {}), attempt=attempt, receipt=receipt, problems=blocked_result.get("problems", []))
            if failed is not None:
                findings = _repair_findings(failed.get("payload"))
                retry = _graph("retry", task_dir, selected_id, {"expected_attempt": attempt, "baseline": _workspace_baseline(workspace_root), "existing_changes": current_existing, "allowed_write_scope": scope, "findings": findings})
                if not retry.get("ok") and adapter_session is not None:
                    adapter.close_session(adapter_session)
                return _result("retry" if retry.get("ok") else "failed", selected_id, retry.get("graph", {}), attempt=attempt, receipt=receipt, problems=retry.get("problems", []), session=adapter_session if retry.get("ok") else None)
        else:
            receipt = worker(worker_request)  # type: ignore[misc]
    except Exception as exc:  # worker boundary: preserve graph state for retry
        if adapter_session is not None:
            adapter.close_session(adapter_session)
        if _graph_files(task_dir) != graph_before_worker or (
            revision_before_worker is not None and _workspace_revision(workspace_root) != revision_before_worker
        ) or _git_metadata_fingerprint(workspace_root) != metadata_before_worker:
            return _result("failed", selected_id, started.get("graph", {}), attempt=attempt, problems=[_problem("worker_mutated_graph", "Worker changed SPEC, HLD, or ticket JSON; graph remains owned by Loop.")])
        return _result("failed", selected_id, started.get("graph", {}), attempt=attempt, problems=[_problem("worker_failed", str(exc))])
    if _graph_files(task_dir) != graph_before_worker or (
        revision_before_worker is not None and _workspace_revision(workspace_root) != revision_before_worker
    ) or _git_metadata_fingerprint(workspace_root) != metadata_before_worker:
        if adapter_session is not None:
            adapter.close_session(adapter_session)
        return _result("failed", selected_id, started.get("graph", {}), attempt=attempt, receipt=receipt if isinstance(receipt, dict) else None, problems=[_problem("worker_mutated_graph", "Worker changed SPEC, HLD, or ticket JSON; graph remains owned by Loop.")])
    problems = _receipt_problems(receipt, started_ticket, attempt)
    if problems or not isinstance(receipt, dict):
        if adapter_session is not None:
            adapter.close_session(adapter_session)
        return _result("failed", selected_id, started.get("graph", {}), attempt=attempt, receipt=receipt if isinstance(receipt, dict) else None, problems=problems)
    workspace_after_worker = _workspace_snapshot(workspace_root)
    if workspace_after_worker is None:
        if adapter_session is not None:
            adapter.close_session(adapter_session)
        return _result("failed", selected_id, started.get("graph", {}), attempt=attempt, receipt=receipt, problems=[_problem("workspace_probe_unavailable", "Loop could not re-check the complete workspace status after the worker ran.")])
    changed = _snapshot_changed(workspace_before_worker, workspace_after_worker)
    if adapter is not None:
        changed -= runtime_artifact_paths
    out_of_scope = sorted(path for path in changed if not _scope_contains(scope, path))
    if out_of_scope:
        if adapter_session is not None:
            adapter.close_session(adapter_session)
        return _result("failed", selected_id, started.get("graph", {}), attempt=attempt, receipt=receipt, problems=[_problem("write_scope_violation", f"Worker changed paths outside allowed_write_scope: {', '.join(out_of_scope)}.")])

    if receipt["outcome"] == "interrupted":
        if adapter_session is not None:
            adapter.close_session(adapter_session)
        return _result("interrupted", selected_id, started.get("graph", {}), attempt=attempt, receipt=receipt)
    if receipt["outcome"] == "failed":
        findings = _repair_findings(receipt)
        retry = _graph("retry", task_dir, selected_id, {"expected_attempt": attempt, "baseline": _workspace_baseline(workspace_root), "existing_changes": current_existing, "allowed_write_scope": scope, "findings": findings})
        return _result("retry" if retry.get("ok") else "failed", selected_id, retry.get("graph", {}), attempt=attempt, receipt=receipt, problems=retry.get("problems", []))

    try:
        save_receipt(task_dir, receipt, ticket_id=selected_id, attempt=attempt, agent_instance_id=agent_instance_id)
    except (OSError, ValueError) as exc:
        if adapter_session is not None:
            adapter.close_session(adapter_session)
        return _result("failed", selected_id, started.get("graph", {}), attempt=attempt, receipt=receipt, problems=[_problem("receipt_artifact_failed", str(exc))])

    if commit_on_complete and receipt["outcome"] == "completed" and _completion_gate_problem(task_dir, started_ticket, receipt) is None:
        try:
            _commit_ticket_changes(workspace_root, started_ticket, changed, workspace_before_worker)
        except RuntimeError as exc:
            if adapter_session is not None:
                adapter.close_session(adapter_session)
            return _result("failed", selected_id, started.get("graph", {}), attempt=attempt, receipt=receipt, problems=[_problem("ticket_commit_failed", str(exc))])
    result = _apply_receipt(task_dir, started_ticket, started.get("graph", {}), receipt, attempt)
    if adapter_session is not None:
        adapter.close_session(adapter_session)
    return result


def _scope_is_valid(scope: object) -> bool:
    try:
        allowed_scope("implement", scope)  # type: ignore[arg-type]
    except ValueError:
        return False
    return True


__all__ = ["RuntimeResult", "dispatch_ready", "load_receipt", "load_receipt_artifact", "reopen_ticket", "run_ticket", "save_receipt"]
