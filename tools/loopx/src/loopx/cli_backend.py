"""Headless CLI backends for Loop capability sessions."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import time
from typing import Any
from uuid import uuid4

PROVIDERS = ("codex", "claude", "kimi", "pi")
OUTCOMES = {"completed", "blocked", "failed", "interrupted"}


class BackendUnavailable(RuntimeError):
    """The selected CLI is not installed or cannot be started."""


@dataclass(eq=False)
class CliHandle:
    provider: str
    capability: str
    agent_instance_id: str
    session_ref: str | None = None
    model: str | None = None
    prompt_mode: bool = False
    cleanup_error: str | None = None
    started: bool = False
    output_file: Path | None = field(default=None, compare=False)
    process: subprocess.Popen[str] | None = field(default=None, compare=False)


class CliBackend:
    """Run one provider CLI with explicit session resume and full access."""

    def __init__(
        self,
        provider: str = "codex",
        *,
        workspace: Path | None = None,
        session_dir: Path | None = None,
        timeout: float | None = None,
        heartbeat_file: Path | None = None,
        heartbeat_timeout: float | None = None,
        progress_timeout: float | None = None,
        poll_interval: float = 1.0,
        executable: str | None = None,
    ) -> None:
        if provider not in PROVIDERS:
            raise ValueError(f"Unsupported CLI provider: {provider}")
        self.provider = provider
        self.workspace = (workspace or Path.cwd()).resolve()
        self.session_dir = (session_dir or Path(tempfile.gettempdir()) / "loop-cli-sessions").resolve()
        self.timeout = timeout
        self.heartbeat_file = heartbeat_file.resolve() if heartbeat_file else None
        self.heartbeat_timeout = heartbeat_timeout
        self.progress_timeout = progress_timeout
        self.poll_interval = max(0.1, poll_interval)
        self.executable = executable or provider

    def create(self, capability: str, bundle: dict[str, Any]) -> CliHandle:
        if not self.available():
            raise BackendUnavailable(f"CLI executable is unavailable: {self.executable}")
        session_ref = str(uuid4()) if self.provider in {"claude", "pi"} else None
        return CliHandle(self.provider, capability, uuid4().hex, session_ref=session_ref, model=bundle.get("model"), prompt_mode=bundle.get("prompt_mode", False))

    def available(self) -> bool:
        executable = shutil.which(self.executable) if os.path.sep not in self.executable else self.executable
        return executable is not None and Path(executable).exists()

    def build_command(self, handle: CliHandle, prompt: str) -> list[str]:
        command: list[str]
        model = handle.model if hasattr(handle, "model") else None
        if self.provider == "claude":
            command = [
                self.executable,
                "-p",
                "--output-format",
                "stream-json",
                "--verbose",
                "--dangerously-skip-permissions",
                "--permission-mode",
                "bypassPermissions",
            ]
            if model:
                command.extend(["--model", model])
            if handle.started and handle.session_ref:
                command.extend(["--resume", handle.session_ref])
            else:
                handle.session_ref = str(uuid4())
                command.extend(["--session-id", handle.session_ref])
            command.append(prompt)
            return command
        if self.provider == "codex":
            output_arg = ["--output-last-message", str(handle.output_file)] if handle.output_file else []
            model_arg = ["--model", model] if model else []
            if handle.started and handle.session_ref:
                command = [self.executable, "exec", "resume", handle.session_ref]
                command.extend(output_arg + model_arg + ["--json", "--dangerously-bypass-approvals-and-sandbox", prompt])
            else:
                command = [self.executable, "exec"]
                command.extend(["--cd", str(self.workspace)] + output_arg + model_arg + ["--json", "--dangerously-bypass-approvals-and-sandbox", prompt])
            return command
        if self.provider == "kimi":
            command = [self.executable, "--auto", "--output-format", "stream-json"]
            if model:
                command.extend(["--model", model])
            if handle.started and handle.session_ref:
                command.extend(["--session", handle.session_ref])
            command.extend(["-p", prompt])
            return command

        self.session_dir.mkdir(parents=True, exist_ok=True)
        command = [
            self.executable,
            "-p",
            "--mode",
            "json",
            "--session-dir",
            str(self.session_dir),
            "--approve",
        ]
        if model:
            command.extend(["--model", model])
        if self.heartbeat_file is not None:
            heartbeat_extension = Path(__file__).parent / "providers" / "heartbeat.js"
            if heartbeat_extension.is_file():
                command.extend(["--extension", str(heartbeat_extension)])
        if handle.started and handle.session_ref:
            command.extend(["--session", handle.session_ref])
        else:
            handle.session_ref = str(uuid4())
            command.extend(["--session-id", handle.session_ref])
        command.append(prompt)
        return command

    def send(self, handle: CliHandle, bundle: dict[str, Any]) -> None:
        if handle.process is not None and handle.process.poll() is None:
            raise RuntimeError("CLI session already has a running turn")
        user_prompt = bundle.get("prompt")
        if not isinstance(user_prompt, str) or not user_prompt.strip():
            user_prompt = json.dumps(
            {
                "loop_handoff": bundle,
                "worker_rules": [
                    "Return one JSON capability result with outcome completed, blocked, failed, or interrupted.",
                    "Do not edit ticket JSON, SPEC.md, HLD.md, or sibling tickets.",
                    "Do not commit, push, create branches, or schedule other workers.",
                    "Only implement may write inside allowed_write_scope; verify and review are read-only.",
                ],
            },
                ensure_ascii=False,
            )
            prompt = user_prompt
        else:
            prompt = user_prompt + "\n\nRuntime constraints:\n- Return a result; structured JSON is preferred when practical, and plain text is accepted for prompt mode.\n- Do not modify ticket graph, SPEC.md, HLD.md, sibling tickets, or version history.\n- Do not commit, push, create branches, or schedule other workers."
        if self.provider == "codex":
            self.session_dir.mkdir(parents=True, exist_ok=True)
            handle.output_file = self.session_dir / f"{handle.agent_instance_id}.last-message.json"
        command = self.build_command(handle, prompt)
        handle.started = True
        environment = os.environ.copy()
        if self.provider == "pi" and self.heartbeat_file is not None:
            environment["PI_SKILLS_HEARTBEAT_FILE"] = str(self.heartbeat_file)
        handle.process = subprocess.Popen(
            command,
            cwd=self.workspace,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def wait(self, handle: CliHandle) -> dict[str, Any]:
        process = handle.process
        if process is None:
            raise RuntimeError("CLI session has no running turn")
        started_at = time.monotonic()
        while True:
            remaining = None if self.timeout is None else self.timeout - (time.monotonic() - started_at)
            if remaining is not None and remaining <= 0:
                self.interrupt(handle)
                stdout, stderr = self._collect_after_interrupt(handle)
                return self._with_raw(
                    {"outcome": "interrupted", "payload": {"reason": "CLI task budget expired."}},
                    stdout,
                    stderr,
                    process.returncode,
                )
            wait_for = self.poll_interval if remaining is None else min(self.poll_interval, remaining)
            try:
                stdout, stderr = process.communicate(timeout=wait_for)
                break
            except subprocess.TimeoutExpired:
                reason = self._stale_reason(started_at)
                if reason is not None:
                    self.interrupt(handle)
                    stdout, stderr = self._collect_after_interrupt(handle)
                    return self._with_raw(
                        {"outcome": "interrupted", "payload": {"reason": reason}},
                        stdout,
                        stderr,
                        process.returncode,
                    )
        handle.process = None
        if handle.output_file and handle.output_file.is_file():
            stdout = stdout + "\n" + handle.output_file.read_text(encoding="utf-8", errors="replace")
        result = self._with_raw(
            self._parse_output(stdout, stderr, process.returncode, allow_text=handle.prompt_mode),
            stdout,
            stderr,
            process.returncode,
        )
        if handle.session_ref is None:
            handle.session_ref = _session_ref_from_output(stdout)
        if not handle.prompt_mode and self.provider in {"codex", "kimi"} and not handle.session_ref:
            return self._with_raw(
                {
                    "outcome": "failed",
                    "payload": {
                        "failure_category": "environment",
                        "reason": f"{self.provider} did not expose an explicit session id.",
                    },
                },
                stdout,
                stderr,
                process.returncode,
            )
        return result

    def _collect_after_interrupt(self, handle: CliHandle) -> tuple[str, str]:
        process = handle.process
        if process is None:
            return "", ""
        try:
            stdout, stderr = process.communicate(timeout=2)
            handle.process = None
            return stdout, stderr
        except subprocess.TimeoutExpired:
            handle.cleanup_error = "Provider process did not close after interruption."
            return "", ""

    @staticmethod
    def _with_raw(result: dict[str, Any], stdout: str, stderr: str, returncode: int | None) -> dict[str, Any]:
        payload = result.setdefault("payload", {})
        if isinstance(payload, dict):
            payload["_cli_raw"] = {
                "stdout": stdout,
                "stderr": stderr,
                "returncode": returncode,
            }
        return result

    def _stale_reason(self, started_at: float) -> str | None:
        del started_at
        if (
            self.heartbeat_file is not None
            and (self.heartbeat_timeout is not None or self.progress_timeout is not None)
        ):
            if not self.heartbeat_file.is_file():
                return "CLI heartbeat is invalid or unreadable."
            try:
                heartbeat = json.loads(self.heartbeat_file.read_text(encoding="utf-8"))
                heartbeat_at = _heartbeat_timestamp(heartbeat.get("heartbeat_at"))
                if self.heartbeat_timeout is not None:
                    if heartbeat_at is None:
                        return "CLI heartbeat is invalid or unreadable."
                    if time.time() - heartbeat_at > self.heartbeat_timeout:
                        return "CLI heartbeat freshness expired."
                progress_at = _heartbeat_timestamp(heartbeat.get("progress_at"))
                if self.progress_timeout is not None:
                    if progress_at is None:
                        return "CLI heartbeat is invalid or unreadable."
                    if time.time() - progress_at > self.progress_timeout:
                        return "CLI progress freshness expired."
            except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError):
                return "CLI heartbeat is invalid or unreadable."
        return None

    def interrupt(self, handle: CliHandle) -> None:
        process = handle.process
        if process is None or process.poll() is not None:
            return
        try:
            process.send_signal(signal.SIGINT)
            process.wait(timeout=2)
        except (OSError, subprocess.TimeoutExpired):
            try:
                process.kill()
            except OSError:
                pass
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                handle.cleanup_error = "Provider process did not exit after kill."

    def close(self, handle: CliHandle) -> None:
        self.interrupt(handle)
        if handle.process is None or handle.process.poll() is not None:
            handle.process = None

    @staticmethod
    def _parse_output(stdout: str, stderr: str, returncode: int | None, *, allow_text: bool = False) -> dict[str, Any]:
        if returncode not in {0, None}:
            return {
                "outcome": "failed",
                "payload": {
                    "failure_category": "environment",
                    "reason": f"CLI exited with status {returncode}.",
                    "stdout": stdout[-2000:],
                    "stderr": stderr[-2000:],
                },
            }
        events: list[dict[str, Any]] = []
        try:
            value = json.loads(stdout)
        except json.JSONDecodeError:
            value = None
        if isinstance(value, dict):
            events.append(value)
        else:
            for line in stdout.splitlines():
                try:
                    value = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(value, dict):
                    events.append(value)
        for event in reversed(events):
            outcome = event.get("outcome")
            payload = event.get("payload")
            if outcome in OUTCOMES and isinstance(payload, dict):
                return {"outcome": outcome, "payload": payload}
            if outcome in OUTCOMES:
                return {"outcome": outcome, "payload": event}
            if event.get("schema_version") == 1 and event.get("outcome") in OUTCOMES:
                return {"outcome": event["outcome"], "payload": event}
            for key in ("result", "message", "text"):
                value = event.get(key)
                if isinstance(value, str):
                    try:
                        decoded = json.loads(value)
                    except json.JSONDecodeError:
                        continue
                    if isinstance(decoded, dict) and decoded.get("outcome") in OUTCOMES:
                        return {"outcome": decoded["outcome"], "payload": decoded.get("payload", decoded)}
            decoded = _find_normalized_value(event)
            if decoded is not None:
                return {"outcome": decoded["outcome"], "payload": decoded.get("payload", decoded)}
        if allow_text and stdout.strip():
            return {"outcome": "completed", "payload": {"text": stdout}}
        return {
            "outcome": "failed",
            "payload": {
                "failure_category": "environment",
                "reason": "CLI completed without a normalized capability result.",
                "stdout": stdout[-4000:],
            },
        }


def _session_ref_from_output(stdout: str) -> str | None:
    for line in stdout.splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(value, dict):
            continue
        if value.get("type") not in {"session.started", "thread.started", "session_start", "thread_start"}:
            continue
        for key in ("session_id", "sessionId", "thread_id", "threadId", "id"):
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate:
                return candidate
    return None


def _heartbeat_timestamp(value: object) -> float | None:
    if not isinstance(value, str):
        return None
    from datetime import datetime

    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def _find_normalized_value(value: object) -> dict[str, Any] | None:
    if isinstance(value, dict):
        if value.get("outcome") in OUTCOMES:
            return value
        for child in value.values():
            found = _find_normalized_value(child)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _find_normalized_value(child)
            if found is not None:
                return found
    elif isinstance(value, str):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError:
            return None
        return _find_normalized_value(decoded)
    return None


__all__ = ["BackendUnavailable", "CliBackend", "CliHandle", "PROVIDERS"]
