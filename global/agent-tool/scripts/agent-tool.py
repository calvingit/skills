#!/usr/bin/env python3
"""One small, provider-neutral wrapper for interactive coding agents."""

from __future__ import annotations

import argparse
import codecs
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import selectors
import signal
import shutil
import subprocess
import sys
import time
import uuid


CLIS = ("claude", "codex", "kimi", "pi", "grok")
MODEL_DISCOVERY_COMMANDS = {
    "pi": ["pi", "--list-models"],
    "kimi": ["kimi", "provider", "list", "--json"],
    "grok": ["grok", "models"],
}
DEFAULT_HEARTBEAT_INTERVAL_SECONDS = 30.0
DEFAULT_IDLE_TIMEOUT_SECONDS = 600.0
STOP_GRACE_SECONDS = 1.0
OUTPUT_DRAIN_SECONDS = 1.0


def command(cli: str, prompt: str, *, workspace: Path, provider: str | None, model: str | None, session: str | None) -> list[str]:
    model_args = ["--model", model] if model else []
    if cli == "claude":
        return ["claude", "-p", "--output-format", "stream-json", "--dangerously-skip-permissions", *model_args, *( ["--resume", session] if session else ["--session-id", str(uuid.uuid4())]), prompt]
    if cli == "codex":
        base = ["codex", "exec"] + (["resume", session] if session else ["--cd", str(workspace)])
        return base + model_args + ["--json", "--dangerously-bypass-approvals-and-sandbox", prompt]
    if cli == "kimi":
        return ["kimi", "--output-format", "stream-json", *model_args, *( ["--session", session] if session else []), "-p", prompt]
    if cli == "pi":
        provider_args = ["--provider", provider] if provider else []
        return ["pi", "-p", "--mode", "json", "--approve", *provider_args, *model_args, *( ["--session", session] if session else ["--session-id", str(uuid.uuid4())]), prompt]
    return ["grok", "-p", *model_args, *( ["--resume", session] if session else ["--session-id", str(uuid.uuid4())]), prompt]


def emit(value: object, *, events: bool = False) -> int:
    print(json.dumps(value, ensure_ascii=False, indent=None if events else 2), flush=events)
    return 0


def emit_event(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False), flush=True)


def positive_seconds(value: str) -> float:
    try:
        seconds = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a number of seconds") from exc
    if not math.isfinite(seconds) or seconds <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return seconds


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agent-tool", description="统一调用 Claude Code、Codex、Kimi、Pi 或 Grok。")
    sub = parser.add_subparsers(dest="action", required=True)
    clis = sub.add_parser("clis")
    clis.set_defaults(func=lambda args: emit({"clis": list(CLIS), "available": [cli for cli in CLIS if shutil.which(cli)]}))
    models = sub.add_parser("models")
    models.add_argument("--cli", choices=CLIS, required=True)
    models.add_argument("--provider")
    models.add_argument("--model")
    models.set_defaults(func=_models)
    doctor = sub.add_parser("doctor")
    doctor.set_defaults(func=lambda args: emit({
        "available": [cli for cli in CLIS if shutil.which(cli)],
        "missing": [cli for cli in CLIS if not shutil.which(cli)],
        "model_discovery": {cli: cli in MODEL_DISCOVERY_COMMANDS for cli in CLIS},
    }))
    run = sub.add_parser("run")
    run.add_argument("--cli", choices=CLIS, required=True)
    run.add_argument("--provider")
    run.add_argument("--model")
    run.add_argument("--session")
    run.add_argument("--workspace", type=Path, default=Path.cwd())
    run.add_argument("--prompt", required=True)
    run.add_argument(
        "--timeout",
        type=positive_seconds,
        help="optional total provider execution budget in seconds (default: unlimited)",
    )
    run.add_argument(
        "--idle-timeout",
        type=positive_seconds,
        default=DEFAULT_IDLE_TIMEOUT_SECONDS,
        help="maximum seconds without provider stdout/stderr activity (default: 600)",
    )
    run.add_argument(
        "--heartbeat-interval",
        type=positive_seconds,
        default=DEFAULT_HEARTBEAT_INTERVAL_SECONDS,
        help="observation event interval in seconds (default: 30)",
    )
    run.add_argument(
        "--events",
        action="store_true",
        help="emit live NDJSON start, output, and heartbeat events before the final result",
    )
    run.set_defaults(func=_run)
    args = parser.parse_args(argv)
    return args.func(args)


def _run(args: argparse.Namespace) -> int:
    workspace = args.workspace.resolve()
    if not workspace.is_dir():
        return emit(_failure(args, f"workspace directory is unavailable: {workspace}"), events=args.events)
    executable = shutil.which(args.cli)
    if executable is None:
        return emit(_failure(args, "cli executable is unavailable"), events=args.events)
    validation_error = _validate_selection(args.cli, args.provider, args.model)
    if validation_error:
        return emit(_failure(args, validation_error), events=args.events)

    started_wall = datetime.now(timezone.utc)
    started = time.monotonic()
    process_options = {
        "cwd": workspace,
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "start_new_session": os.name != "nt",
    }
    try:
        process = subprocess.Popen(
            command(args.cli, args.prompt, workspace=workspace, provider=args.provider, model=args.model, session=args.session),
            **process_options,
        )
    except OSError as exc:
        result = _failure(args, str(exc))
        result["outcome"] = "failed"
        return emit(result, events=args.events)

    if args.events:
        emit_event({
            "event": "started",
            "cli": args.cli,
            "provider": args.provider,
            "model": args.model,
            "heartbeat_mode": "process-observation",
            "timeout_seconds": args.timeout,
            "idle_timeout_seconds": args.idle_timeout,
            "heartbeat_interval_seconds": args.heartbeat_interval,
            "started_at": started_wall.isoformat(),
        })

    selector = selectors.DefaultSelector()
    output = {"stdout": bytearray(), "stderr": bytearray()}
    decoders = {name: codecs.getincrementaldecoder("utf-8")(errors="replace") for name in output}
    for name, stream in (("stdout", process.stdout), ("stderr", process.stderr)):
        assert stream is not None
        selector.register(stream, selectors.EVENT_READ, name)

    last_output = started
    next_heartbeat = started + args.heartbeat_interval
    heartbeat_count = 0
    timeout_reason = None
    drain_deadline = None
    try:
        while process.poll() is None or selector.get_map():
            now = time.monotonic()
            if drain_deadline is not None and time.monotonic() >= drain_deadline:
                break

            wait_for = 0.1
            if timeout_reason is None:
                wait_for = min(wait_for, max(0.0, last_output + args.idle_timeout - now))
                if args.timeout is not None:
                    wait_for = min(wait_for, max(0.0, started + args.timeout - now))
            if args.events and process.poll() is None:
                wait_for = min(wait_for, max(0.0, next_heartbeat - now))
            if process.poll() is not None:
                wait_for = min(wait_for, 0.05)
            events = selector.select(wait_for)
            for key, _ in events:
                chunk = os.read(key.fileobj.fileno(), 65536)
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                stream_name = key.data
                output[stream_name].extend(chunk)
                last_output = time.monotonic()
                if args.events:
                    data = decoders[stream_name].decode(chunk)
                    if data:
                        emit_event({"event": "output", "stream": stream_name, "data": data})

            now = time.monotonic()
            # Read ready output before deciding that the provider has been idle.
            if timeout_reason is None and (process.poll() is None or selector.get_map()):
                if args.timeout is not None and now - started >= args.timeout:
                    timeout_reason = "provider timeout"
                elif now - last_output >= args.idle_timeout:
                    timeout_reason = "provider idle timeout"
                if timeout_reason is not None:
                    _stop_process(process)
                    drain_deadline = time.monotonic() + OUTPUT_DRAIN_SECONDS

            if args.events and timeout_reason is None and process.poll() is None and now >= next_heartbeat:
                heartbeat_count += 1
                emit_event({
                    "event": "heartbeat",
                    "cli": args.cli,
                    "provider": args.provider,
                    "model": args.model,
                    "process_alive": True,
                    "elapsed_seconds": round(now - started, 3),
                    "last_output_age_seconds": round(now - last_output, 3),
                    "heartbeat_number": heartbeat_count,
                })
                while next_heartbeat <= now:
                    next_heartbeat += args.heartbeat_interval
    finally:
        selector.close()
        for stream in (process.stdout, process.stderr):
            if stream is not None:
                stream.close()

    if args.events:
        for name, decoder in decoders.items():
            data = decoder.decode(b"", final=True)
            if data:
                emit_event({"event": "output", "stream": name, "data": data})

    returncode = process.wait()
    duration = time.monotonic() - started
    result = {
        "outcome": "interrupted" if timeout_reason is not None else ("completed" if returncode == 0 else "failed"),
        "cli": args.cli,
        "provider": args.provider,
        "model": args.model,
        "exit_code": returncode,
        "stdout": _text(bytes(output["stdout"])),
        "stderr": _text(bytes(output["stderr"])),
        "heartbeat": {
            "mode": "process-observation",
            "interval_seconds": args.heartbeat_interval,
            "timeout_seconds": args.timeout,
            "idle_timeout_seconds": args.idle_timeout,
            "observed_seconds": round(duration, 3),
            "heartbeat_events": heartbeat_count,
            "last_output_age_seconds": round(max(0.0, duration - (last_output - started)), 3),
        },
    }
    if timeout_reason is not None:
        result["reason"] = timeout_reason
    return emit(result, events=args.events)


def _models(args: argparse.Namespace) -> int:
    if shutil.which(args.cli) is None:
        return emit({"outcome": "blocked", "cli": args.cli, "reason": "cli executable is unavailable"})
    models, error = discover_models(args.cli)
    if error:
        return emit({"outcome": "blocked", "cli": args.cli, "reason": error})
    matches = [item for item in models if (not args.provider or item["provider"] == args.provider) and (not args.model or item["model"] == args.model)]
    return emit({"outcome": "completed", "cli": args.cli, "provider": args.provider, "model": args.model, "models": matches})


def _failure(args: argparse.Namespace, reason: str) -> dict[str, object]:
    return {"outcome": "blocked", "cli": args.cli, "provider": args.provider, "model": args.model, "reason": reason}


def _validate_selection(cli: str, provider: str | None, model: str | None) -> str | None:
    if provider and cli not in ("pi", "kimi"):
        return f"cli {cli} does not support provider selection"
    if not provider and not model:
        return None
    models, error = discover_models(cli)
    if error:
        return error
    if provider and not any(item["provider"] == provider for item in models):
        return f"provider {provider} is unavailable for cli {cli}"
    if model and not any(item["model"] == model and (not provider or item["provider"] == provider) for item in models):
        suffix = f" from provider {provider}" if provider else ""
        return f"model {model}{suffix} is unavailable for cli {cli}"
    return None


def discover_models(cli: str) -> tuple[list[dict[str, str]], str | None]:
    if cli not in MODEL_DISCOVERY_COMMANDS:
        return [], f"model discovery is unsupported for cli {cli}"
    try:
        result = subprocess.run(MODEL_DISCOVERY_COMMANDS[cli], capture_output=True, text=True, check=False)
    except OSError as exc:
        return [], f"model discovery failed for cli {cli}: {exc}"
    if result.returncode != 0:
        detail = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else "unknown error"
        return [], f"model discovery failed for cli {cli}: {detail}"
    try:
        if cli == "pi":
            models = []
            for line in result.stdout.splitlines()[1:]:
                columns = line.split()
                if len(columns) >= 2:
                    models.append({"provider": columns[0], "model": columns[1]})
            return models, None
        if cli == "kimi":
            data = json.loads(result.stdout)
            return [
                {"provider": value["provider"], "model": name}
                for name, value in data.get("models", {}).items()
                if isinstance(value, dict) and isinstance(value.get("provider"), str)
            ], None
        models = []
        for line in result.stdout.splitlines():
            stripped = line.strip()
            if stripped.startswith(("- ", "* ")):
                models.append({"provider": "xai", "model": stripped[2:].split(" ", 1)[0]})
        return models, None
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        return [], f"invalid model list from cli {cli}: {exc}"


def _stop_process(process: subprocess.Popen[bytes]) -> None:
    """Stop the provider and its children without leaving overlapping work."""
    if os.name == "nt":
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=STOP_GRACE_SECONDS)
            except subprocess.TimeoutExpired:
                process.kill()
        return

    # The group can outlive its leader and keep the output pipes open.
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    deadline = time.monotonic() + STOP_GRACE_SECONDS
    while time.monotonic() < deadline:
        process.poll()  # Reap the leader before checking whether the group remains.
        try:
            os.killpg(process.pid, 0)
        except ProcessLookupError:
            return
        time.sleep(min(0.02, max(0.0, deadline - time.monotonic())))
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def _text(value: object) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value if isinstance(value, str) else ""


if __name__ == "__main__":
    sys.exit(main())
