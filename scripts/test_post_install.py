import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import post_install


class RunChecksTests(unittest.TestCase):
    def test_all_present_returns_empty(self) -> None:
        with patch("shutil.which", return_value="/usr/bin/ctx7"):
            missing = post_install.run_checks(post_install.REQUIRED_CLIS)
        self.assertEqual(missing, [])

    def test_one_missing_returned(self) -> None:
        def which_side_effect(name: str) -> str | None:
            return None if name == "tvly" else f"/usr/bin/{name}"

        with patch("shutil.which", side_effect=which_side_effect):
            missing = post_install.run_checks(post_install.REQUIRED_CLIS)

        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0].name, "tvly")

    def test_all_missing(self) -> None:
        with patch("shutil.which", return_value=None):
            missing = post_install.run_checks(post_install.REQUIRED_CLIS)
        self.assertEqual(len(missing), len(post_install.REQUIRED_CLIS))


class CheckCliTests(unittest.TestCase):
    def test_found(self) -> None:
        cli = post_install.CliCheck(name="ctx7", install_hint="npm i -g ctx7", description="x")
        with patch("shutil.which", return_value="/usr/bin/ctx7"):
            self.assertTrue(post_install.check_cli(cli))

    def test_not_found(self) -> None:
        cli = post_install.CliCheck(name="ctx7", install_hint="npm i -g ctx7", description="x")
        with patch("shutil.which", return_value=None):
            self.assertFalse(post_install.check_cli(cli))


class MainTests(unittest.TestCase):
    def test_returns_zero_when_all_present(self) -> None:
        with patch("shutil.which", return_value="/usr/bin/cli"):
            rc = post_install.main([])
        self.assertEqual(rc, 0)

    def test_returns_nonzero_when_missing(self) -> None:
        with patch("shutil.which", return_value=None):
            rc = post_install.main([])
        self.assertNotEqual(rc, 0)

    def test_required_clis_include_all_three(self) -> None:
        names = {cli.name for cli in post_install.REQUIRED_CLIS}
        self.assertIn("ctx7", names)
        self.assertIn("tvly", names)
        self.assertIn("agent-browser", names)


if __name__ == "__main__":
    unittest.main()
