from __future__ import annotations

import json
import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from loopx.cli_backend import CliBackend
from loopx.review_report import normalize_review_report
from loopx.capability_adapter import CapabilityAdapter


def report(verdict="PASS", findings="None.", follow_up="None.", gaps="None.", unverified="None."):
    return f"""## Verdict
{verdict}

## Scope
src/orders.py against HEAD; request: reject duplicate orders.

## Findings
{findings}

## Follow-up
{follow_up}

## Requirement gaps
{gaps}

## Unverified
{unverified}

## Evidence
Inspected submit() callers and the duplicate-order assertion. Supplied pytest result: exit 0.
"""


DEFECT = "### [P2] 重试会重复下单\nsrc/orders.py:42 在超时重试时没有复用幂等键，造成重复扣款。复用请求键，并验证重复调用只生成一笔订单。"


class ReviewReportTests(unittest.TestCase):
    def test_pass_and_optional_follow_up(self):
        for follow_up in ("None.", DEFECT):
            result = normalize_review_report(report(follow_up=follow_up))
            self.assertEqual(result["outcome"], "completed")
            self.assertEqual(result["payload"]["review"]["change_surface"], "pass")
            self.assertFalse(result["payload"]["blocking_findings"])
            self.assertEqual(len(result["payload"]["non_blocking_findings"]), int(follow_up != "None."))

    def test_p2_defect_requires_fixes_and_preserves_evidence(self):
        result = normalize_review_report(report("FIXES NEEDED", findings=DEFECT))
        self.assertEqual(result["payload"]["review"]["change_surface"], "failed")
        finding = result["payload"]["blocking_findings"][0]
        self.assertEqual(finding["severity"], "P2")
        self.assertIn("重复扣款", finding["evidence"])
        self.assertEqual(finding["recommended_route"], "retry")

    def test_gaps_and_missing_evidence_never_pass(self):
        for kwargs, key in (({"gaps": "Cancellation requirements conflict."}, "acceptance_protocol_gaps"),
                            ({"unverified": "Permission test could not run."}, "unverified_scope")):
            result = normalize_review_report(report("INCOMPLETE", **kwargs))
            self.assertTrue(result["payload"][key])
            self.assertEqual(result["payload"]["review"]["contract"], "failed")

    def test_malformed_or_contradictory_reports_block(self):
        bad = ["Looks good", "", report().replace("## Evidence", "## Scope"),
               report(findings=DEFECT), report("FIXES NEEDED"), report("INCOMPLETE"),
               report().replace("None.", "", 1), report().replace("## Evidence", "## Unknown"),
               report("FIXES NEEDED", findings="### [P1] No evidence"),
               "```markdown\n" + report() + "```", report().replace("PASS", "PASS maybe")]
        for text in bad:
            with self.subTest(text=text):
                result = normalize_review_report(text)
                self.assertEqual(result["outcome"], "blocked")
                self.assertIn("release_condition", result["payload"]["blocker"])

    def test_provider_assistant_events_and_raw_markdown(self):
        text = report("FIXES NEEDED", findings=DEFECT)
        events = [{"type": "item.completed", "item": {"type": "agent_message", "text": text}},
                  {"type": "result", "result": text},
                  {"type": "message_end", "message": {"role": "assistant", "content": [{"type": "text", "text": text}]}},
                  {"type": "assistant", "message": {"role": "assistant", "content": text}}]
        for output in [text] + [json.dumps(event) for event in events]:
            result = CliBackend._parse_output(output, "", 0, review=True)
            self.assertTrue(result["payload"]["blocking_findings"])

    def test_final_message_wins_and_tool_output_cannot_pass(self):
        passing = json.dumps({"type": "assistant", "message": {"role": "assistant", "content": report()}})
        tool = json.dumps({"type": "tool_result", "content": report()})
        latest = json.dumps({"type": "assistant", "message": {"role": "assistant", "content": "Unable to finish"}})
        for output, final in ((tool, None), (passing + "\n" + latest, None), (passing, "Unable to finish"), (passing, "")):
            self.assertEqual(CliBackend._parse_output(output, "", 0, review=True, final_text=final)["outcome"], "blocked")
        self.assertEqual(CliBackend._parse_output(report(), "fatal", 1, review=True)["outcome"], "failed")

    def test_markdown_results_drive_real_ticket_transitions(self):
        from test_loop_runtime import ticket, receipt
        from loopx.loop_runtime import run_ticket
        cases = [(report(), "completed"), (report(follow_up=DEFECT), "completed"),
                 (report("FIXES NEEDED", findings=DEFECT), "retry"),
                 (report("INCOMPLETE", gaps="Requirements conflict."), "blocked"),
                 (report("INCOMPLETE", unverified="Cannot inspect required file."), "blocked"),
                 ("No report", "blocked")]
        for text, expected in cases:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as directory:
                task = Path(directory)
                (task / "tickets").mkdir()
                (task / "SPEC.md").write_text("# Spec\n1. **R1** — Run.\n- **AC1** — Covers: R1. Run.\n")
                (task / "HLD.md").write_text("# HLD\n- **D1** — Use graph.\n")
                (task / "tickets/T001-test.json").write_text(json.dumps(ticket()))
                result = CliBackend._parse_output(text, "", 0, review=True)
                value = receipt(outcome=result["outcome"], **{key: val for key, val in result["payload"].items() if key != "review_report"})
                actual = run_ticket(task, lambda _: value, allowed_write_scope=["src/"],
                                    baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []})
                self.assertEqual(actual.outcome, expected, actual.problems)

    def test_review_handoff_requests_markdown_and_wait_normalizes(self):
        backend = CliBackend("claude", executable="/bin/echo")
        handle = backend.create("review", {})
        process = Mock()
        process.communicate.return_value = (json.dumps({"type": "result", "result": report()}), "")
        process.returncode = 0
        with patch("loopx.cli_backend.subprocess.Popen", return_value=process) as popen:
            backend.send(handle, {"ticket": {"id": "T001"}})
        prompt = json.loads(popen.call_args.args[0][-1])
        self.assertEqual(prompt["response_contract"]["sections"][0], "Verdict")
        result = backend.wait(handle)
        self.assertEqual(result["payload"]["review"]["contract"], "pass")
        self.assertIn("review_report", result["payload"])
        normalized = CapabilityAdapter._result("review", "T001", 1, handle, result)
        aggregated = CapabilityAdapter._aggregate([normalized])
        self.assertEqual(aggregated["receipt"]["review"]["change_surface"], "pass")


if __name__ == "__main__":
    unittest.main()
