from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "inspect_graph.py"


def ticket(
    *,
    status: str,
    acceptance: str = "- [x] AC1 — behavior is observable",
    blocked_by: str = "- None (can start immediately)",
    evidence: str = "- AC1 — passed — targeted verification",
    execution_blocker: str = "- None",
) -> str:
    return f"""# 01 — Example

## Specification

- [SPEC.md](../SPEC.md)

## What to build

Implement one observable behavior.

## Constraints

- Preserve the existing contract.

## Acceptance criteria

{acceptance}

## Blocked by

{blocked_by}

## Execution evidence

{evidence}

## Execution blocker

{execution_blocker}

## Status

{status}
"""


class InspectGraphTests(unittest.TestCase):
    def inspect(self, ticket_text: str) -> tuple[dict[str, object], int]:
        with tempfile.TemporaryDirectory() as temp_dir:
            task_dir = Path(temp_dir)
            (task_dir / "tickets").mkdir()
            (task_dir / "SPEC.md").write_text("# Spec\n", encoding="utf-8")
            (task_dir / "tickets" / "01-example.md").write_text(ticket_text, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(task_dir)],
                check=False,
                capture_output=True,
                text=True,
            )
            return json.loads(result.stdout), result.returncode

    def test_done_requires_checked_acceptance_and_execution_evidence(self) -> None:
        payload, exit_code = self.inspect(
            ticket(
                status="done",
                acceptance="- [ ] AC1 — behavior is observable",
                evidence="- Pending",
            )
        )

        self.assertEqual(exit_code, 1)
        self.assertFalse(payload["valid"])
        self.assertEqual(
            {problem["code"] for problem in payload["problems"]},
            {"done_with_unchecked_acceptance", "done_without_acceptance_evidence"},
        )

    def test_done_with_acceptance_evidence_is_complete(self) -> None:
        payload, exit_code = self.inspect(ticket(status="done"))

        self.assertEqual(exit_code, 0)
        self.assertTrue(payload["valid"])
        self.assertTrue(payload["all_active_done"])

    def test_done_requires_evidence_for_every_acceptance_id(self) -> None:
        payload, exit_code = self.inspect(
            ticket(
                status="done",
                acceptance="- [x] AC1 — first behavior\n- [x] AC2 — second behavior",
                evidence="- AC1 — passed — first behavior verified",
            )
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            {problem["code"] for problem in payload["problems"]},
            {"done_without_acceptance_evidence"},
        )
        self.assertIn("AC2", payload["problems"][0]["detail"])

    def test_done_accepts_evidence_for_each_acceptance_id(self) -> None:
        payload, exit_code = self.inspect(
            ticket(
                status="done",
                acceptance="- [x] AC1 — first behavior\n- [x] AC2 — second behavior",
                evidence="- AC1 — passed — first behavior verified\n- AC2 — passed — second behavior verified",
            )
        )

        self.assertEqual(exit_code, 0)
        self.assertTrue(payload["valid"])
        self.assertTrue(payload["all_active_done"])

    def test_execution_evidence_cannot_reference_unknown_acceptance_id(self) -> None:
        payload, exit_code = self.inspect(
            ticket(
                status="done",
                evidence="- AC1 — passed — behavior verified\n- AC2 — passed — unknown behavior",
            )
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            {problem["code"] for problem in payload["problems"]},
            {"execution_evidence_for_unknown_acceptance"},
        )

    def test_acceptance_ids_must_be_unique(self) -> None:
        payload, exit_code = self.inspect(
            ticket(
                status="done",
                acceptance="- [x] AC1 — first behavior\n- [x] AC1 — duplicate behavior",
            )
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            {problem["code"] for problem in payload["problems"]},
            {"duplicate_acceptance_id"},
        )

    def test_execution_evidence_ids_must_be_unique(self) -> None:
        payload, exit_code = self.inspect(
            ticket(
                status="done",
                evidence="- AC1 — passed — first observation\n- AC1 — passed — duplicate observation",
            )
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            {problem["code"] for problem in payload["problems"]},
            {"duplicate_execution_evidence"},
        )

    def test_not_verified_entry_does_not_satisfy_acceptance(self) -> None:
        payload, exit_code = self.inspect(
            ticket(
                status="done",
                evidence="- AC1 — not_verified — verification was unavailable",
            )
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            {problem["code"] for problem in payload["problems"]},
            {"unparsed_execution_evidence", "done_without_acceptance_evidence"},
        )

    def test_placeholder_passed_evidence_does_not_satisfy_acceptance(self) -> None:
        payload, exit_code = self.inspect(
            ticket(
                status="done",
                evidence="- AC1 — passed — Pending",
            )
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            {problem["code"] for problem in payload["problems"]},
            {"unparsed_execution_evidence", "done_without_acceptance_evidence"},
        )

    def test_ready_ticket_cannot_keep_an_execution_blocker(self) -> None:
        payload, exit_code = self.inspect(
            ticket(
                status="ready",
                evidence="- Pending",
                execution_blocker="- Waiting for a required permission",
            )
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            {problem["code"] for problem in payload["problems"]},
            {"active_execution_blocker"},
        )

    def test_ticket_requires_execution_sections(self) -> None:
        ticket_text = ticket(status="ready", evidence="- Pending").replace(
            "\n## Execution evidence\n\n- Pending\n",
            "\n",
        )

        payload, exit_code = self.inspect(ticket_text)

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            {problem["code"] for problem in payload["problems"]},
            {"missing_execution_evidence"},
        )

    def test_active_execution_blocker_is_reported_for_dependency_release_candidate(self) -> None:
        payload, exit_code = self.inspect(
            ticket(
                status="blocked",
                evidence="- Pending",
                execution_blocker="- Waiting for a required permission",
            )
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["dependency_releasable"], ["tickets/01-example.md"])
        self.assertEqual(
            payload["blocked"],
            [
                {
                    "ticket": "tickets/01-example.md",
                    "blocked_by": [],
                    "pending": [],
                    "execution_blocker": True,
                }
            ],
        )

    def test_blocked_ticket_without_remaining_blocker_is_release_candidate(self) -> None:
        payload, exit_code = self.inspect(ticket(status="blocked", evidence="- Pending"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["dependency_releasable"], ["tickets/01-example.md"])


if __name__ == "__main__":
    unittest.main()
