from __future__ import annotations

import unittest

from engineering.loop.scripts.scope_guard import allowed_scope, violations


class ScopeGuardTests(unittest.TestCase):
    def test_implement_accepts_only_delivery_scope(self) -> None:
        self.assertEqual(allowed_scope("implement", ["src/"]), ["src/"])
        self.assertEqual(violations("implement", ["src/"], ["src/app.py"]), [])
        self.assertEqual(violations("implement", ["src/"], ["README.md", "tickets/T001.json"]), ["README.md", "tickets/T001.json"])

    def test_read_only_capabilities_reject_all_repository_changes(self) -> None:
        self.assertEqual(allowed_scope("verify", []), [])
        self.assertEqual(violations("verify", [], ["build/cache.bin"]), ["build/cache.bin"])
        self.assertEqual(violations("review", [], ["SPEC.md", "src/app.py"]), ["SPEC.md", "src/app.py"])
        with self.assertRaises(ValueError):
            allowed_scope("verify", ["tmp/"])


if __name__ == "__main__":
    unittest.main()
