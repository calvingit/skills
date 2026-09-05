from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from engineering.loop.scripts.receipt_artifacts import load, save


class ReceiptArtifactTests(unittest.TestCase):
    def test_round_trip_keeps_identity_and_payload_outside_graph(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = save(root, ticket_id="T001", attempt=2, capability="verify", payload={"passed": True})
            artifact = load(root, ticket_id="T001", attempt=2, capability="verify")

            self.assertEqual(path.name, "verify.json")
            self.assertEqual(artifact["payload"], {"passed": True})
            self.assertTrue(artifact["agent_instance_id"])
            self.assertFalse((root / "tickets").exists())

    def test_rejects_wrong_identity_and_path_segments(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            save(root, ticket_id="T001", attempt=1, capability="aggregate", payload={})
            with self.assertRaises(ValueError):
                load(root, ticket_id="T002", attempt=1, capability="aggregate")
            with self.assertRaises(ValueError):
                save(root, ticket_id="../T001", attempt=1, capability="verify", payload={})
            with self.assertRaises(ValueError):
                save(root, ticket_id="T01", attempt=1, capability="verify", payload={})
            with self.assertRaises(ValueError):
                save(root, ticket_id="T001", attempt=True, capability="verify", payload={})


if __name__ == "__main__":
    unittest.main()
