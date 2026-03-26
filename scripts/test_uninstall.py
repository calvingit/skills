import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import uninstall


def _make_index(root: Path, categories: list) -> None:
    (root / "index.json").write_text(
        json.dumps({"categories": categories}), encoding="utf-8"
    )


class GetCategorySkillIdsTests(unittest.TestCase):
    def test_returns_ids_for_existing_category(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_index(
                root,
                [
                    {
                        "name": "Tool",
                        "items": [
                            {"id": "ctx7", "url": "https://x.com/ctx7", "desc": ""},
                            {"id": "xlsx", "url": "https://x.com/xlsx", "desc": ""},
                        ],
                    }
                ],
            )
            ids = uninstall.get_category_skill_ids(root, "Tool")
            self.assertEqual(ids, ["ctx7", "xlsx"])

    def test_raises_for_unknown_category(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_index(root, [{"name": "Tool", "items": [{"id": "x", "url": "u", "desc": ""}]}])
            with self.assertRaises(ValueError, msg="未找到分类"):
                uninstall.get_category_skill_ids(root, "Unknown")

    def test_raises_for_empty_category(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_index(root, [{"name": "Tool", "items": []}])
            with self.assertRaises(ValueError, msg="没有可卸载的技能"):
                uninstall.get_category_skill_ids(root, "Tool")


class BuildRemoveCommandTests(unittest.TestCase):
    def test_basic_command(self) -> None:
        cmd = uninstall.build_remove_command("ctx7", False, [])
        self.assertEqual(cmd, ["npx", "skills", "remove", "ctx7", "-y"])

    def test_global_flag(self) -> None:
        cmd = uninstall.build_remove_command("ctx7", True, [])
        self.assertIn("-g", cmd)

    def test_agent_flags(self) -> None:
        cmd = uninstall.build_remove_command("ctx7", False, ["claude-code", "codex"])
        self.assertEqual(cmd.count("-a"), 2)

    def test_yes_flag_always_last(self) -> None:
        cmd = uninstall.build_remove_command("ctx7", True, ["a"])
        self.assertEqual(cmd[-1], "-y")


class ParseArgsTests(unittest.TestCase):
    def test_skill_flag(self) -> None:
        args = uninstall.parse_args(["--skill", "ctx7"])
        self.assertEqual(args.skill, "ctx7")
        self.assertIsNone(args.category)

    def test_category_flag(self) -> None:
        args = uninstall.parse_args(["--category", "Tool"])
        self.assertEqual(args.category, "Tool")
        self.assertIsNone(args.skill)

    def test_dry_run_flag(self) -> None:
        args = uninstall.parse_args(["--skill", "x", "--dry-run"])
        self.assertTrue(args.dry_run)


class ExecuteRemovesTests(unittest.TestCase):
    def test_dry_run_skips_subprocess(self) -> None:
        with patch("subprocess.run") as mock_run:
            failures = uninstall.execute_removes(["ctx7", "xlsx"], False, [], dry_run=True)
            mock_run.assert_not_called()
            self.assertEqual(failures, [])

    def test_collects_failures_and_continues(self) -> None:
        def side_effect(cmd, **_):
            result = MagicMock()
            result.returncode = 1 if "ctx7" in cmd else 0
            return result

        with patch("subprocess.run", side_effect=side_effect):
            failures = uninstall.execute_removes(["ctx7", "xlsx"], False, [], dry_run=False)
        self.assertEqual(failures, ["ctx7"])


class MainTests(unittest.TestCase):
    def test_requires_exactly_one_of_skill_or_category(self) -> None:
        with self.assertRaises(ValueError):
            uninstall.main([])  # neither
        with self.assertRaises(ValueError):
            uninstall.main(["--skill", "x", "--category", "Tool"])  # both

    def test_skill_dry_run_returns_zero(self) -> None:
        with patch.object(uninstall, "ensure_npx_available"):
            with patch("subprocess.run"):
                rc = uninstall.main(["--skill", "ctx7", "--dry-run"])
        self.assertEqual(rc, 0)

    def test_category_expands_to_all_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_index(
                root,
                [
                    {
                        "name": "Tool",
                        "items": [
                            {"id": "ctx7", "url": "u1", "desc": ""},
                            {"id": "xlsx", "url": "u2", "desc": ""},
                        ],
                    }
                ],
            )
            called_ids: list[str] = []

            def fake_run(cmd, **_):
                called_ids.append(cmd[3])
                result = MagicMock()
                result.returncode = 0
                return result

            original_root = uninstall.ROOT
            uninstall.ROOT = root
            try:
                with patch.object(uninstall, "ensure_npx_available"):
                    with patch("subprocess.run", side_effect=fake_run):
                        rc = uninstall.main(["--category", "Tool"])
            finally:
                uninstall.ROOT = original_root

            self.assertEqual(rc, 0)
            self.assertEqual(called_ids, ["ctx7", "xlsx"])


if __name__ == "__main__":
    unittest.main()
