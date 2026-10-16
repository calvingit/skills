"""Regression cases A-P: ticket contract vs runtime state, and serial/swarm strategy.

Each case drives real graph commands; none of them asserts on documentation prose.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import test_bootstrap
from test_bootstrap import read_state, read_ticket, runtime_entry, write_ticket

E = Path(__file__).resolve().parents[2]

from lifecycle import initialize_state, mutate_ticket
from ticket_graph.authority import authority_fingerprint, contract_fingerprint
from ticket_graph.migrate import parse_v3_ticket
from ticket_graph.queries import inspect
from planning import reconcile_batch
from test_ticket_graph import canonical_ticket as ticket
import delivery

SPEC = "# Spec\n1. **R1** — Send a message.\n- **AC1** — Covers: R1. Visible result.\n"
SOLUTION = "# Solution\n- **D1** — Reuse persistence.\n"
BASELINE = {"reference": "HEAD", "staged": [], "unstaged": [], "untracked": []}


def run(script, *args, stdin=None, cwd=None):
    env = dict(os.environ); env.pop("PYTHONPATH", None)
    result = subprocess.run(
        [sys.executable, str(E / script), *args],
        input=stdin, capture_output=True, text=True, cwd=cwd, env=env,
    )
    return result.returncode, json.loads(result.stdout)


def start_request(scope, mode=None):
    request = {"baseline": BASELINE, "existing_changes": {"included": [], "excluded": []}, "allowed_write_scope": scope}
    if mode is not None:
        request["mode"] = mode
    return request


def complete_request(attempt, **evidence):
    return {
        "expected_attempt": attempt,
        "evidence": evidence or {"AC1": {"result": "passed", "summary": "Observed expected result."}},
        "verification": [{"command": "project test", "exit_code": 0, "summary": "Required checks passed."}],
    }


def candidate(key, title, dependencies=(), acceptance=()):
    criteria = list(acceptance) or [{"id": "AC1", "description": f"{title} is observable."}]
    return {
        "key": key,
        "title": title,
        "covers": {"requirements": ["R1"], "spec_acceptance": ["AC1"]},
        "referenced_design_decisions": ["D1"],
        "what_to_build": f"Deliver {title}.",
        "constraints": [],
        "delivery_acceptance": criteria,
        "dependencies": list(dependencies),
    }


class StateSeparationCaseTests(unittest.TestCase):
    def setUp(self):
        self.workspace = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(self.workspace, ignore_errors=True))
        self.workspace.joinpath("src.py").write_text("print(1)\n", encoding="utf-8")
        self.task = self.workspace / "task"
        (self.task / "tickets").mkdir(parents=True)
        (self.task / "SPEC.md").write_text(SPEC, encoding="utf-8")
        (self.task / "SOLUTION.md").write_text(SOLUTION, encoding="utf-8")

    def git(self, *args):
        subprocess.run(["git", "-C", str(self.workspace), *args], check=True, capture_output=True)

    def create(self, *candidates):
        code, payload = run(
            "to-tickets/scripts/create-graph", "create-batch", str(self.task),
            "--input", "-", stdin=json.dumps({"tickets": list(candidates)}),
        )
        self.assertEqual(code, 0, payload)
        return payload

    def status(self):
        code, payload = run("graph-workflow/scripts/update-status", *self.args)
        return code, payload

    def loop(self, operation, target, request):
        args = [operation, str(self.task), target, "--input", "-"]
        code, payload = run("graph-workflow/scripts/update-status", *args, stdin=json.dumps(request))
        return code, payload

    # Case A
    def test_case_a_create_three_tickets_initializes_contract_and_state(self):
        self.create(candidate("a", "A"), candidate("b", "B", ["a"]), candidate("c", "C", ["a"]))
        for path in sorted((self.task / "tickets").glob("*.md")):
            text = path.read_text(encoding="utf-8")
            head = text.split("\n---\n", 1)[0]
            self.assertIn("schema_version: 4", head)
            for absent in ("lifecycle", "execution", "evidence"):
                self.assertNotIn(absent, head)
        state = read_state(self.task)
        self.assertEqual(sorted(state["tickets"]), ["T001", "T002", "T003"])
        self.assertTrue(all(entry["phase"] == "open" for entry in state["tickets"].values()))
        graph = inspect(self.task)[0]["graph"]
        self.assertEqual(graph["frontier"], ["T001"])

    # Case B
    def test_case_b_frontier_ready_and_blocked_semantics_are_unchanged(self):
        self.create(candidate("a", "A"), candidate("b", "B", ["a"]), candidate("c", "C"))
        code, payload = run("graph-workflow/scripts/graph-query", "list", str(self.task))
        self.assertEqual(code, 0, payload)
        readiness = {item["id"]: item["readiness"] for item in payload["result"]["tickets"]}
        self.assertEqual(readiness, {"T001": "ready", "T002": "blocked", "T003": "ready"})
        self.loop("start", "T001", start_request(["src/"]))
        self.loop("complete", "T001", complete_request(1))
        graph = inspect(self.task)[0]["graph"]
        self.assertEqual(graph["frontier"], ["T002", "T003"])
        self.assertEqual(graph["done"], ["T001"])

    # Case C
    def test_case_c_state_changes_never_touch_the_ticket_file(self):
        self.create(candidate("a", "A"))
        path = self.task / "tickets/T001-a.md"
        before = path.read_bytes()
        self.loop("start", "T001", start_request(["src/"]))
        middle = runtime_entry(self.task, "T001")
        self.assertEqual((middle["phase"], middle["attempt"]), ("in_progress", 1))
        self.loop("complete", "T001", complete_request(1))
        self.assertEqual(path.read_bytes(), before)
        after = runtime_entry(self.task, "T001")
        self.assertEqual(after["phase"], "done")
        self.assertEqual(after["evidence"]["AC1"]["attempt"], 1)

    # Case D
    def test_case_d_retry_and_reopen_never_reuse_invalidated_evidence(self):
        self.create(candidate("a", "A", acceptance=[
            {"id": "AC1", "description": "First."}, {"id": "AC2", "description": "Second."},
        ]))
        self.loop("start", "T001", start_request(["src/"]))
        self.loop("complete", "T001", complete_request(1, **{
            "AC1": {"result": "passed", "summary": "First observed."},
            "AC2": {"result": "passed", "summary": "Second observed."},
        }))
        code, payload = self.loop("reopen", "T001", {
            "review_finding": "First behaviour is wrong.", "invalidated_acceptance": ["AC1"], "upstream_unchanged": True,
        })
        self.assertEqual(code, 0, payload)
        reopened = runtime_entry(self.task, "T001")
        self.assertEqual(sorted(reopened["evidence"]), ["AC2"])
        self.assertEqual(reopened["evidence"]["AC2"]["attempt"], 1)
        self.loop("start", "T001", start_request(["src/"]))
        self.assertEqual(runtime_entry(self.task, "T001")["attempt"], 2)
        code, payload = self.loop("complete", "T001", complete_request(1, **{
            "AC1": {"result": "passed", "summary": "Corrected."},
            "AC2": {"result": "passed", "summary": "Second observed."},
        }))
        self.assertEqual(code, 1)
        self.assertEqual(payload["problems"][0]["code"], "stale_attempt")
        self.loop("complete", "T001", complete_request(2, **{
            "AC1": {"result": "passed", "summary": "Corrected."},
            "AC2": {"result": "passed", "summary": "Second observed."},
        }))
        self.assertEqual(runtime_entry(self.task, "T001")["evidence"]["AC1"]["attempt"], 2)
        self.loop("reopen", "T001", {
            "review_finding": "Correction attempt still needs rework.", "invalidated_acceptance": ["AC1"], "upstream_unchanged": True,
        })
        self.loop("start", "T001", start_request(["src/"]))
        self.loop("retry", "T001", {"baseline": BASELINE, "existing_changes": {"included": [], "excluded": []}, "expected_attempt": 3, "findings": "Rework."})
        retried = runtime_entry(self.task, "T001")
        self.assertNotIn("evidence", retried)
        self.assertEqual(retried["reopen_context"]["invalidated_acceptance"], ["AC1", "AC2"])

    # Case E
    def test_case_e_block_records_reason_and_release_condition(self):
        self.create(candidate("a", "A"))
        self.loop("start", "T001", start_request(["src/"]))
        self.loop("block", "T001", {
            "blocker": {"category": "environment", "reason": "Service is down.", "release_condition": "Service answers."},
            "evidence": {},
        })
        entry = runtime_entry(self.task, "T001")
        self.assertEqual(entry["phase"], "open")
        self.assertEqual(entry["blocker"]["release_condition"], "Service answers.")
        code, payload = self.loop("start", "T001", start_request(["src/"]))
        self.assertEqual(code, 1)
        self.assertEqual(payload["problems"][0]["code"], "ticket_not_ready")
        self.loop("unblock", "T001", {"release_evidence": "Service answers on the project health check."})
        self.assertNotIn("blocker", runtime_entry(self.task, "T001"))
        self.assertEqual(self.loop("start", "T001", start_request(["src/"]))[0], 0)

    # Case F
    def test_case_f_changed_upstream_invalidates_recorded_authority(self):
        self.create(candidate("a", "A"))
        self.loop("start", "T001", start_request(["src/"]))
        self.loop("complete", "T001", complete_request(1))
        (self.task / "SPEC.md").write_text(SPEC.replace("Send a message.", "Send a signed message."), encoding="utf-8")
        graph = inspect(self.task)[0]["graph"]
        self.assertEqual(graph["stale_authority"], ["T001"])
        self.assertFalse(graph["delivery_ready"])
        code, payload = self.loop("reopen", "T001", {
            "review_finding": "x", "invalidated_acceptance": ["AC1"], "upstream_unchanged": True,
        })
        self.assertEqual(code, 1)
        self.assertEqual(payload["problems"][0]["code"], "upstream_changed")
        with self.assertRaises(ValueError):
            delivery.prepare(self.task, self.workspace)

    # Case G
    def test_case_g_reconcile_keeps_contract_and_state_consistent(self):
        self.create(candidate("a", "A"), candidate("b", "B", ["a"]))
        payload, code = reconcile_batch(self.task, {"reason": "Confirmed delta.", "operations": [
            {"operation": "create", "key": "c", "ticket": {k: v for k, v in candidate("c", "C").items() if k != "key"}},
            {"operation": "replace_dependency", "ticket_id": "T002", "from": "T001", "to": "c"},
        ]})
        self.assertEqual(code, 0, payload)
        state = read_state(self.task)["tickets"]
        self.assertEqual(sorted(state), ["T001", "T002", "T003"])
        self.assertEqual(state["T003"]["phase"], "open")
        self.assertEqual(read_ticket(self.task / "tickets/T002-b.md")["dependencies"], ["T003"])
        snapshot = inspect(self.task)[0]
        self.assertTrue(snapshot["ok"], snapshot)

    # Case H
    def test_case_h_lost_state_fails_loudly_and_requires_explicit_reinitialization(self):
        self.create(candidate("a", "A"))
        self.loop("start", "T001", start_request(["src/"]))
        self.loop("complete", "T001", complete_request(1))
        test_bootstrap.state_file(self.task).unlink()
        code, payload = run("graph-workflow/scripts/frontier", str(self.task))
        self.assertEqual(code, 1)
        self.assertEqual(payload["problems"][0]["code"], "missing_runtime_state")
        code, payload = self.loop("start", "T001", start_request(["src/"]))
        self.assertEqual(code, 1)
        self.assertEqual(payload["problems"][0]["code"], "missing_runtime_state")
        self.assertFalse(test_bootstrap.state_file(self.task).exists())
        code, payload = run(
            "graph-workflow/scripts/update-status", "init-state", str(self.task),
            "--input", "-", stdin=json.dumps({"reason": "User confirmed the recorded progress was lost."}),
        )
        self.assertEqual(code, 0, payload)
        self.assertEqual(runtime_entry(self.task, "T001"), {"phase": "open", "attempt": 0})
        self.assertEqual(payload["graph"]["done"], [])
        code, payload = run(
            "graph-workflow/scripts/update-status", "init-state", str(self.task),
            "--input", "-", stdin=json.dumps({"reason": "Again."}),
        )
        self.assertEqual(code, 1)
        self.assertEqual(payload["problems"][0]["code"], "runtime_state_present")

    # Cases I and T004
    def test_case_i_and_t004_local_completion_never_passes_final_delivery(self):
        self.git("init", "-q")
        self.git("add", ".")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "baseline")
        self.create(candidate("a", "A"))
        self.loop("start", "T001", start_request(["src.py"]))
        self.loop("complete", "T001", complete_request(1))
        graph = inspect(self.task)[0]["graph"]
        self.assertTrue(graph["delivery_ready"])
        self.assertEqual(delivery.status(self.task)["state"], "not_reviewed")
        context = delivery.prepare(self.task, self.workspace)
        receipt = {
            "snapshot": context["snapshot"],
            "evidence": {"AC1": {"result": "passed", "summary": "Independently observed."}},
            "verification": [{"command": "project test", "exit_code": 0, "summary": "Passed."}],
            "approved": True, "unverified": [],
        }
        with self.assertRaises(ValueError):
            delivery.complete(self.task, receipt)  # Local acceptance is not an independent review.
        receipt["review"] = "Independent review found a blocking defect in the delivered behaviour."
        self.assertEqual(delivery.complete(self.task, receipt)["state"], "passed")
        self.assertEqual(
            run("graph-workflow/scripts/frontier", str(self.task))[1]["result"]["delivery_review"]["state"],
            "passed",
        )

    # Case J
    def test_case_j_progress_and_code_changes_invalidate_the_delivery_snapshot(self):
        self.git("init", "-q")
        self.git("add", ".")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "baseline")
        self.create(candidate("a", "A"))
        self.loop("start", "T001", start_request(["src.py"]))
        self.loop("complete", "T001", complete_request(1))
        context = delivery.prepare(self.task, self.workspace)
        self.assertTrue(delivery.complete(self.task, {
            "snapshot": context["snapshot"],
            "evidence": {"AC1": {"result": "passed", "summary": "Independently observed."}},
            "verification": [{"command": "project test", "exit_code": 0, "summary": "Passed."}],
            "approved": True, "unverified": [], "review": "Independent review report.",
        })["state"], "passed")
        (self.workspace / "src.py").write_text("print(2)\n", encoding="utf-8")
        self.assertEqual(delivery.status(self.task)["state"], "stale")

    def test_case_j_runtime_progress_change_invalidates_the_delivery_snapshot(self):
        self.git("init", "-q")
        self.git("add", ".")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "baseline")
        self.create(candidate("a", "A"), candidate("b", "B"))
        for ticket_id in ("T001", "T002"):
            self.loop("start", ticket_id, start_request(["src.py"]))
            self.loop("complete", ticket_id, complete_request(1))
        context = delivery.prepare(self.task, self.workspace)
        self.assertTrue(delivery.complete(self.task, {
            "snapshot": context["snapshot"],
            "evidence": {"AC1": {"result": "passed", "summary": "Independently observed."}},
            "verification": [{"command": "project test", "exit_code": 0, "summary": "Passed."}],
            "approved": True, "unverified": [], "review": "Independent review report.",
        })["state"], "passed")
        code, payload = self.loop("reopen", "T001", {
            "review_finding": "Later review invalidated this evidence.", "invalidated_acceptance": ["AC1"], "upstream_unchanged": True,
        })
        self.assertEqual(code, 0, payload)
        self.assertEqual(delivery.status(self.task)["state"], "stale")
        with self.assertRaises(ValueError):
            delivery.complete(self.task, {
                "snapshot": context["snapshot"],
                "evidence": {"AC1": {"result": "passed", "summary": "Independently observed."}},
                "verification": [{"command": "project test", "exit_code": 0, "summary": "Passed."}],
                "approved": True, "unverified": [], "review": "Independent review report.",
            })

    # Case K
    def test_case_k_default_execution_is_serial(self):
        self.create(candidate("a", "A"), candidate("b", "B"))
        self.assertEqual(self.loop("start", "T001", start_request(["src/a/"]))[0], 0)
        code, payload = self.loop("start", "T002", start_request(["src/b/"]))
        self.assertEqual(code, 1)
        self.assertEqual(payload["problems"][0]["code"], "parallel_dispatch_requires_swarm")
        self.assertEqual(inspect(self.task)[0]["graph"]["in_progress"], ["T001"])

    # Case L
    def test_case_l_explicit_swarm_allows_safe_parallel_attempts(self):
        self.create(candidate("a", "A"), candidate("b", "B"))
        self.assertEqual(self.loop("start", "T001", start_request(["src/a/"]))[0], 0)
        code, payload = self.loop("start", "T002", start_request(["src/b/"], mode="swarm"))
        self.assertEqual(code, 0, payload)
        self.assertEqual(payload["graph"]["in_progress"], ["T001", "T002"])
        self.assertEqual(runtime_entry(self.task, "T002")["current_attempt"]["number"], 1)

    # Case M
    def test_case_m_swarm_refuses_dependencies_and_overlapping_writes(self):
        self.create(candidate("a", "A"), candidate("b", "B"), candidate("c", "C", ["a"]))
        self.assertEqual(self.loop("start", "T001", start_request(["src/shared/"]))[0], 0)
        code, payload = self.loop("start", "T002", start_request(["src/shared/file.py"], mode="swarm"))
        self.assertEqual(code, 1)
        self.assertEqual(payload["problems"][0]["code"], "write_scope_overlap")
        code, payload = self.loop("start", "T003", start_request(["src/other/"], mode="swarm"))
        self.assertEqual(code, 1)
        codes = {item["code"] for item in payload["problems"]}
        self.assertIn("ticket_not_ready", codes)  # Its dependency has not finished; swarm cannot start it early.

    # Case N
    def test_case_n_switching_modes_keeps_attempts_and_writes_disjoint(self):
        self.create(candidate("a", "A"), candidate("b", "B"))
        self.assertEqual(self.loop("start", "T001", start_request(["src/a/"], mode="swarm"))[0], 0)
        self.assertEqual(self.loop("start", "T002", start_request(["src/b/"], mode="swarm"))[0], 0)
        code, payload = self.loop("start", "T001", start_request(["src/a/"]))
        self.assertEqual(code, 1)
        self.assertEqual(payload["problems"][0]["code"], "ticket_not_ready")
        self.loop("complete", "T001", complete_request(1))
        self.loop("complete", "T002", complete_request(1))
        self.assertEqual(
            {item_id: entry["attempt"] for item_id, entry in read_state(self.task)["tickets"].items()},
            {"T001": 1, "T002": 1},
        )
        self.assertEqual(inspect(self.task)[0]["graph"]["done"], ["T001", "T002"])

    # Case O
    def test_case_o_task_reports_do_not_invalidate_the_candidate(self):
        self.git("init", "-q")
        self.git("add", ".")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "baseline")
        self.create(candidate("a", "A"))
        self.loop("start", "T001", start_request(["src.py"]))
        self.loop("complete", "T001", complete_request(1))
        context = delivery.prepare(self.task, self.workspace)
        reports = self.task / ".loop/reports"
        reports.mkdir()
        for name in ("T001-attempt-1.md", "delivery-review.md", "command-log.txt"):
            (reports / name).write_text("appended execution output\n", encoding="utf-8")
            self.assertEqual(
                delivery._snapshot(self.task.resolve(), self.workspace.resolve())[0],
                context["snapshot"],
            )

    # Case P
    def test_case_p_loop_never_appears_in_git_status(self):
        self.git("init", "-q")
        self.create(candidate("a", "A"))
        self.loop("start", "T001", start_request(["src/"]))
        (self.task / ".loop/T001-attempt-1.md").write_text("report\n", encoding="utf-8")
        (self.task / ".loop/command-log.txt").write_text("log\n", encoding="utf-8")
        status = subprocess.run(
            ["git", "-C", str(self.workspace), "status", "--porcelain", "-uall"],
            capture_output=True, text=True, check=True,
        ).stdout
        self.assertNotIn(".loop", status)
        self.assertIn("task/tickets/T001-a.md", status)

    # T001: state separation
    def test_t001_completed_ticket_keeps_its_contract_and_reports_progress_from_state(self):
        self.create(candidate("a", "A"))
        self.loop("start", "T001", start_request(["src/"]))
        self.loop("complete", "T001", complete_request(1))
        path = self.task / "tickets/T001-a.md"
        head = path.read_text(encoding="utf-8").split("\n---\n", 1)[0]
        for absent in ("lifecycle", "execution", "evidence", "attempt", "authority"):
            self.assertNotIn(absent, head)
        code, payload = run("graph-workflow/scripts/graph-query", "show", str(self.task), "T001")
        self.assertEqual(code, 0, payload)
        entry = payload["result"]["ticket"]["runtime"]
        self.assertEqual(entry["phase"], "done")
        self.assertEqual(entry["attempt"], 1)
        self.assertEqual(entry["evidence"], {"AC1": {"attempt": 1, "summary": "Observed expected result."}})
        self.assertEqual(entry["authority"]["fingerprint"], contract_fingerprint(self.task, read_ticket(path)))

    # T002: reopening after review invalidates only the affected evidence
    def test_t002_reopen_after_review_keeps_history_and_the_contract(self):
        self.create(candidate("a", "A", acceptance=[
            {"id": "AC1", "description": "First."}, {"id": "AC2", "description": "Second."},
        ]))
        path = self.task / "tickets/T001-a.md"
        role = self.loop("start", "T001", start_request(["src/"]))
        self.assertEqual(role[0], 0, role[1])
        self.loop("complete", "T001", complete_request(1, **{
            "AC1": {"result": "passed", "summary": "First observed."},
            "AC2": {"result": "passed", "summary": "Second observed."},
        }))
        contract_before = path.read_bytes()
        code, payload = self.loop("reopen", "T001", {
            "review_finding": "Independent review found the second behaviour missing.",
            "invalidated_acceptance": ["AC2"], "upstream_unchanged": True,
        })
        self.assertEqual(code, 0, payload)
        entry = runtime_entry(self.task, "T001")
        self.assertEqual(entry["phase"], "open")
        self.assertEqual(sorted(entry["evidence"]), ["AC1"])
        self.assertEqual(entry["reopen_context"]["invalidated_acceptance"], ["AC2"])
        self.assertEqual(path.read_bytes(), contract_before)
        self.assertEqual(read_state(self.task)["tickets"]["T001"]["attempt"], 1)
        self.loop("start", "T001", start_request(["src/"]))
        self.assertEqual(runtime_entry(self.task, "T001")["attempt"], 2)

    def test_v3_task_migrates_with_its_confirmed_execution_record(self):
        v3_document = (
            "---\n"
            "schema_version: 3\n"
            "id: T001\n"
            "covers:\n  requirements:\n    - R1\n  spec_acceptance:\n    - AC1\n"
            "referenced_design_decisions:\n  - D1\n"
            "dependencies: []\n"
            "lifecycle:\n  phase: done\n"
            "execution:\n"
            "  attempt_sequence: 1\n"
            "  evidence:\n"
            "    AC1:\n      result: passed\n      summary: \"Observed before the split.\"\n"
            "  blocker: null\n"
            "  current_attempt: null\n"
            "  reopen_context: null\n"
            "  authority:\n"
            "    fingerprint: \"FINGERPRINT\"\n"
            "    reason: \"Execution contract confirmed at start.\"\n"
            "supersession: null\n"
            "---\n\n# A\n\n## Delivery\n\nDeliver A.\n\n## Constraints\n\n## Delivery Acceptance\n\n- **AC1** — A is observable.\n"
        )
        recorded_contract = parse_v3_ticket(v3_document)[0]
        fingerprint = contract_fingerprint(self.task, recorded_contract)
        path = self.task / "tickets/T001-a.md"
        path.write_text(v3_document.replace("FINGERPRINT", fingerprint), encoding="utf-8")
        code, payload = run("to-tickets/scripts/create-graph", "migrate-v3", str(self.task))
        self.assertEqual(code, 0, payload)
        self.assertEqual(payload["result"]["migrated"], ["T001"])
        self.assertTrue(any("attempt" in note for note in payload["result"]["notes"]))
        self.assertEqual(read_ticket(path)["schema_version"], 4)
        self.assertEqual(
            runtime_entry(self.task, "T001"),
            {
                "phase": "done", "attempt": 1,
                "authority": {"fingerprint": fingerprint, "reason": "Execution contract confirmed at start."},
                "evidence": {"AC1": {"attempt": 1, "summary": "Observed before the split."}},
            },
        )
        self.assertEqual(payload["graph"]["stale_authority"], [])
        self.assertTrue(payload["graph"]["delivery_ready"])

    def test_v3_migration_reports_an_uncertain_execution_record_instead_of_inventing_one(self):
        v3_document = (
            "---\n"
            "schema_version: 3\n"
            "id: T001\n"
            "covers:\n  requirements:\n    - R1\n  spec_acceptance:\n    - AC1\n"
            "referenced_design_decisions:\n  - D1\n"
            "dependencies: []\n"
            "lifecycle:\n  phase: done\n"
            "execution:\n"
            "  attempt_sequence: 0\n"
            "  evidence: {}\n"
            "  blocker: null\n"
            "  current_attempt: null\n"
            "  reopen_context: null\n"
            "supersession: null\n"
            "---\n\n# A\n\n## Delivery\n\nDeliver A.\n\n## Constraints\n\n## Delivery Acceptance\n\n- **AC1** — A is observable.\n"
        )
        (self.task / "tickets/T001-a.md").write_text(v3_document, encoding="utf-8")
        code, payload = run("to-tickets/scripts/create-graph", "migrate-v3", str(self.task))
        self.assertEqual(code, 1)
        self.assertIn("done_without_acceptance_evidence", {item["code"] for item in payload["problems"]})
        self.assertFalse(test_bootstrap.state_file(self.task).exists())
        self.assertIn("schema_version: 3", (self.task / "tickets/T001-a.md").read_text(encoding="utf-8"))

    def test_migration_rejects_a_task_that_still_has_runtime_state(self):
        self.create(candidate("a", "A"))
        code, payload = run("to-tickets/scripts/create-graph", "migrate-v3", str(self.task))
        self.assertEqual(code, 1)
        self.assertEqual(payload["problems"][0]["code"], "runtime_state_present")

    def test_unknown_state_entries_are_reported(self):
        self.create(candidate("a", "A"))
        state = read_state(self.task)
        state["tickets"]["T404"] = {"phase": "open", "attempt": 0}
        test_bootstrap.state_file(self.task).write_text(json.dumps(state), encoding="utf-8")
        code, payload = run("graph-workflow/scripts/frontier", str(self.task))
        self.assertEqual(code, 1)
        self.assertIn("unknown_state_ticket", {item["code"] for item in payload["problems"]})

    def test_unreadable_state_can_be_reinitialized_explicitly(self):
        self.create(candidate("a", "A"))
        test_bootstrap.state_file(self.task).write_text("{not json", encoding="utf-8")
        code, payload = run("graph-workflow/scripts/frontier", str(self.task))
        self.assertEqual(code, 1)
        self.assertEqual(payload["problems"][0]["code"], "invalid_runtime_state")
        payload, code = initialize_state(self.task, {"reason": "Recorded progress is unreadable and confirmed lost."})
        self.assertEqual(code, 0, payload)
        self.assertEqual(runtime_entry(self.task, "T001")["phase"], "open")


if __name__ == "__main__":
    unittest.main()
