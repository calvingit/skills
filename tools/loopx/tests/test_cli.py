import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SRC = ROOT / "src"


class LoopxCliTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC)
        return subprocess.run(
            [sys.executable, "-m", "loopx", *args],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_help_is_standard_usage(self) -> None:
        result = self.run_cli("worker", "run", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage: loopx worker run", result.stdout)

    def test_version_command_is_versioned_json(self) -> None:
        result = self.run_cli("version")
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["command"], "version")
        self.assertEqual(payload["result"]["version"], "0.1.0")

    def test_public_contract_files_exist(self) -> None:
        self.assertTrue((ROOT / "src" / "loopx" / "contracts" / "cli-envelope.schema.json").is_file())
        self.assertTrue((ROOT / "src" / "loopx" / "contracts" / "worker-result.schema.json").is_file())

    def test_providers_is_versioned_json(self) -> None:
        result = self.run_cli("worker", "providers")
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["version"], 1)
        self.assertEqual(payload["command"], "worker.providers")
        self.assertIn("supported", payload["result"])

    def test_graph_command_delegates_to_graph_contract(self) -> None:
        task_dir = ROOT / "tests" / "fixtures" / "empty-task"
        task_dir.mkdir(parents=True, exist_ok=True)
        result = self.run_cli("graph", "inspect", str(task_dir))
        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["command"], "graph.inspect")

    def test_graph_output_uses_loopx_envelope(self) -> None:
        task_dir = ROOT / "tests" / "fixtures" / "empty-task"
        result = self.run_cli("graph", "inspect", str(task_dir))
        payload = json.loads(result.stdout)
        self.assertEqual(payload["version"], 1)
        self.assertEqual(payload["command"], "graph.inspect")

    def test_graph_without_operation_is_an_argument_error(self) -> None:
        result = self.run_cli("graph")
        self.assertEqual(result.returncode, 2)
        self.assertFalse(json.loads(result.stdout)["ok"])

    def test_graph_operation_help_is_usage(self) -> None:
        result = self.run_cli("graph", "inspect", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage: loopx graph inspect", result.stdout)

    def test_worker_requires_external_prompt(self) -> None:
        result = self.run_cli("worker", "run", "/tmp/task")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--prompt", result.stderr)

    def test_loop_run_requires_write_scope(self) -> None:
        result = self.run_cli("loop", "run", ".")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--scope", result.stderr)

    def test_worker_help_describes_prompt_runner(self) -> None:
        result = self.run_cli("worker", "run", "--help")
        self.assertIn("Run an external prompt", result.stdout)
        self.assertNotIn("implement", result.stdout)
        self.assertNotIn("--ticket", result.stdout)

    def test_worker_has_no_ticket_status_command(self) -> None:
        result = self.run_cli("worker", "status", ".", "--ticket", "T001")
        self.assertEqual(result.returncode, 2)

    def test_invalid_runtime_provider_is_json_error(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC)
        env["LOOPX_RUNTIME_PROVIDER"] = "unknown"
        result = subprocess.run(
            [sys.executable, "-m", "loopx", "worker", "run", ".", "--prompt", "test"],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["problems"][0]["code"], "invalid_runtime_provider")
        self.assertIn("outcome", json.loads(result.stdout)["result"])

    def test_worker_failure_result_has_a_payload(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC)
        result = subprocess.run(
            [sys.executable, "-m", "loopx", "worker", "run", "/missing", "--provider", "codex", "--prompt", "test"],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout)
        self.assertIn("payload", payload["result"])

    def test_missing_workspace_does_not_create_artifacts(self) -> None:
        missing = ROOT / "tests" / "fixtures" / "missing-workspace"
        result = self.run_cli("worker", "run", str(missing), "--provider", "codex", "--prompt", "test")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["problems"][0]["code"], "workspace_invalid")
        self.assertFalse(missing.exists())
        self.assertIsNone(json.loads(result.stdout)["result"]["artifact"])


if __name__ == "__main__":
    unittest.main()
