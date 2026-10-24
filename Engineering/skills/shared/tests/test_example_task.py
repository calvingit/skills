"""The docs example task stays loadable and internally consistent."""
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

import test_bootstrap
from ticket_graph import runtime, store

E = Path(__file__).resolve().parents[2]
EXAMPLE = E.parent / "docs" / "example-task"


class ExampleTaskRegressionTests(unittest.TestCase):
    def test_example_artifacts_load_and_cover_done_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            task = Path(temp)
            for name in ("SPEC.md", "SOLUTION.md"):
                shutil.copy(EXAMPLE / name, task / name)
            shutil.copytree(EXAMPLE / "tickets", task / "tickets")
            (task / ".loop").mkdir()
            shutil.copy(EXAMPLE / "loop-state.example.json", task / ".loop" / "state.json")

            state, state_problems = runtime.load_state(task)
            self.assertEqual(state_problems, [])
            self.assertIsNotNone(state)
            contracts, contract_problems = store.load_contracts(task)
            self.assertEqual(contract_problems, [])

            for ticket in contracts:
                entry = state["tickets"][ticket["id"]]
                if entry["phase"] == "done":
                    missing = {ac["id"] for ac in ticket["delivery_acceptance"]} - set(entry.get("evidence", {}))
                    self.assertEqual(missing, set(), ticket["id"])
