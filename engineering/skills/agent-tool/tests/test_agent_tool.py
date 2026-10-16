from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import shlex
import signal
import subprocess
import sys
import time
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "agent-tool.py"
SPEC = importlib.util.spec_from_file_location("agent_tool", SCRIPT)
assert SPEC and SPEC.loader
agent_tool = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(agent_tool)


class AgentToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()
        self.old_path = os.environ.get("PATH")

    def tearDown(self) -> None:
        if self.old_path is None:
            os.environ.pop("PATH", None)
        else:
            os.environ["PATH"] = self.old_path
        self.temp.cleanup()

    def provider(self, script: str) -> None:
        path = self.bin / "codex"
        path.write_text("#!/bin/sh\n" + script)
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        system_path = self.old_path or "/usr/bin:/bin"
        os.environ["PATH"] = str(self.bin) + os.pathsep + system_path

    def invoke(self, *args: str) -> tuple[int, str]:
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            code = agent_tool.main(["run", "--cli", "codex", "--workspace", str(self.workspace), "--prompt", "test", *args])
        return code, stream.getvalue()

    def test_default_run_has_idle_limit_but_no_total_limit(self) -> None:
        self.provider("printf 'hello\\n'\n")
        code, output = self.invoke("--heartbeat-interval", "0.05")
        self.assertEqual(code, 0)
        result = json.loads(output)
        self.assertEqual(result["outcome"], "completed")
        self.assertEqual(result["stdout"], "hello\n")
        self.assertIsNone(result["heartbeat"]["timeout_seconds"])
        self.assertEqual(result["heartbeat"]["mode"], "process-observation")
        self.assertEqual(result["heartbeat"]["idle_timeout_seconds"], 600.0)

    def test_output_on_either_stream_renews_idle_budget_without_events(self) -> None:
        for fd, stream in ((1, "stdout"), (2, "stderr")):
            with self.subTest(stream=stream):
                self.python_provider(
                    "import os,time\n"
                    f"for _ in range(8): os.write({fd}, b'x'); time.sleep(0.2)\n"
                )
                _, output = self.invoke("--idle-timeout", "1")
                result = json.loads(output)
                self.assertEqual(result["outcome"], "completed")
                self.assertEqual(result[stream], "xxxxxxxx")
                self.assertGreater(result["heartbeat"]["observed_seconds"], 1)
                self.assertIsNone(result["heartbeat"]["timeout_seconds"])

    def test_idle_timeout_is_not_renewed_by_wrapper_heartbeats(self) -> None:
        self.python_provider("import time\nprint('ready', flush=True)\ntime.sleep(2)\n")
        _, output = self.invoke("--events", "--idle-timeout", "0.8", "--heartbeat-interval", "0.05")
        events = [json.loads(line) for line in output.splitlines()]
        result = events[-1]
        self.assertEqual(events[0]["idle_timeout_seconds"], 0.8)
        self.assertTrue(any(event.get("event") == "heartbeat" for event in events))
        self.assertEqual(result["outcome"], "interrupted")
        self.assertEqual(result["reason"], "provider idle timeout")
        self.assertEqual(result["stdout"], "ready\n")
        self.assertLess(result["heartbeat"]["observed_seconds"], 3)

    def test_silent_provider_idle_budget_starts_at_launch(self) -> None:
        self.python_provider("import time; time.sleep(2)")
        _, output = self.invoke("--idle-timeout", "0.2")
        result = json.loads(output)
        self.assertEqual(result["outcome"], "interrupted")
        self.assertEqual(result["reason"], "provider idle timeout")
        self.assertEqual(result["stdout"], "")

    def test_output_does_not_renew_explicit_total_budget(self) -> None:
        self.python_provider(
            "import os,time\n"
            "for _ in range(60): os.write(1, b'x'); time.sleep(0.05)\n"
        )
        _, output = self.invoke("--timeout", "1.5", "--idle-timeout", "1")
        result = json.loads(output)
        self.assertEqual(result["outcome"], "interrupted")
        self.assertEqual(result["reason"], "provider timeout")
        self.assertTrue(result["stdout"])

    def test_events_report_output_and_heartbeat_before_final_result(self) -> None:
        self.provider("printf 'started\\n'\nsleep 0.2\nprintf 'finished\\n'\n")
        code, output = self.invoke("--events", "--heartbeat-interval", "0.05", "--timeout", "2")
        self.assertEqual(code, 0)
        events = [json.loads(line) for line in output.splitlines()]
        self.assertEqual(events[0]["event"], "started")
        self.assertTrue(any(event.get("event") == "output" and event["stream"] == "stdout" for event in events))
        heartbeat = next(event for event in events if event.get("event") == "heartbeat" and event["process_alive"])
        self.assertEqual(heartbeat["cli"], "codex")
        self.assertIsNone(heartbeat["provider"])
        self.assertIsNone(heartbeat["model"])
        self.assertEqual(events[-1]["outcome"], "completed")
        self.assertEqual(events[-1]["stdout"], "started\nfinished\n")

    def test_timeout_stops_provider_and_preserves_partial_output(self) -> None:
        self.provider("printf 'before-timeout\\n'\nsleep 4\n")
        code, output = self.invoke("--timeout", "1.5", "--heartbeat-interval", "0.05")
        self.assertEqual(code, 0)
        result = json.loads(output)
        self.assertEqual(result["outcome"], "interrupted")
        self.assertEqual(result["reason"], "provider timeout")
        self.assertIn("before-timeout", result["stdout"])
        self.assertLess(result["heartbeat"]["observed_seconds"], 3)

    def test_nonzero_provider_exit_is_failed(self) -> None:
        self.provider("printf 'failure\\n' >&2\nexit 7\n")
        code, output = self.invoke("--timeout", "2")
        self.assertEqual(code, 0)
        result = json.loads(output)
        self.assertEqual(result["outcome"], "failed")
        self.assertEqual(result["exit_code"], 7)
        self.assertEqual(result["stderr"], "failure\n")

    def test_missing_provider_is_blocked_without_starting_a_process(self) -> None:
        os.environ["PATH"] = str(self.bin)
        code, output = self.invoke("--timeout", "1")
        self.assertEqual(code, 0)
        result = json.loads(output)
        self.assertEqual(result["outcome"], "blocked")
        self.assertIn("unavailable", result["reason"])

    def python_provider(self, source: str) -> None:
        self.provider("exec " + shlex.quote(sys.executable) + " -c " + shlex.quote(source))

    def test_events_preserve_split_utf8_on_both_streams_and_flush_at_eof(self) -> None:
        self.python_provider(
            "import os,time\n"
            "os.write(1, b'\\xe4'); os.write(2, b'\\xf0\\x9f')\n"
            "time.sleep(0.15)\n"
            "os.write(1, b'\\xb8\\xad'); os.write(2, b'\\x98\\x80\\xe4')\n"
        )
        _, output = self.invoke("--events", "--timeout", "2")
        events = [json.loads(line) for line in output.splitlines()]
        for stream, expected in (("stdout", "中"), ("stderr", "😀�")):
            with self.subTest(stream=stream):
                streamed = "".join(event["data"] for event in events
                                   if event.get("event") == "output" and event["stream"] == stream)
                self.assertEqual(streamed, expected)
                self.assertEqual(events[-1][stream], expected)

    def test_events_use_ndjson_for_all_startup_failures(self) -> None:
        for failure in ("workspace", "missing_provider", "spawn"):
            with self.subTest(failure=failure):
                self.provider("exit 0\n")
                args = ["--events"]
                if failure == "workspace":
                    args += ["--workspace", str(self.root / "missing")]
                elif failure == "missing_provider":
                    (self.bin / "codex").unlink()
                    os.environ["PATH"] = str(self.bin)
                with mock.patch.object(agent_tool.subprocess, "Popen", side_effect=OSError("spawn failed")) as spawn:
                    _, output = self.invoke(*args)
                events = [json.loads(line) for line in output.splitlines()]
                self.assertEqual(len(events), 1)
                self.assertEqual(events[0]["outcome"], "failed" if failure == "spawn" else "blocked")
                self.assertEqual(spawn.call_count, int(failure == "spawn"))

    @unittest.skipIf(os.name == "nt", "requires POSIX process groups")
    def test_timeout_kills_residual_group_even_after_leader_exit(self) -> None:
        for exit_early in (False, True):
            with self.subTest(exit_early=exit_early):
                pidfile = self.root / "child.pid"
                leaderfile = self.root / "leader.pid"
                child = (
                    "import os,signal,time,pathlib\n"
                    "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
                    f"pathlib.Path({str(pidfile)!r}).write_text(str(os.getpid()))\n"
                    "print('child-ready', flush=True)\n"
                    "time.sleep(30)\n"
                )
                self.python_provider(
                    "import os,subprocess,sys,time,pathlib\n"
                    f"pathlib.Path({str(leaderfile)!r}).write_text(str(os.getpid()))\n"
                    f"subprocess.Popen([sys.executable, '-c', {child!r}])\n"
                    f"while not pathlib.Path({str(pidfile)!r}).exists(): time.sleep(0.01)\n"
                    + ("sys.exit(0)\n" if exit_early else "time.sleep(30)\n")
                )
                started = time.monotonic()
                wrapper = subprocess.Popen(
                    [sys.executable, str(SCRIPT), "run", "--cli", "codex",
                     "--workspace", str(self.workspace), "--prompt", "test", "--timeout", "1.5"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                )
                try:
                    output, error = wrapper.communicate(timeout=5)
                    self.assertEqual(wrapper.returncode, 0, error)
                    result = json.loads(output)
                    self.assertEqual(result["outcome"], "interrupted")
                    self.assertIn("child-ready", result["stdout"])
                    self.assertLess(time.monotonic() - started, 4)
                    child_pid = int(pidfile.read_text())
                    state = subprocess.run(["ps", "-o", "stat=", "-p", str(child_pid)],
                                           capture_output=True, text=True, check=False).stdout.strip()
                    self.assertTrue(not state or state.startswith("Z"), state)
                finally:
                    if wrapper.poll() is None:
                        wrapper.kill()
                    wrapper.communicate()
                    if leaderfile.exists():
                        try:
                            os.killpg(int(leaderfile.read_text()), signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                        leaderfile.unlink()
                    if pidfile.exists():
                        pidfile.unlink()

    def test_pi_command_separates_cli_provider_and_model(self) -> None:
        result = agent_tool.command(
            "pi", "test", workspace=self.workspace,
            provider="dianxiaomi", model="kimi-k3", session="session-id",
        )
        self.assertEqual(result[:8], [
            "pi", "-p", "--mode", "json", "--provider",
            "dianxiaomi", "--model", "kimi-k3",
        ])

    def test_run_preserves_cli_permissions_and_passes_exact_model(self) -> None:
        for cli in agent_tool.CLIS:
            with self.subTest(cli=cli):
                self.provider("printf '%s\\n' \"$@\"\n")
                if cli != "codex":
                    (self.bin / "codex").rename(self.bin / cli)
                args = ["run", "--cli", cli, "--workspace", str(self.workspace),
                        "--prompt", "review only"]
                if cli in ("claude", "codex"):
                    args += ["--model", "exact-user-model"]
                stream = io.StringIO()
                with contextlib.redirect_stdout(stream):
                    agent_tool.main(args)
                result = json.loads(stream.getvalue())
                self.assertEqual(result["outcome"], "completed")
                passed = result["stdout"].splitlines()
                for forbidden in ("--dangerously-skip-permissions",
                                  "--dangerously-bypass-approvals-and-sandbox",
                                  "--approve", "--auto"):
                    self.assertNotIn(forbidden, passed)
                if cli in ("claude", "codex"):
                    self.assertEqual(passed[passed.index("--model") + 1], "exact-user-model")

    def test_cli_model_rejection_is_reported_without_retry(self) -> None:
        self.provider("printf 'unknown model\\n' >&2\nexit 2\n")
        _, output = self.invoke("--model", "unknown-user-model")
        result = json.loads(output)
        self.assertEqual(result["outcome"], "failed")
        self.assertEqual(result["exit_code"], 2)
        self.assertEqual(result["stderr"], "unknown model\n")

    def test_unsupported_provider_is_still_rejected(self) -> None:
        self.assertIn("does not support provider", agent_tool._validate_selection("claude", "custom", "model"))

    def test_kimi_prompt_mode_does_not_use_auto(self) -> None:
        result = agent_tool.command(
            "kimi", "test", workspace=self.workspace,
            provider="dianxiaomi", model="kimi-k3", session=None,
        )
        self.assertIn("-p", result)
        self.assertNotIn("--auto", result)

    def test_model_selection_requires_exact_provider_and_model(self) -> None:
        available = ([{"provider": "dianxiaomi", "model": "kimi-k3"}], None)
        with mock.patch.object(agent_tool, "discover_models", return_value=available):
            self.assertIsNone(agent_tool._validate_selection("pi", "dianxiaomi", "kimi-k3"))
            self.assertIn("model kimi", agent_tool._validate_selection("pi", "dianxiaomi", "kimi"))

    def test_kimi_model_discovery_discards_credentials(self) -> None:
        output = json.dumps({
            "providers": {"dianxiaomi": {"apiKey": "secret"}},
            "models": {"kimi-k3": {"provider": "dianxiaomi", "model": "kimi-k3"}},
        })
        completed = subprocess.CompletedProcess([], 0, stdout=output, stderr="")
        with mock.patch.object(agent_tool.subprocess, "run", return_value=completed):
            models, error = agent_tool.discover_models("kimi")
        self.assertIsNone(error)
        self.assertEqual(models, [{"provider": "dianxiaomi", "model": "kimi-k3"}])
        self.assertNotIn("secret", json.dumps(models))


if __name__ == "__main__":
    unittest.main()
