import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import post_install


class RunChecksTests(unittest.TestCase):
    def test_all_present_returns_empty(self) -> None:
        checks = [
            post_install.CliCheck("ctx7", "npm i -g ctx7", "Context7"),
            post_install.CliCheck("tvly", "curl ...", "Tavily"),
        ]
        with patch("shutil.which", return_value="/usr/bin/ctx7"):
            missing = post_install.run_checks(checks)
        self.assertEqual(missing, [])

    def test_one_missing_returned(self) -> None:
        def which_side_effect(name: str) -> str | None:
            return None if name == "tvly" else f"/usr/bin/{name}"

        checks = [
            post_install.CliCheck("ctx7", "npm i -g ctx7", "Context7"),
            post_install.CliCheck("tvly", "curl ...", "Tavily"),
        ]
        with patch("shutil.which", side_effect=which_side_effect):
            missing = post_install.run_checks(checks)

        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0].name, "tvly")

    def test_all_missing(self) -> None:
        checks = [
            post_install.CliCheck("ctx7", "npm i -g ctx7", "Context7"),
            post_install.CliCheck("tvly", "curl ...", "Tavily"),
        ]
        with patch("shutil.which", return_value=None):
            missing = post_install.run_checks(checks)
        self.assertEqual(len(missing), len(checks))


class CheckCliTests(unittest.TestCase):
    def test_found(self) -> None:
        cli = post_install.CliCheck(
            name="ctx7", install_hint="npm i -g ctx7", description="x"
        )
        with patch("shutil.which", return_value="/usr/bin/ctx7"):
            self.assertTrue(post_install.check_cli(cli))

    def test_not_found(self) -> None:
        cli = post_install.CliCheck(
            name="ctx7", install_hint="npm i -g ctx7", description="x"
        )
        with patch("shutil.which", return_value=None):
            self.assertFalse(post_install.check_cli(cli))


class NormalizeSkillIdsTests(unittest.TestCase):
    def test_normalize_skill_ids(self) -> None:
        raw = ["context7-cli,tavily-search", "agent-browser", " context7-cli "]
        normalized = post_install.normalize_skill_ids(raw)
        self.assertEqual(
            normalized,
            {"context7-cli", "tavily-search", "agent-browser"},
        )


class FindMissingEnvVarsTests(unittest.TestCase):
    def test_missing_env_vars_detected(self) -> None:
        checks = [
            post_install.CliCheck(
                "ctx7",
                "npm i -g ctx7",
                "Context7",
                env_vars=[
                    post_install.EnvVarCheck(
                        "CONTEXT7_API_KEY",
                        "export CONTEXT7_API_KEY=your_key",
                        "Context7 API Key",
                    )
                ],
            )
        ]
        with patch.dict("os.environ", {}, clear=True):
            missing = post_install.find_missing_env_vars(checks)
        self.assertEqual(list(missing.keys()), ["ctx7"])
        self.assertEqual(missing["ctx7"][0].name, "CONTEXT7_API_KEY")

    def test_present_env_vars_skipped(self) -> None:
        checks = [
            post_install.CliCheck(
                "ctx7",
                "npm i -g ctx7",
                "Context7",
                env_vars=[
                    post_install.EnvVarCheck(
                        "CONTEXT7_API_KEY",
                        "export CONTEXT7_API_KEY=your_key",
                        "Context7 API Key",
                    )
                ],
            )
        ]
        with patch.dict("os.environ", {"CONTEXT7_API_KEY": "abc"}, clear=True):
            missing = post_install.find_missing_env_vars(checks)
        self.assertEqual(missing, {})


class LoadRequiredClisTests(unittest.TestCase):
    def _write_index(self, path: Path) -> None:
        path.write_text(
            """
{
  "categories": [
    {
      "name": "Tool",
      "items": [
        {
          "id": "context7-cli",
          "url": "https://example.com/context7-cli",
          "desc": "x",
          "cli": [
            {
              "name": "ctx7",
              "install_hint": "npm install -g ctx7@latest",
              "description": "Context7 CLI"
            }
          ]
        },
        {
          "id": "tavily-search",
          "url": "https://example.com/tavily-search",
          "desc": "x",
          "cli": [
            {
              "name": "tvly",
              "install_hint": "curl -fsSL https://cli.tavily.com/install.sh | bash",
              "description": "Tavily CLI"
            },
            {
              "name": "ctx7",
              "install_hint": "npm install -g ctx7@latest",
              "description": "重复项用于去重"
            }
          ]
        },
        {
          "id": "plain-skill",
          "url": "https://example.com/plain-skill",
          "desc": "no cli"
        }
      ]
    }
  ]
}
""".strip(),
            encoding="utf-8",
        )

    def test_load_all_when_no_filter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            index_path = Path(tmp) / "index.json"
            self._write_index(index_path)

            with patch.object(post_install, "INDEX_PATH", index_path):
                clis = post_install.load_required_clis()

        self.assertEqual([cli.name for cli in clis], ["ctx7", "tvly"])
        self.assertEqual(clis[0].env_vars, [])

    def test_filter_by_installed_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            index_path = Path(tmp) / "index.json"
            self._write_index(index_path)

            with patch.object(post_install, "INDEX_PATH", index_path):
                clis = post_install.load_required_clis({"tavily-search"})

        self.assertEqual([cli.name for cli in clis], ["tvly", "ctx7"])

        def test_loads_cli_env_vars(self) -> None:
            with tempfile.TemporaryDirectory() as tmp:
                index_path = Path(tmp) / "index.json"
                index_path.write_text(
                    """
{
    "categories": [
        {
            "name": "Tool",
            "items": [
                {
                    "id": "context7-cli",
                    "url": "https://example.com/context7-cli",
                    "desc": "x",
                    "cli": [
                        {
                            "name": "ctx7",
                            "install_hint": "npm install -g ctx7@latest",
                            "description": "Context7 CLI",
                            "env_vars": [
                                {
                                    "name": "CONTEXT7_API_KEY",
                                    "export_hint": "export CONTEXT7_API_KEY=your_key",
                                    "description": "Context7 API Key"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}
""".strip(),
                    encoding="utf-8",
                )

                with patch.object(post_install, "INDEX_PATH", index_path):
                    clis = post_install.load_required_clis({"context7-cli"})

            self.assertEqual(len(clis[0].env_vars), 1)
            self.assertEqual(clis[0].env_vars[0].name, "CONTEXT7_API_KEY")

    def test_missing_index_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            index_path = Path(tmp) / "missing.json"
            with patch.object(post_install, "INDEX_PATH", index_path):
                with self.assertRaises(ValueError):
                    post_install.load_required_clis()


class MainTests(unittest.TestCase):

    def test_returns_zero_when_no_required_cli(self) -> None:
        with patch.object(post_install, "load_required_clis", return_value=[]):
            rc = post_install.main([])
        self.assertEqual(rc, 0)

    def test_returns_nonzero_when_missing(self) -> None:
        checks = [post_install.CliCheck("ctx7", "npm install -g ctx7", "Context7")]
        with patch.object(post_install, "load_required_clis", return_value=checks):
            with patch("shutil.which", return_value=None):
                rc = post_install.main(["--installed-skills", "context7-cli"])
        self.assertNotEqual(rc, 0)

    def test_returns_nonzero_when_env_missing(self) -> None:
        checks = [
            post_install.CliCheck(
                "ctx7",
                "npm install -g ctx7",
                "Context7",
                env_vars=[
                    post_install.EnvVarCheck(
                        "CONTEXT7_API_KEY",
                        "export CONTEXT7_API_KEY=your_key",
                        "Context7 API Key",
                    )
                ],
            )
        ]
        with patch.object(post_install, "load_required_clis", return_value=checks):
            with patch("shutil.which", return_value="/usr/bin/ctx7"):
                with patch.dict("os.environ", {}, clear=True):
                    rc = post_install.main(["--installed-skills", "context7-cli"])
        self.assertNotEqual(rc, 0)

    def test_installed_skills_filter_is_passed(self) -> None:
        checks = [post_install.CliCheck("ctx7", "npm install -g ctx7", "Context7")]
        with patch.object(
            post_install, "load_required_clis", return_value=checks
        ) as mocked:
            with patch("shutil.which", return_value="/usr/bin/ctx7"):
                rc = post_install.main(
                    ["--installed-skills", "context7-cli,tavily-search"]
                )
        self.assertEqual(rc, 0)
        mocked.assert_called_once_with({"context7-cli", "tavily-search"})

    def test_without_installed_skills_uses_none_filter(self) -> None:
        checks = [post_install.CliCheck("ctx7", "npm install -g ctx7", "Context7")]
        with patch.object(
            post_install, "load_required_clis", return_value=checks
        ) as mocked:
            with patch("shutil.which", return_value="/usr/bin/ctx7"):
                rc = post_install.main([])
        self.assertEqual(rc, 0)
        mocked.assert_called_once_with(None)

    def test_returns_zero_when_cli_and_env_ready(self) -> None:
        checks = [
            post_install.CliCheck(
                "ctx7",
                "npm install -g ctx7",
                "Context7",
                env_vars=[
                    post_install.EnvVarCheck(
                        "CONTEXT7_API_KEY",
                        "export CONTEXT7_API_KEY=your_key",
                        "Context7 API Key",
                    )
                ],
            )
        ]
        with patch.object(post_install, "load_required_clis", return_value=checks):
            with patch("shutil.which", return_value="/usr/bin/ctx7"):
                with patch.dict("os.environ", {"CONTEXT7_API_KEY": "abc"}, clear=True):
                    rc = post_install.main([])
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
