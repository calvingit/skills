import os
import unittest
from unittest.mock import patch

from loopx.worker.routing import runtime_provider, select_provider


class RoutingTests(unittest.TestCase):
    @patch("loopx.worker.routing.available_providers", return_value=["codex", "pi"])
    def test_current_runtime_wins_over_probe_order(self, _available) -> None:
        with patch.dict(os.environ, {"CODEX_THREAD_ID": "thread-1"}, clear=True):
            self.assertEqual(select_provider(), ("codex", "current runtime provider: codex", ["codex", "pi"]))

    @patch("loopx.worker.routing.available_providers", return_value=["codex", "pi"])
    def test_runtime_override_wins_over_detected_runtime(self, _available) -> None:
        with patch.dict(os.environ, {"LOOPX_RUNTIME_PROVIDER": "pi", "CODEX_THREAD_ID": "thread-1"}, clear=True):
            self.assertEqual(select_provider(), ("pi", "current runtime provider: pi", ["codex", "pi"]))

    @patch("loopx.worker.routing.available_providers", return_value=["codex", "pi"])
    def test_explicit_provider_wins_over_current_runtime(self, _available) -> None:
        with patch.dict(os.environ, {"CODEX_THREAD_ID": "thread-1"}, clear=True):
            self.assertEqual(select_provider("pi"), ("pi", "explicit provider override", ["codex", "pi"]))

    def test_unknown_runtime_override_is_rejected(self) -> None:
        with patch.dict(os.environ, {"LOOPX_RUNTIME_PROVIDER": "unknown"}, clear=True):
            with self.assertRaises(ValueError):
                runtime_provider()

    def test_false_runtime_override_is_ignored(self) -> None:
        with patch.dict(os.environ, {"LOOPX_RUNTIME_PROVIDER": "false"}, clear=True):
            self.assertIsNone(runtime_provider())
