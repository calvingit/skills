from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "fetch_markdown.sh"


class FetchMarkdownTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.calls = self.root / "calls.jsonl"
        self.responses = self.root / "responses.json"
        fake = self.root / "curl"
        fake.write_text(
            "#!" + sys.executable + "\n"
            "from pathlib import Path\nimport json, os, sys\n"
            "calls = Path(os.environ['FETCH_TEST_CALLS'])\n"
            "index = len(calls.read_text().splitlines()) if calls.exists() else 0\n"
            "with calls.open('a') as stream: stream.write(json.dumps(sys.argv[1:]) + '\\n')\n"
            "response = json.loads(Path(os.environ['FETCH_TEST_RESPONSES']).read_text())[index]\n"
            "output = Path(os.environ['FETCH_TEST_OUTPUT'])\n"
            "kind = response.get('concurrent_kind')\n"
            "if kind == 'file': output.write_text('user content')\n"
            "elif kind == 'directory': output.mkdir(); (output / 'user.txt').write_text('user content')\n"
            "elif kind == 'symlink':\n"
            " target = output.with_name('user.txt'); target.write_text('user content'); output.symlink_to(target)\n"
            "Path(sys.argv[sys.argv.index('--output') + 1]).write_text(response['body'])\n"
            "sys.exit(response.get('exit', 0))\n"
        )
        fake.chmod(0o755)
        self.env = {
            **os.environ,
            "PATH": str(self.root) + os.pathsep + os.environ["PATH"],
            "FETCH_TEST_CALLS": str(self.calls),
            "FETCH_TEST_RESPONSES": str(self.responses),
            "FETCH_TEST_OUTPUT": str(self.root / "article.md"),
        }

    def run_fetch(self, responses, output="article.md", url="https://example.com/article"):
        self.responses.write_text(json.dumps(responses))
        args = ["bash", str(SCRIPT), url]
        if output is not None:
            args.append(str(self.root / output))
        return subprocess.run(args, cwd=self.root, env=self.env, capture_output=True, text=True)

    def test_error_page_falls_through_to_valid_markdown(self):
        body = "# Article\n\nActual page content.\n"
        result = self.run_fetch([
            {"body": "<html><body>Access denied</body></html>"},
            {"body": body},
        ])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / "article.md").read_text(), body)
        self.assertEqual(len(self.calls.read_text().splitlines()), 2)
        self.assertIn("https://r.jina.ai", result.stdout)

    def test_all_invalid_responses_fail_without_output(self):
        result = self.run_fetch([
            {"body": " \n\t"},
            {"body": "<!DOCTYPE html><html>Challenge</html>"},
            {"body": "# Access denied\n"},
        ])
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / "article.md").exists())
        self.assertIn("empty response", result.stderr)
        self.assertIn("HTML or error response", result.stderr)
        self.assertEqual(len(self.calls.read_text().splitlines()), 3)

    def test_network_failure_does_not_accept_partial_body(self):
        body = "# Complete page\n"
        result = self.run_fetch([
            {"body": "partial", "exit": 28},
            {"body": body},
        ])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / "article.md").read_text(), body)

    def test_existing_output_is_preserved_without_request(self):
        (self.root / "article.md").write_text("user content")
        result = self.run_fetch([])
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.root / "article.md").read_text(), "user content")
        self.assertFalse(self.calls.exists())

    def test_default_filename_works_outside_skill_directory(self):
        result = self.run_fetch([{"body": "# Page\n"}], output=None)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / "example.com-article.md").read_text(), "# Page\n")

    def test_normal_markdown_with_html_example_is_preserved(self):
        body = "# HTML tutorial\n\n```html\n<html><body>Hello</body></html>\n```\n"
        result = self.run_fetch([{"body": body}])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / "article.md").read_text(), body)

    def test_invalid_url_does_not_make_request(self):
        result = self.run_fetch([], url="file:///private/file")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.calls.exists())

    def assert_late_output_preserved(self, kind):
        result = self.run_fetch([{"body": "# Download\n", "concurrent_kind": kind}])
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Saved markdown", result.stdout)
        output = self.root / "article.md"
        if kind == "directory":
            self.assertEqual(list(output.iterdir()), [output / "user.txt"])
            output = output / "user.txt"
        elif kind == "symlink":
            self.assertTrue(output.is_symlink())
        self.assertEqual(output.read_text(), "user content")

    def test_file_created_during_download_is_preserved(self):
        self.assert_late_output_preserved("file")

    def test_directory_created_during_download_is_preserved(self):
        self.assert_late_output_preserved("directory")

    def test_symlink_created_during_download_is_preserved(self):
        self.assert_late_output_preserved("symlink")

    def test_explicit_error_responses_fall_through(self):
        for body in ("HTTP 429: Too Many Requests", '{"error":"Service unavailable"}'):
            with self.subTest(body=body):
                result = self.run_fetch([{"body": body}, {"body": "# Article\n"}])
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual((self.root / "article.md").read_text(), "# Article\n")
                self.assertEqual(len(self.calls.read_text().splitlines()), 2)
                (self.root / "article.md").unlink()
                self.calls.unlink()


if __name__ == "__main__":
    unittest.main()
