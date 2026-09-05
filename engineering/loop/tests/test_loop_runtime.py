from __future__ import annotations

import json
import subprocess
import tempfile
import threading
import time
import unittest
from pathlib import Path

from engineering.loop.scripts.loop_runtime import _workspace_baseline, dispatch_ready, load_receipt, load_receipt_artifact, reopen_ticket, run_ticket
from engineering.loop.scripts.capability_adapter import CapabilityAdapter, CapabilitySession


def ticket() -> dict[str, object]:
    return {
        "schema_version": 1,
        "id": "T001",
        "title": "Runtime ticket",
        "covers": {"requirements": ["R1"], "spec_acceptance": ["AC1"]},
        "design_decisions": ["D1"],
        "what_to_build": "Run one ticket.",
        "constraints": ["Use the graph CLI."],
        "acceptance_criteria": [{"id": "AC1", "description": "It runs."}],
        "dependencies": [],
        "lifecycle": {"phase": "open"},
        "execution": {"attempt_sequence": 0, "evidence": {}, "blocker": None, "current_attempt": None, "reopen_context": None},
        "supersession": None,
    }


def receipt(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "schema_version": 1,
        "outcome": "completed",
        "ticket_id": "T001",
        "current_attempt": 1,
        "landed_changes": [],
        "acceptance_evidence": [{"acceptance_id": "AC1", "result": "passed", "summary": "Verified."}],
        "verification": [{"command": "self-check", "exit_code": 0, "summary": "Passed."}],
        "simplification": {"result": "no_change"},
        "review": {"standards": "pass", "spec": "pass", "hld": "pass"},
        "blocker": None,
        "unverified": [],
    }
    value.update(overrides)
    return value


class LoopRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.task_dir = Path(self.tmp.name)
        (self.task_dir / "tickets").mkdir()
        (self.task_dir / "SPEC.md").write_text("# Spec\n\n1. **R1** — Run.\n\n## Acceptance Criteria\n\n- **AC1** — Covers: R1. Run.\n", encoding="utf-8")
        (self.task_dir / "HLD.md").write_text("# HLD\n\n- **D1** — Use graph.\n", encoding="utf-8")
        (self.task_dir / "tickets" / "T001-runtime.json").write_text(json.dumps(ticket()) + "\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_completed_worker_is_normalized_and_persisted_through_cli(self) -> None:
        result = run_ticket(self.task_dir, lambda request: receipt(), allowed_write_scope=["src/"], baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []})
        self.assertEqual(result.outcome, "completed")
        stored = json.loads((self.task_dir / "tickets" / "T001-runtime.json").read_text(encoding="utf-8"))
        self.assertEqual(stored["lifecycle"]["phase"], "done")
        self.assertEqual(stored["execution"]["evidence"]["AC1"]["result"], "passed")
        self.assertEqual(load_receipt(self.task_dir, ticket_id="T001", attempt=1)["ticket_id"], "T001")
        self.assertTrue(load_receipt_artifact(self.task_dir, ticket_id="T001", attempt=1)["agent_instance_id"])
        self.assertTrue(load_receipt_artifact(self.task_dir, ticket_id="T001", attempt=1)["authority_fingerprint"])

    def test_missing_executor_does_not_start_ticket(self) -> None:
        result = run_ticket(self.task_dir, allowed_write_scope=["src/"], baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []})

        self.assertEqual(result.outcome, "failed")
        self.assertIn("missing_executor", {item["code"] for item in result.problems})
        stored = json.loads((self.task_dir / "tickets" / "T001-runtime.json").read_text(encoding="utf-8"))
        self.assertEqual(stored["lifecycle"]["phase"], "open")

    def test_untracked_paths_are_not_reported_as_staged_or_unstaged(self) -> None:
        subprocess.run(["git", "init", "-q", str(self.task_dir)], check=True)

        baseline = _workspace_baseline(self.task_dir)

        self.assertEqual(baseline["staged"], [])
        self.assertEqual(baseline["unstaged"], [])
        self.assertIn("SPEC.md", baseline["untracked"])

    def test_non_git_workspace_is_rejected_before_start(self) -> None:
        result = run_ticket(
            self.task_dir,
            lambda request: receipt(),
            workspace_root=self.task_dir,
            allowed_write_scope=["src/"],
            baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []},
        )

        self.assertEqual(result.outcome, "failed")
        self.assertIn("workspace_probe_unavailable", {item["code"] for item in result.problems})
        stored = json.loads((self.task_dir / "tickets" / "T001-runtime.json").read_text(encoding="utf-8"))
        self.assertEqual(stored["lifecycle"]["phase"], "open")

    def test_unknown_cli_provider_does_not_start_ticket(self) -> None:
        result = run_ticket(
            self.task_dir,
            provider="unknown",
            allowed_write_scope=["src/"],
            baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []},
        )

        self.assertEqual(result.outcome, "failed")
        self.assertIn("provider_unavailable", {item["code"] for item in result.problems})
        stored = json.loads((self.task_dir / "tickets" / "T001-runtime.json").read_text(encoding="utf-8"))
        self.assertEqual(stored["lifecycle"]["phase"], "open")

    def test_empty_implement_scope_is_rejected_before_start(self) -> None:
        result = run_ticket(self.task_dir, lambda request: receipt(), allowed_write_scope=[], baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []})

        self.assertEqual(result.outcome, "failed")
        self.assertIn("invalid_write_scope", {item["code"] for item in result.problems})
        stored = json.loads((self.task_dir / "tickets" / "T001-runtime.json").read_text(encoding="utf-8"))
        self.assertEqual(stored["lifecycle"]["phase"], "open")

    def test_run_ticket_can_use_capability_adapter(self) -> None:
        class Backend:
            def create(self, capability: str, bundle: dict[str, object]) -> str:
                return capability

            def send(self, handle: str, bundle: dict[str, object]) -> None:
                return None

            def wait(self, handle: str) -> dict[str, object]:
                if handle == "implement":
                    return {"outcome": "completed", "payload": {"simplification": {"result": "no_change"}}}
                if handle == "verify":
                    return {"outcome": "completed", "payload": {"acceptance_evidence": [{"acceptance_id": "AC1", "result": "passed", "summary": "passed"}], "verification": [{"command": "self-check", "exit_code": 0, "summary": "passed"}], "unverified": []}}
                return {"outcome": "completed", "payload": {"review": {"standards": "pass", "spec": "pass", "hld": "pass"}}}

            def interrupt(self, handle: str) -> None:
                return None

            def close(self, handle: str) -> None:
                return None

        result = run_ticket(self.task_dir, adapter=CapabilityAdapter(Backend()), allowed_write_scope=["engineering/loop/"], baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []})
        self.assertEqual(result.outcome, "completed")
        artifact_dir = self.task_dir / ".loop" / "receipts" / "T001" / "attempt-1"
        self.assertEqual({path.name for path in artifact_dir.iterdir()}, {"implement.json", "verify.json", "review.json", "aggregate.json"})

    def test_adapter_ignores_its_own_artifacts_in_a_git_workspace(self) -> None:
        subprocess.run(["git", "init", "-q", str(self.task_dir)], check=True)

        class Backend:
            def create(self, capability: str, bundle: dict[str, object]) -> str:
                return capability

            def send(self, handle: str, bundle: dict[str, object]) -> None:
                return None

            def wait(self, handle: str) -> dict[str, object]:
                if handle == "implement":
                    return {"outcome": "completed", "payload": {"simplification": {"result": "no_change"}}}
                if handle == "verify":
                    return {"outcome": "completed", "payload": {"acceptance_evidence": [{"acceptance_id": "AC1", "result": "passed", "summary": "passed"}], "verification": [{"command": "self-check", "exit_code": 0, "summary": "passed"}], "unverified": []}}
                return {"outcome": "completed", "payload": {"review": {"standards": "pass", "spec": "pass", "hld": "pass"}}}

            def interrupt(self, handle: str) -> None:
                return None

            def close(self, handle: str) -> None:
                return None

        result = run_ticket(
            self.task_dir,
            adapter=CapabilityAdapter(Backend()),
            workspace_root=self.task_dir,
            allowed_write_scope=["src/"],
            baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []},
        )

        self.assertEqual(result.outcome, "completed")

    def test_adapter_cannot_hide_unowned_loop_artifact_changes(self) -> None:
        subprocess.run(["git", "init", "-q", str(self.task_dir)], check=True)

        class Backend:
            def create(self, capability: str, bundle: dict[str, object]) -> str: return capability
            def send(self, handle: str, bundle: dict[str, object]) -> None: return None
            def wait(self, handle: str) -> dict[str, object]:
                if handle == "verify":
                    (self.task_dir / ".loop" / "unowned.json").write_text("{}\n", encoding="utf-8")
                return {"outcome": "completed", "payload": {"simplification": {"result": "no_change"}}}
            def interrupt(self, handle: str) -> None: return None
            def close(self, handle: str) -> None: return None

        backend = Backend()
        backend.task_dir = self.task_dir  # type: ignore[attr-defined]
        result = run_ticket(
            self.task_dir,
            adapter=CapabilityAdapter(backend),
            workspace_root=self.task_dir,
            allowed_write_scope=["src/"],
            baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []},
        )

        self.assertEqual(result.outcome, "failed")
        self.assertIn("worker_failed", {item["code"] for item in result.problems})

    def test_run_ticket_forwards_capability_parallelism_options(self) -> None:
        calls: dict[str, object] = {}

        class Adapter:
            def run(self, bundle: dict[str, object], **options: object) -> dict[str, object]:
                calls.update(options)
                return {
                    "outcome": "completed",
                    "capabilities": [],
                    "receipt": receipt(),
                }

        proof = {"dependencies": True, "write_scope": True, "shared_side_effects": True, "integration_order": True}
        result = run_ticket(
            self.task_dir,
            adapter=Adapter(),  # type: ignore[arg-type]
            allowed_write_scope=["src/"],
            isolation_proof=proof,
            concurrency_limit=2,
            baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []},
        )

        self.assertEqual(result.outcome, "completed")
        self.assertEqual(calls["isolation_proof"], proof)
        self.assertEqual(calls["concurrency_limit"], 2)

    def test_adapter_failure_routes_to_retry(self) -> None:
        class Backend:
            def create(self, capability: str, bundle: dict[str, object]) -> str: return capability
            def send(self, handle: str, bundle: dict[str, object]) -> None: return None
            def wait(self, handle: str) -> dict[str, object]:
                if handle == "verify": return {"outcome": "failed", "payload": {"reason": "AC1 failed"}}
                return {"outcome": "completed", "payload": {"simplification": {"result": "no_change"}}}
            def interrupt(self, handle: str) -> None: return None
            def close(self, handle: str) -> None: return None

        adapter = CapabilityAdapter(Backend())
        session = CapabilitySession()
        result = run_ticket(self.task_dir, adapter=adapter, adapter_session=session, allowed_write_scope=["engineering/loop/"], baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []})
        self.assertEqual(result.outcome, "retry")
        self.assertIsNotNone(result.session)
        self.assertEqual(json.loads((self.task_dir / "tickets" / "T001-runtime.json").read_text(encoding="utf-8"))["execution"]["attempt_sequence"], 2)
        resumed = run_ticket(
            self.task_dir,
            adapter=adapter,
            adapter_session=result.session,
            ticket_id="T001",
            allowed_write_scope=["engineering/loop/"],
            baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []},
        )
        self.assertEqual(resumed.outcome, "retry")
        self.assertEqual(json.loads((self.task_dir / "tickets" / "T001-runtime.json").read_text(encoding="utf-8"))["execution"]["attempt_sequence"], 3)

    def test_resume_rejects_a_different_write_scope(self) -> None:
        class Backend:
            def create(self, capability: str, bundle: dict[str, object]) -> str: return capability
            def send(self, handle: str, bundle: dict[str, object]) -> None: return None
            def wait(self, handle: str) -> dict[str, object]:
                if handle == "verify": return {"outcome": "failed", "payload": {"reason": "repair"}}
                return {"outcome": "completed", "payload": {"simplification": {"result": "no_change"}}}
            def interrupt(self, handle: str) -> None: return None
            def close(self, handle: str) -> None: return None

        adapter = CapabilityAdapter(Backend())
        first = run_ticket(self.task_dir, adapter=adapter, adapter_session=CapabilitySession(), allowed_write_scope=["src/"], baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []})
        self.assertEqual(first.outcome, "retry")
        resumed = run_ticket(self.task_dir, adapter=adapter, adapter_session=first.session, ticket_id="T001", allowed_write_scope=["other/"], baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []})

        self.assertEqual(resumed.outcome, "failed")
        self.assertIn("scope_mismatch", {item["code"] for item in resumed.problems})

    def test_resume_after_restart_can_create_a_fresh_session(self) -> None:
        class Backend:
            def create(self, capability: str, bundle: dict[str, object]) -> str: return capability
            def send(self, handle: str, bundle: dict[str, object]) -> None: return None
            def wait(self, handle: str) -> dict[str, object]:
                if handle == "verify": return {"outcome": "failed", "payload": {"reason": "repair"}}
                return {"outcome": "completed", "payload": {"simplification": {"result": "no_change"}}}
            def interrupt(self, handle: str) -> None: return None
            def close(self, handle: str) -> None: return None

        adapter = CapabilityAdapter(Backend())
        first = run_ticket(self.task_dir, adapter=adapter, adapter_session=CapabilitySession(), allowed_write_scope=["src/"], baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []})
        self.assertEqual(first.outcome, "retry")
        resumed = run_ticket(self.task_dir, adapter=adapter, ticket_id="T001", allowed_write_scope=["src/"], baseline={"reference": "wrong", "staged": [], "unstaged": [], "untracked": []})

        self.assertEqual(resumed.outcome, "retry")

    def test_failed_serial_receipt_routes_to_retry(self) -> None:
        result = run_ticket(
            self.task_dir,
            lambda request: receipt(outcome="failed"),
            allowed_write_scope=["src/"],
            baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []},
        )

        self.assertEqual(result.outcome, "retry")
        self.assertEqual(json.loads((self.task_dir / "tickets" / "T001-runtime.json").read_text(encoding="utf-8"))["execution"]["attempt_sequence"], 2)

    def test_interrupted_worker_leaves_ticket_in_progress_for_caller_decision(self) -> None:
        result = run_ticket(
            self.task_dir,
            lambda request: receipt(outcome="interrupted"),
            allowed_write_scope=["src/"],
            baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []},
        )

        self.assertEqual(result.outcome, "interrupted")
        self.assertEqual(json.loads((self.task_dir / "tickets" / "T001-runtime.json").read_text(encoding="utf-8"))["lifecycle"]["phase"], "in_progress")

    def test_review_failure_preserves_review_findings_for_retry(self) -> None:
        class Backend:
            def create(self, capability: str, bundle: dict[str, object]) -> str: return capability
            def send(self, handle: str, bundle: dict[str, object]) -> None: return None
            def wait(self, handle: str) -> dict[str, object]:
                if handle == "implement": return {"outcome": "completed", "payload": {"simplification": {"result": "no_change"}}}
                if handle == "verify": return {"outcome": "completed", "payload": {"acceptance_evidence": [{"acceptance_id": "AC1", "result": "passed", "summary": "ok"}], "verification": [{"command": "self-check", "exit_code": 0, "summary": "ok"}], "unverified": []}}
                return {"outcome": "failed", "payload": {"findings": "The standards review found a regression.", "review": {"standards": "failed", "spec": "pass", "hld": "pass"}}}
            def interrupt(self, handle: str) -> None: return None
            def close(self, handle: str) -> None: return None

        result = run_ticket(self.task_dir, adapter=CapabilityAdapter(Backend()), allowed_write_scope=["src/"], baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []})

        self.assertEqual(result.outcome, "retry")
        stored = json.loads((self.task_dir / "tickets" / "T001-runtime.json").read_text(encoding="utf-8"))
        self.assertEqual(stored["execution"]["reopen_context"]["review_finding"], "The standards review found a regression.")

    def test_failed_adapter_cannot_mutate_graph(self) -> None:
        class Backend:
            def create(self, capability: str, bundle: dict[str, object]) -> str: return capability
            def send(self, handle: str, bundle: dict[str, object]) -> None: return None
            def wait(self, handle: str) -> dict[str, object]:
                if handle == "verify":
                    (self.task_dir / "SPEC.md").write_text("tampered\n", encoding="utf-8")
                    return {"outcome": "failed", "payload": {"reason": "AC1 failed"}}
                return {"outcome": "completed", "payload": {"simplification": {"result": "no_change"}}}
            def interrupt(self, handle: str) -> None: return None
            def close(self, handle: str) -> None: return None

        backend = Backend()
        backend.task_dir = self.task_dir  # type: ignore[attr-defined]
        result = run_ticket(self.task_dir, adapter=CapabilityAdapter(backend), allowed_write_scope=["src/"], baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []})

        self.assertEqual(result.outcome, "failed")
        self.assertIn("worker_mutated_graph", {item["code"] for item in result.problems})

    def test_invalid_receipt_cannot_hide_graph_mutation(self) -> None:
        def worker(request: dict[str, object]) -> dict[str, object]:
            (self.task_dir / "SPEC.md").write_text("tampered\n", encoding="utf-8")
            return {}

        result = run_ticket(self.task_dir, worker, allowed_write_scope=["src/"], baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []})

        self.assertEqual(result.outcome, "failed")
        self.assertIn("worker_mutated_graph", {item["code"] for item in result.problems})

    def test_invalid_receipt_does_not_complete_ticket(self) -> None:
        result = run_ticket(self.task_dir, lambda request: receipt(acceptance_evidence=[]), allowed_write_scope=["src/"], baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []})
        self.assertEqual(result.outcome, "failed")
        stored = json.loads((self.task_dir / "tickets" / "T001-runtime.json").read_text(encoding="utf-8"))
        self.assertEqual(stored["lifecycle"]["phase"], "in_progress")

    def test_blocked_worker_persists_only_accepted_facts(self) -> None:
        result = run_ticket(
            self.task_dir,
            lambda request: receipt(
                outcome="blocked",
                acceptance_evidence=[],
                verification=[],
                review={"standards": "pass", "spec": "pass", "hld": "pass"},
                blocker={
                    "category": "environment",
                    "reason": "Runtime unavailable.",
                    "release_condition": "Runtime becomes available.",
                },
            ),
            allowed_write_scope=["src/"],
            baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []},
        )
        self.assertEqual(result.outcome, "blocked")
        stored = json.loads((self.task_dir / "tickets" / "T001-runtime.json").read_text(encoding="utf-8"))
        self.assertEqual(stored["lifecycle"]["phase"], "open")
        self.assertEqual(stored["execution"]["blocker"]["category"], "environment")

    def test_worker_cannot_modify_graph(self) -> None:
        def worker(request: dict[str, object]) -> dict[str, object]:
            (self.task_dir / "SPEC.md").write_text("tampered\n", encoding="utf-8")
            return receipt()

        result = run_ticket(self.task_dir, worker, allowed_write_scope=["src/"], baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []})
        self.assertEqual(result.outcome, "failed")
        self.assertIn("worker_mutated_graph", {item["code"] for item in result.problems})

    def test_worker_cannot_commit_with_full_access(self) -> None:
        subprocess.run(["git", "init", "-q", str(self.task_dir)], check=True)
        subprocess.run(["git", "-C", str(self.task_dir), "config", "user.email", "loop@test"], check=True)
        subprocess.run(["git", "-C", str(self.task_dir), "config", "user.name", "Loop Test"], check=True)
        subprocess.run(["git", "-C", str(self.task_dir), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(self.task_dir), "commit", "-qm", "baseline"], check=True)

        def worker(request: dict[str, object]) -> dict[str, object]:
            (self.task_dir / "src").mkdir()
            (self.task_dir / "src" / "delivery.py").write_text("value = 1\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(self.task_dir), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(self.task_dir), "commit", "-qm", "worker commit"], check=True)
            return receipt()

        result = run_ticket(
            self.task_dir,
            worker,
            workspace_root=self.task_dir,
            allowed_write_scope=["src/"],
            baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []},
        )

        self.assertEqual(result.outcome, "failed")
        self.assertIn("worker_mutated_graph", {item["code"] for item in result.problems})

    def test_worker_commit_then_failure_is_rejected(self) -> None:
        subprocess.run(["git", "init", "-q", str(self.task_dir)], check=True)
        subprocess.run(["git", "-C", str(self.task_dir), "config", "user.email", "loop@test"], check=True)
        subprocess.run(["git", "-C", str(self.task_dir), "config", "user.name", "Loop Test"], check=True)
        subprocess.run(["git", "-C", str(self.task_dir), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(self.task_dir), "commit", "-qm", "baseline"], check=True)

        def worker(request: dict[str, object]) -> dict[str, object]:
            (self.task_dir / "src").mkdir()
            (self.task_dir / "src" / "delivery.py").write_text("value = 1\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(self.task_dir), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(self.task_dir), "commit", "-qm", "worker commit"], check=True)
            raise RuntimeError("receipt generation failed")

        result = run_ticket(
            self.task_dir,
            worker,
            workspace_root=self.task_dir,
            allowed_write_scope=["src/"],
            baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []},
        )

        self.assertEqual(result.outcome, "failed")
        self.assertIn("worker_mutated_graph", {item["code"] for item in result.problems})

    def test_worker_cannot_overwrite_an_existing_dirty_file(self) -> None:
        subprocess.run(["git", "init", "-q", str(self.task_dir)], check=True)
        subprocess.run(["git", "-C", str(self.task_dir), "config", "user.email", "loop@test"], check=True)
        subprocess.run(["git", "-C", str(self.task_dir), "config", "user.name", "Loop Test"], check=True)
        (self.task_dir / "outside.py").write_text("baseline\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.task_dir), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(self.task_dir), "commit", "-qm", "baseline"], check=True)
        (self.task_dir / "outside.py").write_text("existing dirty\n", encoding="utf-8")

        def worker(request: dict[str, object]) -> dict[str, object]:
            (self.task_dir / "outside.py").write_text("worker changed\n", encoding="utf-8")
            return receipt()

        result = run_ticket(
            self.task_dir,
            worker,
            workspace_root=self.task_dir,
            allowed_write_scope=["src/"],
            baseline={"reference": "test", "staged": [], "unstaged": ["outside.py"], "untracked": []},
        )

        self.assertEqual(result.outcome, "failed")
        self.assertIn("write_scope_violation", {item["code"] for item in result.problems})

    def test_worker_cannot_hide_an_ignored_out_of_scope_file(self) -> None:
        subprocess.run(["git", "init", "-q", str(self.task_dir)], check=True)
        subprocess.run(["git", "-C", str(self.task_dir), "config", "user.email", "loop@test"], check=True)
        subprocess.run(["git", "-C", str(self.task_dir), "config", "user.name", "Loop Test"], check=True)
        (self.task_dir / ".gitignore").write_text("ignored.txt\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.task_dir), "add", ".gitignore"], check=True)
        subprocess.run(["git", "-C", str(self.task_dir), "commit", "-qm", "baseline"], check=True)

        def worker(request: dict[str, object]) -> dict[str, object]:
            (self.task_dir / "ignored.txt").write_text("worker changed\n", encoding="utf-8")
            return receipt()

        result = run_ticket(
            self.task_dir,
            worker,
            workspace_root=self.task_dir,
            allowed_write_scope=["src/"],
            baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []},
        )

        self.assertEqual(result.outcome, "failed")
        self.assertIn("write_scope_violation", {item["code"] for item in result.problems})

    def test_worker_cannot_hide_an_assume_unchanged_file(self) -> None:
        subprocess.run(["git", "init", "-q", str(self.task_dir)], check=True)
        subprocess.run(["git", "-C", str(self.task_dir), "config", "user.email", "loop@test"], check=True)
        subprocess.run(["git", "-C", str(self.task_dir), "config", "user.name", "Loop Test"], check=True)
        outside = self.task_dir / "outside.py"
        outside.write_text("baseline\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.task_dir), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(self.task_dir), "commit", "-qm", "baseline"], check=True)
        subprocess.run(["git", "-C", str(self.task_dir), "update-index", "--assume-unchanged", "outside.py"], check=True)

        def worker(request: dict[str, object]) -> dict[str, object]:
            outside.write_text("worker changed\n", encoding="utf-8")
            return receipt()

        result = run_ticket(
            self.task_dir,
            worker,
            workspace_root=self.task_dir,
            allowed_write_scope=["src/"],
            baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []},
        )

        self.assertEqual(result.outcome, "failed")
        self.assertIn("write_scope_violation", {item["code"] for item in result.problems})

    def test_receipt_identity_is_checked_on_restore(self) -> None:
        run_ticket(self.task_dir, lambda request: receipt(), allowed_write_scope=["src/"], baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []})
        with self.assertRaises(ValueError):
            load_receipt(self.task_dir, ticket_id="T999", attempt=1)
        with self.assertRaises(ValueError):
            load_receipt(self.task_dir, ticket_id="../outside", attempt=1)

    def test_reopen_uses_the_review_contract(self) -> None:
        run_ticket(self.task_dir, lambda request: receipt(), allowed_write_scope=["src/"], baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []})
        result = reopen_ticket(self.task_dir, "T001", review_finding="AC1 needs another check.", invalidated_acceptance=["AC1"])
        self.assertEqual(result.outcome, "reopened")
        stored = json.loads((self.task_dir / "tickets" / "T001-runtime.json").read_text(encoding="utf-8"))
        self.assertEqual(stored["lifecycle"]["phase"], "open")

    def test_reopen_rejects_changed_upstream_content(self) -> None:
        run_ticket(self.task_dir, lambda request: receipt(), allowed_write_scope=["src/"], baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []})
        (self.task_dir / "SPEC.md").write_text("# Spec\n\n1. **R1** — Changed wording.\n\n## Acceptance Criteria\n\n- **AC1** — Covers: R1. Changed.\n", encoding="utf-8")

        result = reopen_ticket(self.task_dir, "T001", review_finding="AC1 needs another check.", invalidated_acceptance=["AC1"])

        self.assertEqual(result.outcome, "failed")
        self.assertIn("upstream_changed", {item["code"] for item in result.problems})

    def test_dispatch_defaults_to_serial_without_isolation_proof(self) -> None:
        second = ticket()
        second["id"] = "T002"
        (self.task_dir / "tickets" / "T002-runtime.json").write_text(json.dumps(second) + "\n", encoding="utf-8")
        active = 0
        maximum = 0
        lock = threading.Lock()

        def worker(request: dict[str, object]) -> dict[str, object]:
            nonlocal active, maximum
            with lock:
                active += 1
                maximum = max(maximum, active)
            time.sleep(0.05)
            value = receipt(ticket_id=request["ticket"]["id"])  # type: ignore[index]
            with lock:
                active -= 1
            return value

        results = dispatch_ready(self.task_dir, worker, concurrency_limit=2, allowed_write_scope=["src/"], baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []})
        self.assertEqual([item.outcome for item in results], ["completed", "completed"])
        self.assertEqual(maximum, 1)

    def test_dispatch_keeps_ticket_workers_serial_in_a_shared_workspace(self) -> None:
        second = ticket()
        second["id"] = "T002"
        (self.task_dir / "tickets" / "T002-runtime.json").write_text(json.dumps(second) + "\n", encoding="utf-8")
        active = 0
        maximum = 0
        lock = threading.Lock()

        def worker(request: dict[str, object]) -> dict[str, object]:
            nonlocal active, maximum
            with lock:
                active += 1
                maximum = max(maximum, active)
            time.sleep(0.05)
            value = receipt(ticket_id=request["ticket"]["id"])  # type: ignore[index]
            with lock:
                active -= 1
            return value

        proof = {"dependencies": True, "write_scope": True, "shared_side_effects": True, "integration_order": True}
        results = dispatch_ready(self.task_dir, worker, concurrency_limit=2, isolation_proof=proof, allowed_write_scope=["src/"], baseline={"reference": "test", "staged": [], "unstaged": [], "untracked": []})
        self.assertEqual([item.outcome for item in results], ["completed", "completed"])
        self.assertEqual(maximum, 1)


if __name__ == "__main__":
    unittest.main()
