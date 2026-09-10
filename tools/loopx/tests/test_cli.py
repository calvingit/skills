import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]

class LoopxCliTests(unittest.TestCase):
    def run_cli(self, *args):
        env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
        return subprocess.run([sys.executable, "-m", "loopx", *args], cwd=ROOT, env=env, capture_output=True, text=True)

    def test_state_help_and_version(self):
        for args in [("loop", "status", "--help"), ("graph", "complete", "--help")]:
            result = self.run_cli(*args)
            self.assertEqual(result.returncode, 0)
            self.assertIn("usage:", result.stdout)
        result = self.run_cli("version")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["command"], "version")

    def test_agent_execution_commands_are_not_available(self):
        for args in [("worker", "run", ".", "--prompt", "test"), ("worker", "providers"),
                     ("loop", "run", ".", "--scope", "src/")]:
            result = self.run_cli(*args)
            self.assertEqual(result.returncode, 2)
            self.assertIn("invalid choice", result.stderr)

    def test_graph_errors_are_structured(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_cli("graph", "inspect", directory)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["command"], "graph.inspect")
        result = self.run_cli("graph")
        self.assertEqual(result.returncode, 2)
        self.assertFalse(json.loads(result.stdout)["ok"])

if __name__ == "__main__":
    unittest.main()
