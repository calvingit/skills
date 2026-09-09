#!/usr/bin/env python3
"""One small, provider-neutral wrapper for interactive coding agents."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import uuid


PROVIDERS = ("claude", "codex", "kimi", "pi", "grok")


def command(provider: str, prompt: str, *, workspace: Path, model: str | None, session: str | None) -> list[str]:
    model_args = ["--model", model] if model else []
    if provider == "claude":
        return ["claude", "-p", "--output-format", "stream-json", "--dangerously-skip-permissions", *model_args, *( ["--resume", session] if session else ["--session-id", str(uuid.uuid4())]), prompt]
    if provider == "codex":
        base = ["codex", "exec"] + (["resume", session] if session else ["--cd", str(workspace)])
        return base + model_args + ["--json", "--dangerously-bypass-approvals-and-sandbox", prompt]
    if provider == "kimi":
        return ["kimi", "--auto", "--output-format", "stream-json", *model_args, *( ["--session", session] if session else []), "-p", prompt]
    if provider == "pi":
        return ["pi", "-p", "--mode", "json", "--approve", *model_args, *( ["--session", session] if session else ["--session-id", str(uuid.uuid4())]), prompt]
    return ["grok", "-p", *model_args, *( ["--resume", session] if session else ["--session-id", str(uuid.uuid4())]), prompt]


def emit(value: object) -> int:
    print(json.dumps(value, ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agent-tool", description="统一调用 Claude Code、Codex、Kimi、Pi 或 Grok。")
    sub = parser.add_subparsers(dest="action", required=True)
    providers = sub.add_parser("providers")
    providers.set_defaults(func=lambda args: emit({"providers": list(PROVIDERS), "available": [p for p in PROVIDERS if shutil.which(p)]}))
    doctor = sub.add_parser("doctor")
    doctor.set_defaults(func=lambda args: emit({"available": [p for p in PROVIDERS if shutil.which(p)], "missing": [p for p in PROVIDERS if not shutil.which(p)]}))
    run = sub.add_parser("run")
    run.add_argument("--provider", choices=PROVIDERS, required=True)
    run.add_argument("--model")
    run.add_argument("--session")
    run.add_argument("--workspace", type=Path, default=Path.cwd())
    run.add_argument("--prompt", required=True)
    run.add_argument("--timeout", type=float)
    run.set_defaults(func=_run)
    args = parser.parse_args(argv)
    return args.func(args)


def _run(args: argparse.Namespace) -> int:
    workspace = args.workspace.resolve()
    if not workspace.is_dir():
        return emit({"outcome": "blocked", "provider": args.provider, "model": args.model, "reason": f"workspace directory is unavailable: {workspace}"})
    executable = shutil.which(args.provider)
    if executable is None:
        return emit({"outcome": "blocked", "provider": args.provider, "model": args.model, "reason": "provider executable is unavailable"})
    try:
        result = subprocess.run(
            command(args.provider, args.prompt, workspace=workspace, model=args.model, session=args.session),
            cwd=workspace,
            text=True,
            capture_output=True,
            timeout=args.timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return emit({"outcome": "interrupted", "provider": args.provider, "model": args.model, "reason": "provider timeout", "stdout": _text(exc.stdout), "stderr": _text(exc.stderr)})
    except OSError as exc:
        return emit({"outcome": "failed", "provider": args.provider, "model": args.model, "reason": str(exc)})
    return emit({"outcome": "completed" if result.returncode == 0 else "failed", "provider": args.provider, "model": args.model, "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr})


def _text(value: object) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value if isinstance(value, str) else ""


if __name__ == "__main__":
    sys.exit(main())
