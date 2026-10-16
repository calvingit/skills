import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "report_lint.py"
SPEC = importlib.util.spec_from_file_location("report_lint", SCRIPT)
report_lint = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(report_lint)


class ReportLintTests(unittest.TestCase):
    def test_secret_diagnostic_does_not_echo_value(self):
        value = "synthetic-only-credential-for-test"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.md"
            path.write_text("# Report\napi_key=" + value + "\n")
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                code = report_lint.main([str(path)])
            self.assertEqual(code, 1)
            self.assertNotIn(value, stream.getvalue())
            self.assertIn("api_key", stream.getvalue())
            self.assertIn("line 2", stream.getvalue())

    def test_redacted_value_is_accepted_by_secret_check(self):
        issues = []
        report_lint.lint_secrets("api_key=<redacted>\npassword: redacted\n", issues)
        self.assertEqual(issues, [])

    def test_lowercase_severity_does_not_crash_statistics(self):
        issues = []
        report_lint.lint_markdown_stats("| High | 1 |\n- Severity: high\n", issues)
        self.assertEqual(issues, [])

    def test_incorrect_total_is_reported(self):
        issues = []
        report_lint.lint_markdown_stats("| High | 1 |\n| **Total** | **2** |\n- Severity: High\n", issues)
        self.assertTrue(any("Total finding count mismatch" in issue for issue in issues))

    def test_full_requires_concurrency_coverage(self):
        issues = []
        report_lint.lint_mode_sections('<section id="security"></section>', True, "full", issues)
        self.assertTrue(any("concurrency" in issue for issue in issues))

    def test_incremental_scope_accepts_focused_dimension(self):
        issues = []
        report_lint.lint_mode_sections("## Concurrency\nNo findings.\n", False, "incremental,concurrency", issues)
        self.assertEqual(issues, [])

    def test_finding_does_not_require_effort_or_redesign(self):
        finding = """### Finding: Retired command
- Severity: Low
- Confidence: High
- Category: Documentation
- Status: Confirmed
- Affected area: README usage
- Evidence: README references a removed CLI command.
- Problem: Documented command no longer exists.
- Why it matters: Setup instructions fail.
- Realistic failure scenario: Reader copies the documented command.
- Minimal fix: Update the usage example.
- Regression test suggestion: Compare with current CLI help.
"""
        issues = []
        report_lint.lint_markdown_findings(finding, issues)
        self.assertEqual(issues, [])
        issues = []
        report_lint.lint_markdown_findings(finding.replace("- Evidence: README references a removed CLI command.\n", ""), issues)
        self.assertTrue(any("missing field: Evidence" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
