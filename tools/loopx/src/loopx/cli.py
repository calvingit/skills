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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="loopx", description="Ticket state and delivery progress helpers.")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("version", help="Print the loopx version.")

    graph = commands.add_parser("graph", help="Inspect and mutate execution graphs.")
    graph.add_argument("args", nargs=argparse.REMAINDER)

    loop = commands.add_parser("loop", help="Inspect and record task progress.")
    loop_commands = loop.add_subparsers(dest="loop_command", required=True)
    loop_status = loop_commands.add_parser("status", help="Inspect graph and execution status.")
    loop_status.add_argument("task_dir")
    review_prepare = loop_commands.add_parser("delivery-prepare", help="Pin the final workspace and current task contract for whole-delivery review.")
    review_prepare.add_argument("task_dir")
    review_prepare.add_argument("--workspace", default=".")
    review_complete = loop_commands.add_parser("delivery-complete", help="Accept verify/review evidence for the prepared final snapshot.")
    review_complete.add_argument("task_dir")
    review_complete.add_argument("--input", required=True)

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
