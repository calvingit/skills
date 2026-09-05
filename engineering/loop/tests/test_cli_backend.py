from __future__ import annotations

import tempfile
import time
import unittest
from pathlib import Path

from engineering.loop.scripts.cli_backend import CliBackend


class CliBackendTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def command(self, provider: str, *, session: str | None = None) -> list[str]:
        backend = CliBackend(provider, workspace=self.root, session_dir=self.root / "sessions", executable="/bin/echo")
        handle = backend.create("implement", {})
        handle.session_ref = session
        handle.started = session is not None
        return backend.build_command(handle, "prompt")

    def test_provider_commands_use_explicit_full_access(self) -> None:
        claude = self.command("claude")
        codex = self.command("codex")
        kimi = self.command("kimi")
        pi = self.command("pi")

        self.assertIn("--dangerously-skip-permissions", claude)
        self.assertIn("bypassPermissions", claude)
        self.assertIn("--dangerously-bypass-approvals-and-sandbox", codex)
        self.assertIn("--auto", kimi)
        self.assertIn("--approve", pi)

        codex_backend = CliBackend("codex", workspace=self.root, session_dir=self.root / "sessions", executable="/bin/echo")
        codex_handle = codex_backend.create("implement", {})
        codex_handle.output_file = self.root / "last.json"
        self.assertIn("--output-last-message", codex_backend.build_command(codex_handle, "prompt"))

    def test_resume_commands_use_exact_session_without_last(self) -> None:
        for provider in ("claude", "codex", "kimi", "pi"):
            command = self.command(provider, session="session-1")
            self.assertIn("session-1", command)
            self.assertNotIn("--last", command)

    def test_claude_and_pi_initial_commands_create_sessions(self) -> None:
        for provider, initial_flag in (("claude", "--session-id"), ("pi", "--session-id")):
            backend = CliBackend(provider, workspace=self.root, session_dir=self.root / "sessions", executable="/bin/echo")
            handle = backend.create("implement", {})
            command = backend.build_command(handle, "prompt")
            self.assertIn(initial_flag, command)
            handle.started = True
            resumed = backend.build_command(handle, "repair")
            self.assertIn("--resume" if provider == "claude" else "--session", resumed)

    def test_cli_result_parser_accepts_normalized_result(self) -> None:
        result = CliBackend._parse_output(
            '{"type":"thread.started","thread_id":"thread-1"}\n'
            '{"outcome":"completed","payload":{"ok":true}}\n',
            "",
            0,
        )

        self.assertEqual(result, {"outcome": "completed", "payload": {"ok": True}})

    def test_cli_result_parser_rejects_success_without_result(self) -> None:
        result = CliBackend._parse_output("plain output\n", "", 0)

        self.assertEqual(result["outcome"], "failed")
        self.assertIn("normalized capability result", result["payload"]["reason"])

    def test_cli_raw_output_is_attached_to_task_local_artifact_payload(self) -> None:
        result = CliBackend._with_raw(
            {"outcome": "failed", "payload": {"reason": "provider failed"}},
            "full stdout",
            "full stderr",
            7,
        )

        self.assertEqual(
            result["payload"]["_cli_raw"],
            {"stdout": "full stdout", "stderr": "full stderr", "returncode": 7},
        )

    def test_wait_budget_is_optional_and_heartbeat_staleness_is_explicit(self) -> None:
        backend = CliBackend("pi", workspace=self.root, session_dir=self.root / "sessions", executable="/bin/echo")
        self.assertIsNone(backend.timeout)
        heartbeat = self.root / "heartbeat.json"
        heartbeat.write_text(
            '{"heartbeat_at":"1970-01-01T00:00:00+00:00","progress_at":"1970-01-01T00:00:00+00:00"}\n',
            encoding="utf-8",
        )
        monitored = CliBackend(
            "pi",
            workspace=self.root,
            session_dir=self.root / "sessions",
            executable="/bin/echo",
            heartbeat_file=heartbeat,
            heartbeat_timeout=1,
            progress_timeout=1,
        )

        self.assertEqual(monitored._stale_reason(time.monotonic()), "CLI heartbeat freshness expired.")

        command = monitored.build_command(monitored.create("implement", {}), "prompt")
        self.assertIn("--extension", command)
        self.assertTrue(any("heartbeat.js" in item for item in command))

    def test_progress_staleness_is_checked_without_heartbeat_timestamp(self) -> None:
        heartbeat = self.root / "heartbeat.json"
        heartbeat.write_text('{"progress_at":"1970-01-01T00:00:00+00:00"}\n', encoding="utf-8")
        backend = CliBackend("pi", heartbeat_file=heartbeat, progress_timeout=1, executable="/bin/echo")

        self.assertEqual(backend._stale_reason(time.monotonic()), "CLI progress freshness expired.")

    def test_progress_timeout_does_not_require_heartbeat_timeout(self) -> None:
        heartbeat = self.root / "heartbeat.json"
        heartbeat.write_text(
            '{"progress_at":"1970-01-01T00:00:00+00:00"}\n', encoding="utf-8"
        )
        backend = CliBackend("pi", heartbeat_file=heartbeat, progress_timeout=1, executable="/bin/echo")

        self.assertEqual(backend._stale_reason(time.monotonic()), "CLI progress freshness expired.")

    def test_missing_heartbeat_is_stale_when_freshness_is_requested(self) -> None:
        backend = CliBackend(
            "pi",
            heartbeat_file=self.root / "missing-heartbeat.json",
            heartbeat_timeout=1,
            executable="/bin/echo",
        )

        self.assertEqual(backend._stale_reason(time.monotonic()), "CLI heartbeat is invalid or unreadable.")


if __name__ == "__main__":
    unittest.main()
