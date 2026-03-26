import json
import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import install


class NormalizeAgentsTests(unittest.TestCase):
    def test_comma_in_single_flag(self) -> None:
        self.assertEqual(
            install.normalize_agents(["claude-code, codex, trae"]),
            ["claude-code", "codex", "trae"],
        )

    def test_mixed_flags_and_commas(self) -> None:
        self.assertEqual(
            install.normalize_agents(["claude-code,codex", "trae"]),
            ["claude-code", "codex", "trae"],
        )

    def test_empty_list(self) -> None:
        self.assertEqual(install.normalize_agents([]), [])


class LoadItemsTests(unittest.TestCase):
    def _make_index(self, tmp: Path, categories: list) -> None:
        (tmp / "index.json").write_text(
            json.dumps({"categories": categories}), encoding="utf-8"
        )

    def test_flattens_all_categories(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_index(
                root,
                [
                    {
                        "name": "Tool",
                        "items": [
                            {"id": "ctx7", "url": "https://a.com/ctx7", "desc": ""}
                        ],
                    },
                    {
                        "name": "Web",
                        "items": [
                            {"id": "nuxt", "url": "https://a.com/nuxt", "desc": ""}
                        ],
                    },
                ],
            )
            items = install.load_items(root)
            self.assertEqual([i["id"] for i in items], ["ctx7", "nuxt"])

    def test_deduplicates_by_url(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dup_url = "https://example.com/skill"
            self._make_index(
                root,
                [
                    {"name": "A", "items": [{"id": "s1", "url": dup_url, "desc": ""}]},
                    {"name": "B", "items": [{"id": "s2", "url": dup_url, "desc": ""}]},
                ],
            )
            items = install.load_items(root)
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0]["id"], "s1")

    def test_missing_index_raises(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                install.load_items(Path(tmp))

    def test_invalid_categories_type_raises(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.json").write_text(
                json.dumps({"categories": "bad"}), encoding="utf-8"
            )
            with self.assertRaises(ValueError):
                install.load_items(root)


class BuildInstallCommandTests(unittest.TestCase):
    def test_basic_url_command(self) -> None:
        cmd = install.build_install_command("https://github.com/foo/bar", False, [])
        self.assertEqual(
            cmd, ["npx", "skills", "add", "https://github.com/foo/bar", "-y"]
        )

    def test_global_flag(self) -> None:
        cmd = install.build_install_command("https://x.com", True, [])
        self.assertIn("-g", cmd)

    def test_agent_flags(self) -> None:
        cmd = install.build_install_command(
            "https://x.com", False, ["claude-code", "codex"]
        )
        self.assertEqual(cmd.count("-a"), 2)
        idx = cmd.index("-a")
        self.assertEqual(cmd[idx + 1], "claude-code")
        self.assertEqual(cmd[idx + 3], "codex")

    def test_yes_flag_always_last(self) -> None:
        cmd = install.build_install_command("https://x.com", True, ["a", "b"])
        self.assertEqual(cmd[-1], "-y")


if __name__ == "__main__":
    unittest.main()
