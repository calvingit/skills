from __future__ import annotations

import argparse
import contextlib
import io
import json
import subprocess
from pathlib import Path
from typing import Any

from . import __version__
from . import delivery
from .graph.execution_graph.cli import main as graph_main
from .cli_backend import BackendUnavailable, CliBackend
from .loop_runtime import _git_metadata_fingerprint, _snapshot_changed, _workspace_snapshot, run_ticket
from .scope_guard import allowed_scope, violations as scope_violations
from .worker.routing import PROVIDERS, available_providers, select_provider
from .worker.artifacts import save as save_worker_artifact


def _emit(value: dict[str, Any]) -> int:
    print(json.dumps(value, ensure_ascii=False, indent=2))
    return 0 if value.get("ok", False) else 1


def _graph_command(arguments: list[str], *, command_name: str | None = None) -> int:
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        code = graph_main(arguments)
    try:
        payload = json.loads(output.getvalue())
    except json.JSONDecodeError:
        return _emit({"version": 1, "ok": False, "command": "graph", "result": {}, "problems": [{"category": "runtime", "code": "invalid_graph_output", "detail": output.getvalue()}]})
    operation = arguments[0] if arguments else "unknown"
    if command_name == "loop.status":
        payload.setdefault("result", {})["delivery_review"] = delivery.status(Path(arguments[1]))
    wrapped = {"version": 1, "ok": bool(payload.get("ok")), "command": command_name or f"graph.{operation}", "result": payload.get("result", {}), "graph": payload.get("graph", {}), "problems": payload.get("problems", [])}
    print(json.dumps(wrapped, ensure_ascii=False, indent=2))
    return code


def _graph_help(operation: str) -> int:
    usage = {
        "inspect": "loopx graph inspect <task-dir>",
        "list": "loopx graph list <task-dir> [--phase <phase>] [--readiness <ready|blocked>]",
        "show": "loopx graph show <task-dir> <ticket-id>",
        "start": "loopx graph start <task-dir> <ticket-id> --input <path|->",
        "retry": "loopx graph retry <task-dir> <ticket-id> --input <path|->",
        "block": "loopx graph block <task-dir> <ticket-id> --input <path|->",
        "unblock": "loopx graph unblock <task-dir> <ticket-id> --input <path|->",
        "complete": "loopx graph complete <task-dir> <ticket-id> --input <path|->",
        "reopen": "loopx graph reopen <task-dir> <ticket-id> --input <path|->",
        "create-batch": "loopx graph create-batch <task-dir> --input <path|->",
        "reconcile-batch": "loopx graph reconcile-batch <task-dir> --input <path|->",
        "recover": "loopx graph recover <task-dir> <rollback|commit>",
    }.get(operation, f"loopx graph {operation} ...")
    print(f"usage: {usage}")
    return 0


def _worker(args: argparse.Namespace) -> int:
    if args.worker_command == "providers":
        return _emit({"version": 1, "ok": True, "command": "worker.providers", "result": {"supported": list(PROVIDERS), "available": available_providers()}, "problems": []})
    if args.worker_command == "doctor":
        available = available_providers()
        return _emit({"version": 1, "ok": bool(available), "command": "worker.doctor", "result": {"available": available}, "problems": [] if available else [{"category": "provider", "code": "none_available", "detail": "No supported provider executable is available."}]})
    if args.worker_command != "run":
        return 2
    if not args.prompt.strip():
        return _emit({"version": 1, "ok": False, "command": "worker.run", "result": {"outcome": "failed", "agent_instance_id": None, "selected_provider": None, "model": args.model, "routing_reason": "prompt validation failed", "available_providers": [], "payload": {}, "artifact": None}, "problems": [{"category": "contract", "code": "prompt_required", "detail": "worker requires a non-empty prompt."}]})
    try:
        selected, reason, available = select_provider(args.provider)
    except ValueError as exc:
        return _emit({"version": 1, "ok": False, "command": "worker.run", "result": {"outcome": "failed", "agent_instance_id": None, "selected_provider": None, "model": args.model, "routing_reason": "invalid runtime provider configuration", "available_providers": [], "payload": {}, "artifact": None}, "problems": [{"category": "contract", "code": "invalid_runtime_provider", "detail": str(exc)}]})
    workspace = Path(args.task_dir).resolve()
    if not workspace.is_dir():
        return _emit({"version": 1, "ok": False, "command": "worker.run", "result": {"outcome": "failed", "agent_instance_id": None, "selected_provider": selected, "model": args.model, "routing_reason": reason, "available_providers": available, "payload": {}, "artifact": None}, "problems": [{"category": "workspace", "code": "workspace_invalid", "detail": f"Workspace directory does not exist: {workspace}"}]})
    if selected is None:
        return _emit({"version": 1, "ok": False, "command": "worker.run", "result": {"outcome": "blocked", "agent_instance_id": None, "selected_provider": None, "model": args.model, "routing_reason": reason, "available_providers": available, "payload": {}, "artifact": None}, "problems": [{"category": "provider", "code": "unavailable", "detail": reason}]})
    try:
        before = _workspace_snapshot(workspace)
        metadata_before = _git_metadata_fingerprint(workspace)
        if before is None or metadata_before is None:
            return _emit({"version": 1, "ok": False, "command": "worker.run", "result": {"outcome": "failed", "agent_instance_id": None, "selected_provider": selected, "model": args.model, "routing_reason": reason, "available_providers": available, "payload": {}, "artifact": None}, "problems": [{"category": "workspace", "code": "workspace_probe_unavailable", "detail": "Worker requires a Git workspace with a complete status probe."}]})
        scope = allowed_scope("implement" if args.scope else "review", args.scope)
        backend = CliBackend(selected, workspace=workspace)
        handle = backend.create("worker", {"model": args.model, "prompt_mode": True})
        backend.send(handle, {"prompt": args.prompt, "model": args.model, "prompt_mode": True, "allowed_write_scope": scope})
        raw = backend.wait(handle)
    except (BackendUnavailable, OSError, RuntimeError, ValueError, KeyboardInterrupt) as exc:
        interrupted = isinstance(exc, KeyboardInterrupt)
        failed = {"outcome": "interrupted" if interrupted else "failed", "agent_instance_id": handle.agent_instance_id if "handle" in locals() else None, "selected_provider": selected, "model": args.model, "routing_reason": reason, "available_providers": available, "payload": {"failure_category": "runtime" if interrupted else "provider", "reason": str(exc)}, "artifact": None}
        if "handle" in locals() and handle.cleanup_error:
            failed["cleanup_warning"] = handle.cleanup_error
        problems = [{"category": "runtime" if interrupted else "provider", "code": "interrupted" if interrupted else "execution_failed", "detail": str(exc) or ("Worker interrupted by user." if interrupted else "Provider execution failed.")}]
        try:
            failed["artifact"] = str(save_worker_artifact(workspace, result=failed, stdout="", stderr=str(exc), returncode=None))
        except OSError as artifact_exc:
            problems.append({"category": "storage", "code": "artifact_write_failed", "detail": str(artifact_exc)})
        return _emit({"version": 1, "ok": False, "command": "worker.run", "result": failed, "problems": problems})
    finally:
        if "handle" in locals():
            backend.close(handle)
    after = _workspace_snapshot(workspace)
    guard_problems = []
    if after is None:
        guard_problems.append({"category": "workspace", "code": "workspace_probe_unavailable", "detail": "Worker workspace could not be rechecked."})
    else:
        violations = scope_violations("implement" if scope else "review", scope, sorted(_snapshot_changed(before, after)))
        if violations:
            guard_problems.append({"category": "scope", "code": "write_scope_violation", "detail": ", ".join(violations)})
    if _git_metadata_fingerprint(workspace) != metadata_before:
        guard_problems.append({"category": "scope", "code": "git_state_violation", "detail": "Worker changed Git state."})
    payload = raw.get("payload", {})
    raw_meta = payload.get("_cli_raw", {}) if isinstance(payload, dict) else {}
    public_payload = {key: value for key, value in payload.items() if key not in {"_cli_raw", "stdout", "stderr"}} if isinstance(payload, dict) else {}
    result = {"outcome": "failed" if guard_problems else raw.get("outcome", "failed"), "agent_instance_id": handle.agent_instance_id, "selected_provider": selected, "model": args.model, "routing_reason": reason, "available_providers": available, "payload": public_payload, "artifact": None}
    if handle.cleanup_error:
        result["cleanup_warning"] = handle.cleanup_error
    try:
        result["artifact"] = str(save_worker_artifact(Path(args.task_dir).resolve(), result=result, stdout=raw_meta.get("stdout", ""), stderr=raw_meta.get("stderr", ""), returncode=raw_meta.get("returncode")))
    except OSError as exc:
        return _emit({"version": 1, "ok": False, "command": "worker.run", "result": result, "problems": [{"category": "storage", "code": "artifact_write_failed", "detail": str(exc)}]})
    return _emit({"version": 1, "ok": result["outcome"] == "completed", "command": "worker.run", "result": result, "problems": guard_problems or ([] if result["outcome"] == "completed" else [{"category": "provider", "code": "worker_failed", "detail": "Provider did not complete the prompt."}])})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="loopx", description="Shared engineering workflow and worker CLI.")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("version", help="Print the loopx version.")

    graph = commands.add_parser("graph", help="Inspect and mutate execution graphs.")
    graph.add_argument("args", nargs=argparse.REMAINDER)

    loop = commands.add_parser("loop", help="Run Loop orchestration.")
    loop_commands = loop.add_subparsers(dest="loop_command", required=True)
    loop_run = loop_commands.add_parser("run", help="Run the Loop pipeline for a task directory.")
    loop_run.add_argument("task_dir")
    loop_run.add_argument("--provider", choices=PROVIDERS)
    loop_run.add_argument("--scope", action="append", required=True)
    loop_run.add_argument("--ticket", help="Explicit ticket to run or resume.")
    loop_status = loop_commands.add_parser("status", help="Inspect graph and execution status.")
    loop_status.add_argument("task_dir")
    review_prepare = loop_commands.add_parser("delivery-prepare", help="Pin the final workspace and current task contract for whole-delivery review.")
    review_prepare.add_argument("task_dir")
    review_prepare.add_argument("--workspace", default=".")
    review_complete = loop_commands.add_parser("delivery-complete", help="Accept verify/review evidence for the prepared final snapshot.")
    review_complete.add_argument("task_dir")
    review_complete.add_argument("--input", required=True)

    worker = commands.add_parser("worker", help="Run an external prompt in a selected runtime.")
    worker_commands = worker.add_subparsers(dest="worker_command", required=True)
    run = worker_commands.add_parser("run", help="Run an external prompt.", description="Run an external prompt in the selected runtime.")
    run.add_argument("task_dir", nargs="?", default=".")
    run.add_argument("--prompt", required=True)
    run.add_argument("--model")
    run.add_argument("--provider", choices=PROVIDERS)
    run.add_argument("--scope", action="append", default=[])
    worker_commands.add_parser("providers", help="List supported and available providers.")
    worker_commands.add_parser("doctor", help="Check provider availability.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "version":
        return _emit({"version": 1, "ok": True, "command": "version", "result": {"version": __version__}, "problems": []})
    if args.command == "graph":
        if not args.args:
            return _graph_command(["unknown"])
        if args.args[0] in {"--help", "-h"}:
            parser.parse_args(["graph", "--help"])
        if len(args.args) > 1 and args.args[1] in {"--help", "-h"}:
            return _graph_help(args.args[0])
        return _graph_command(args.args)
    if args.command == "worker":
        return _worker(args)
    if args.loop_command in {"delivery-prepare", "delivery-complete"}:
        try:
            if args.loop_command == "delivery-prepare":
                result = delivery.prepare(Path(args.task_dir), Path(args.workspace))
            else:
                result = delivery.complete(Path(args.task_dir), json.loads(Path(args.input).read_text()))
            return _emit({"version": 1, "ok": True, "command": args.loop_command, "result": result, "problems": []})
        except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as exc:
            return _emit({"version": 1, "ok": False, "command": args.loop_command, "result": {}, "problems": [{"category": "delivery", "code": "delivery_not_accepted", "detail": str(exc)}]})
    if args.loop_command == "status":
        return _graph_command(["inspect", args.task_dir], command_name="loop.status")
    try:
        selected, reason, available = select_provider(args.provider)
    except ValueError as exc:
        return _emit({"version": 1, "ok": False, "command": "loop.run", "result": {}, "problems": [{"category": "contract", "code": "invalid_runtime_provider", "detail": str(exc)}]})
    if selected is None:
        return _emit({"version": 1, "ok": False, "command": "loop.run", "result": {}, "problems": [{"category": "provider", "code": "unavailable", "detail": reason}]})
    result = run_ticket(Path(args.task_dir), provider=selected, allowed_write_scope=args.scope, ticket_id=args.ticket)
    return _emit({"version": 1, "ok": result.outcome == "completed", "command": "loop.run", "result": {**result.as_dict(), "selected_provider": selected, "model": None, "routing_reason": reason, "available_providers": available}, "problems": list(result.problems)})
