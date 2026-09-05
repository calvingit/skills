from __future__ import annotations

import json
import re
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "ticket_graph.py"
SCHEMAS = Path(__file__).parents[1] / "schemas"
REPOSITORY = Path(__file__).parents[3]


def schema_errors(
    value: object,
    schema: dict[str, object],
    root: dict[str, object],
    path: str = "$",
) -> list[str]:
    if "$ref" in schema:
        target: object = root
        for part in str(schema["$ref"]).removeprefix("#/").split("/"):
            target = target[part]  # type: ignore[index]
        return schema_errors(value, target, root, path)  # type: ignore[arg-type]
    if "oneOf" in schema:
        matches = [
            branch
            for branch in schema["oneOf"]  # type: ignore[union-attr]
            if not schema_errors(value, branch, root, path)
        ]
        return [] if len(matches) == 1 else [f"{path}: expected exactly one matching schema"]

    errors: list[str] = []
    expected_type = schema.get("type")
    type_names = expected_type if isinstance(expected_type, list) else [expected_type]
    checks = {
        "object": lambda item: isinstance(item, dict),
        "array": lambda item: isinstance(item, list),
        "string": lambda item: isinstance(item, str),
        "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
        "null": lambda item: item is None,
    }
    if expected_type is not None and not any(checks[name](value) for name in type_names):
        return [f"{path}: invalid type"]
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: invalid constant")
    if "enum" in schema and value not in schema["enum"]:  # type: ignore[operator]
        errors.append(f"{path}: value is outside enum")
    if isinstance(value, str):
        if len(value) < int(schema.get("minLength", 0)):
            errors.append(f"{path}: string is too short")
        if "pattern" in schema and not re.fullmatch(str(schema["pattern"]), value):
            errors.append(f"{path}: string does not match pattern")
    if isinstance(value, int) and not isinstance(value, bool) and "minimum" in schema:
        if value < int(schema["minimum"]):
            errors.append(f"{path}: integer is below minimum")
    if isinstance(value, list):
        if len(value) < int(schema.get("minItems", 0)):
            errors.append(f"{path}: array is too short")
        if schema.get("uniqueItems") and len({json.dumps(item, sort_keys=True) for item in value}) != len(value):
            errors.append(f"{path}: array items are not unique")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(schema_errors(item, item_schema, root, f"{path}[{index}]"))
    if isinstance(value, dict):
        required = set(schema.get("required", []))
        properties = schema.get("properties", {})
        for name in sorted(required - value.keys()):
            errors.append(f"{path}.{name}: missing")
        if schema.get("additionalProperties") is False:
            for name in sorted(value.keys() - properties.keys()):  # type: ignore[union-attr]
                errors.append(f"{path}.{name}: unknown")
        for name, item in value.items():
            child = properties.get(name) if isinstance(properties, dict) else None
            if isinstance(child, dict):
                errors.extend(schema_errors(item, child, root, f"{path}.{name}"))
            elif isinstance(schema.get("additionalProperties"), dict):
                errors.extend(
                    schema_errors(item, schema["additionalProperties"], root, f"{path}.{name}")  # type: ignore[arg-type]
                )
    return errors


def canonical_ticket(**overrides: object) -> dict[str, object]:
    ticket: dict[str, object] = {
        "schema_version": 1,
        "id": "T001",
        "title": "Example delivery",
        "covers": {"requirements": ["R1"], "spec_acceptance": ["AC1"]},
        "design_decisions": ["D1"],
        "what_to_build": "Deliver one observable behavior.",
        "constraints": ["Preserve the confirmed contract."],
        "acceptance_criteria": [
            {"id": "AC1", "description": "The behavior is observable."}
        ],
        "dependencies": [],
        "lifecycle": {"phase": "open"},
        "execution": {
            "attempt_sequence": 0,
            "evidence": {},
            "blocker": None,
            "current_attempt": None,
            "reopen_context": None,
        },
        "supersession": None,
    }
    ticket.update(overrides)
    return ticket


def canonical_receipt(**overrides: object) -> dict[str, object]:
    receipt: dict[str, object] = {
        "schema_version": 1,
        "outcome": "completed",
        "ticket_id": "T001",
        "current_attempt": 1,
        "landed_changes": [{"path": "example.py", "summary": "Delivered behavior."}],
        "acceptance_evidence": [
            {"acceptance_id": "AC1", "result": "passed", "summary": "Verified."}
        ],
        "verification": [{"command": "test", "exit_code": 0, "summary": "Passed."}],
        "simplification": {"result": "completed"},
        "review": {"standards": "pass", "spec": "pass", "hld": "pass"},
        "blocker": None,
        "unverified": [],
    }
    receipt.update(overrides)
    return receipt


class TicketGraphCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.task_dir = Path(self.temporary_directory.name)
        (self.task_dir / "tickets").mkdir()
        (self.task_dir / "SPEC.md").write_text(
            "# Spec\n\n## User Stories\n\n1. **R1** — Behavior.\n\n"
            "## Acceptance Criteria\n\n- **AC1** — Covers: R1. Observable.\n",
            encoding="utf-8",
        )
        (self.task_dir / "HLD.md").write_text(
            "# HLD\n\n## Design Decisions\n\n- **D1** — Shared decision.\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_ticket(
        self, ticket: dict[str, object], filename: str = "T001-example-delivery.json"
    ) -> Path:
        path = self.task_dir / "tickets" / filename
        path.write_text(json.dumps(ticket, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path

    def write_request(self, value: dict[str, object]) -> Path:
        path = self.task_dir / "request.json"
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path

    def run_cli(self, *arguments: str) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            check=False,
            capture_output=True,
            text=True,
        )
        return result, json.loads(result.stdout)

    def prepare_switching_transaction(
        self, original: dict[str, object], target: dict[str, object]
    ) -> tuple[Path, Path]:
        ticket_path = self.write_ticket(original)
        transaction = self.task_dir / ".ticket-graph-transaction"
        staging = transaction / "staging"
        backup = transaction / "backup"
        (staging / "tickets").mkdir(parents=True)
        (backup / "tickets").mkdir(parents=True)
        shutil.copy2(self.task_dir / "SPEC.md", staging / "SPEC.md")
        shutil.copy2(self.task_dir / "HLD.md", staging / "HLD.md")
        relative = ticket_path.relative_to(self.task_dir)
        shutil.copy2(ticket_path, backup / relative)
        (staging / relative).write_text(
            json.dumps(target, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        (transaction / "manifest.json").write_text(
            json.dumps(
                {
                    "operation": "test",
                    "state": "switching",
                    "original_files": [relative.as_posix()],
                    "target_files": [relative.as_posix()],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return ticket_path, staging / relative

    def test_inspect_returns_the_canonical_graph_projection(self) -> None:
        self.write_ticket(canonical_ticket())

        result, payload = self.run_cli("inspect", str(self.task_dir))

        self.assertEqual(result.returncode, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["operation"], "inspect")
        self.assertEqual(payload["problems"], [])
        self.assertEqual(payload["graph"]["frontier"], ["T001"])
        self.assertEqual(payload["graph"]["blocked"], [])
        self.assertEqual(payload["graph"]["all_active_done"], False)

    def test_invalid_ticket_contracts_return_structured_problems(self) -> None:
        cases: list[tuple[dict[str, object], str]] = []

        missing_title = canonical_ticket()
        del missing_title["title"]
        cases.append((missing_title, "missing_field"))

        persisted_readiness = canonical_ticket(readiness="ready")
        cases.append((persisted_readiness, "unknown_field"))

        invalid_phase = canonical_ticket(lifecycle={"phase": "ready"})
        cases.append((invalid_phase, "invalid_field"))

        invalid_phase_type = canonical_ticket(lifecycle={"phase": {"unexpected": True}})
        cases.append((invalid_phase_type, "invalid_field"))

        unsupported_version = canonical_ticket(schema_version=2)
        cases.append((unsupported_version, "unsupported_schema_version"))

        for ticket, expected_code in cases:
            with self.subTest(expected_code=expected_code):
                self.write_ticket(ticket)
                result, payload = self.run_cli("inspect", str(self.task_dir))
                self.assertEqual(result.returncode, 1)
                self.assertFalse(payload["ok"])
                self.assertIn(expected_code, {item["code"] for item in payload["problems"]})

    def test_public_schemas_define_closed_v1_contracts(self) -> None:
        ticket_schema = json.loads((SCHEMAS / "ticket.schema.json").read_text(encoding="utf-8"))
        receipt_schema = json.loads(
            (SCHEMAS / "worker-receipt.schema.json").read_text(encoding="utf-8")
        )

        self.assertEqual(ticket_schema["properties"]["schema_version"]["const"], 1)
        self.assertFalse(ticket_schema["additionalProperties"])
        self.assertEqual(set(ticket_schema["required"]), set(canonical_ticket()))
        self.assertEqual(receipt_schema["properties"]["schema_version"]["const"], 1)
        self.assertFalse(receipt_schema["additionalProperties"])
        self.assertIn("acceptance_evidence", receipt_schema["required"])
        self.assertEqual(schema_errors(canonical_ticket(), ticket_schema, ticket_schema), [])
        self.assertEqual(schema_errors(canonical_receipt(), receipt_schema, receipt_schema), [])
        self.assertTrue(
            schema_errors(canonical_ticket(readiness="ready"), ticket_schema, ticket_schema)
        )

    def test_markdown_only_graph_is_rejected(self) -> None:
        (self.task_dir / "tickets" / "01-legacy.md").write_text("# Legacy\n", encoding="utf-8")

        result, payload = self.run_cli("inspect", str(self.task_dir))

        self.assertEqual(result.returncode, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("unsupported_markdown_ticket", {item["code"] for item in payload["problems"]})

    def test_unknown_authority_references_and_coverage_gaps_are_reported(self) -> None:
        ticket = canonical_ticket(
            covers={"requirements": ["R2"], "spec_acceptance": ["AC2"]},
            design_decisions=["D2"],
        )
        self.write_ticket(ticket)

        result, payload = self.run_cli("inspect", str(self.task_dir))

        self.assertEqual(result.returncode, 1)
        codes = {item["code"] for item in payload["problems"]}
        self.assertTrue(
            {"unknown_requirement", "unknown_spec_acceptance", "unknown_design_decision", "coverage_gap"}
            <= codes
        )

    def test_duplicate_ticket_ids_are_rejected(self) -> None:
        self.write_ticket(canonical_ticket(), "T001-first.json")
        self.write_ticket(canonical_ticket(), "T001-second.json")

        result, payload = self.run_cli("inspect", str(self.task_dir))

        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate_ticket_id", {item["code"] for item in payload["problems"]})

    def test_dependency_cycles_are_rejected(self) -> None:
        self.write_ticket(canonical_ticket(dependencies=["T002"]), "T001-first.json")
        second = canonical_ticket(id="T002", dependencies=["T001"])
        self.write_ticket(second, "T002-second.json")

        result, payload = self.run_cli("inspect", str(self.task_dir))

        self.assertEqual(result.returncode, 1)
        self.assertIn("dependency_cycle", {item["code"] for item in payload["problems"]})

    def test_dependencies_on_superseded_tickets_are_rejected(self) -> None:
        superseded = canonical_ticket(
            lifecycle={"phase": "superseded"},
            supersession={"reason": "Replaced", "replacement_ticket_id": "T002"},
        )
        self.write_ticket(superseded, "T001-old.json")
        replacement = canonical_ticket(id="T002", dependencies=["T001"])
        self.write_ticket(replacement, "T002-new.json")

        result, payload = self.run_cli("inspect", str(self.task_dir))

        self.assertEqual(result.returncode, 1)
        self.assertIn("dependency_on_superseded", {item["code"] for item in payload["problems"]})

    def test_list_filters_and_show_return_read_only_ticket_views(self) -> None:
        completed = canonical_ticket(
            lifecycle={"phase": "done"},
            execution={
                "attempt_sequence": 1,
                "evidence": {"AC1": {"result": "passed", "summary": "Verified."}},
                "blocker": None,
                "current_attempt": None,
                "reopen_context": None,
            },
        )
        first_path = self.write_ticket(completed, "T001-completed.json")
        second = canonical_ticket(id="T002", dependencies=["T001"])
        second_path = self.write_ticket(second, "T002-ready.json")
        before = {first_path: first_path.read_bytes(), second_path: second_path.read_bytes()}

        list_result, list_payload = self.run_cli(
            "list", str(self.task_dir), "--phase", "open", "--readiness", "ready"
        )
        show_result, show_payload = self.run_cli("show", str(self.task_dir), "T002")

        self.assertEqual(list_result.returncode, 0)
        self.assertEqual([item["id"] for item in list_payload["result"]["tickets"]], ["T002"])
        self.assertEqual(list_payload["result"]["tickets"][0]["readiness"], "ready")
        self.assertEqual(show_result.returncode, 0)
        self.assertEqual(show_payload["result"]["ticket"]["id"], "T002")
        self.assertEqual(show_payload["result"]["readiness"], "ready")
        self.assertEqual(before, {first_path: first_path.read_bytes(), second_path: second_path.read_bytes()})

    def test_argument_and_missing_ticket_failures_are_json_envelopes(self) -> None:
        self.write_ticket(canonical_ticket())

        invalid_result, invalid_payload = self.run_cli("list", str(self.task_dir), "--phase")
        missing_result, missing_payload = self.run_cli("show", str(self.task_dir), "T999")

        self.assertEqual(invalid_result.returncode, 2)
        self.assertEqual(invalid_payload["problems"][0]["code"], "invalid_arguments")
        self.assertEqual(missing_result.returncode, 1)
        self.assertEqual(missing_payload["problems"][0]["code"], "unknown_ticket")
        for forbidden in ("delete", "supersede", "set-status", "patch"):
            forbidden_result, forbidden_payload = self.run_cli(
                forbidden, str(self.task_dir), "T001"
            )
            self.assertEqual(forbidden_result.returncode, 2)
            self.assertEqual(forbidden_payload["problems"][0]["code"], "invalid_arguments")

    def test_worker_receipt_runtime_validation_matches_the_public_contract(self) -> None:
        validate_worker_receipt = runpy.run_path(str(SCRIPT))["validate_worker_receipt"]

        self.assertEqual(validate_worker_receipt(canonical_receipt()), [])

        missing = canonical_receipt()
        del missing["acceptance_evidence"]
        unknown = canonical_receipt(extra="not allowed")
        invalid = canonical_receipt(outcome="done")
        invalid_type = canonical_receipt(outcome={"unexpected": True})
        self.assertIn("missing_field", {item["code"] for item in validate_worker_receipt(missing)})
        self.assertIn("unknown_field", {item["code"] for item in validate_worker_receipt(unknown)})
        self.assertIn("invalid_field", {item["code"] for item in validate_worker_receipt(invalid)})
        self.assertIn(
            "invalid_field", {item["code"] for item in validate_worker_receipt(invalid_type)}
        )

    def test_in_progress_ticket_requires_a_complete_current_attempt(self) -> None:
        ticket = canonical_ticket(
            lifecycle={"phase": "in_progress"},
            execution={
                "attempt_sequence": 1,
                "evidence": {},
                "blocker": None,
                "current_attempt": {},
                "reopen_context": None,
            },
        )
        self.write_ticket(ticket)

        result, payload = self.run_cli("inspect", str(self.task_dir))

        self.assertEqual(result.returncode, 1)
        self.assertIn("missing_field", {item["code"] for item in payload["problems"]})

    def test_readiness_keeps_dependency_and_execution_blockers_distinct(self) -> None:
        blocked = canonical_ticket(
            execution={
                "attempt_sequence": 0,
                "evidence": {},
                "blocker": {
                    "category": "environment",
                    "reason": "Runtime unavailable.",
                    "release_condition": "Runtime is available.",
                },
                "current_attempt": None,
                "reopen_context": None,
            }
        )
        self.write_ticket(blocked, "T001-environment.json")
        dependent = canonical_ticket(id="T002", dependencies=["T001"])
        self.write_ticket(dependent, "T002-dependent.json")

        result, payload = self.run_cli("inspect", str(self.task_dir))

        self.assertEqual(result.returncode, 0)
        by_id = {item["ticket_id"]: item for item in payload["graph"]["blocked"]}
        self.assertEqual(by_id["T001"]["reasons"][0]["source"], "execution")
        self.assertEqual(by_id["T002"]["reasons"][0], {"source": "dependency", "ticket_id": "T001"})

    def test_superseded_ticket_cannot_keep_execution_state(self) -> None:
        superseded = canonical_ticket(
            lifecycle={"phase": "superseded"},
            execution={
                "attempt_sequence": 1,
                "evidence": {},
                "blocker": {
                    "category": "external",
                    "reason": "Still waiting.",
                    "release_condition": "External change arrives.",
                },
                "current_attempt": None,
                "reopen_context": None,
            },
            supersession={"reason": "Replaced", "replacement_ticket_id": "T002"},
        )
        self.write_ticket(superseded, "T001-old.json")
        self.write_ticket(canonical_ticket(id="T002"), "T002-current.json")

        result, payload = self.run_cli("inspect", str(self.task_dir))

        self.assertEqual(result.returncode, 1)
        self.assertIn("superseded_execution_state", {item["code"] for item in payload["problems"]})

    def test_supersession_replacement_must_resolve_to_an_active_ticket(self) -> None:
        superseded = canonical_ticket(
            lifecycle={"phase": "superseded"},
            supersession={"reason": "Replaced", "replacement_ticket_id": "T999"},
        )
        self.write_ticket(superseded, "T001-old.json")
        self.write_ticket(canonical_ticket(id="T002"), "T002-current.json")

        result, payload = self.run_cli("inspect", str(self.task_dir))

        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid_supersession_replacement", {item["code"] for item in payload["problems"]})

    def test_start_persists_an_attempt_only_for_a_ready_open_ticket(self) -> None:
        path = self.write_ticket(canonical_ticket())
        request = self.write_request(
            {
                "baseline": {
                    "reference": "working tree snapshot",
                    "staged": [],
                    "unstaged": ["existing.py"],
                    "untracked": [],
                },
                "existing_changes": {"included": [], "excluded": ["existing.py"]},
                "allowed_write_scope": ["delivery.py"],
            }
        )

        result, payload = self.run_cli(
            "start", str(self.task_dir), "T001", "--input", str(request)
        )

        self.assertEqual(result.returncode, 0)
        self.assertTrue(payload["ok"])
        stored = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(stored["lifecycle"]["phase"], "in_progress")
        self.assertEqual(stored["execution"]["attempt_sequence"], 1)
        self.assertEqual(stored["execution"]["current_attempt"]["number"], 1)
        self.assertEqual(stored["execution"]["current_attempt"]["allowed_write_scope"], ["delivery.py"])

        blocked = canonical_ticket(
            execution={
                "attempt_sequence": 0,
                "evidence": {},
                "blocker": {
                    "category": "environment",
                    "reason": "Runtime unavailable.",
                    "release_condition": "Runtime is available.",
                },
                "current_attempt": None,
                "reopen_context": None,
            }
        )
        path.write_text(json.dumps(blocked, indent=2) + "\n", encoding="utf-8")
        before = path.read_bytes()
        blocked_result, blocked_payload = self.run_cli(
            "start", str(self.task_dir), "T001", "--input", str(request)
        )
        self.assertEqual(blocked_result.returncode, 1)
        self.assertEqual(blocked_payload["problems"][0]["code"], "ticket_not_ready")
        self.assertEqual(path.read_bytes(), before)

    def test_block_and_unblock_preserve_the_execution_boundary(self) -> None:
        ticket = canonical_ticket(
            lifecycle={"phase": "in_progress"},
            execution={
                "attempt_sequence": 1,
                "evidence": {},
                "blocker": None,
                "current_attempt": {
                    "number": 1,
                    "baseline": {
                        "reference": "snapshot",
                        "staged": [],
                        "unstaged": [],
                        "untracked": [],
                    },
                    "existing_changes": {"included": [], "excluded": []},
                    "allowed_write_scope": ["delivery.py"],
                },
                "reopen_context": None,
            },
        )
        path = self.write_ticket(ticket)
        block_request = self.write_request(
            {
                "blocker": {
                    "category": "environment",
                    "reason": "Runtime unavailable.",
                    "release_condition": "Runtime is available.",
                },
                "evidence": {"AC1": {"result": "passed", "summary": "Partial behavior verified."}},
            }
        )

        block_result, _ = self.run_cli(
            "block", str(self.task_dir), "T001", "--input", str(block_request)
        )

        self.assertEqual(block_result.returncode, 0)
        stored = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(stored["lifecycle"]["phase"], "open")
        self.assertIsNone(stored["execution"]["current_attempt"])
        self.assertEqual(stored["execution"]["blocker"]["category"], "environment")
        self.assertEqual(stored["execution"]["evidence"]["AC1"]["result"], "passed")

        invalid_request = self.write_request({"release_evidence": ""})
        before = path.read_bytes()
        invalid_result, _ = self.run_cli(
            "unblock", str(self.task_dir), "T001", "--input", str(invalid_request)
        )
        self.assertEqual(invalid_result.returncode, 1)
        self.assertEqual(path.read_bytes(), before)

        unblock_request = self.write_request(
            {"release_evidence": "The required runtime verification now exits 0."}
        )
        unblock_result, _ = self.run_cli(
            "unblock", str(self.task_dir), "T001", "--input", str(unblock_request)
        )
        self.assertEqual(unblock_result.returncode, 0)
        self.assertIsNone(json.loads(path.read_text(encoding="utf-8"))["execution"]["blocker"])

    def test_block_rejects_dependency_as_an_execution_blocker(self) -> None:
        ticket = canonical_ticket(
            lifecycle={"phase": "in_progress"},
            execution={
                "attempt_sequence": 1,
                "evidence": {},
                "blocker": None,
                "current_attempt": {
                    "number": 1,
                    "baseline": {"reference": "snapshot", "staged": [], "unstaged": [], "untracked": []},
                    "existing_changes": {"included": [], "excluded": []},
                    "allowed_write_scope": [],
                },
                "reopen_context": None,
            },
        )
        path = self.write_ticket(ticket)
        request = self.write_request(
            {
                "blocker": {
                    "category": "dependency",
                    "reason": "Another ticket is pending.",
                    "release_condition": "The ticket completes.",
                },
                "evidence": {},
            }
        )
        before = path.read_bytes()

        result, payload = self.run_cli(
            "block", str(self.task_dir), "T001", "--input", str(request)
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid_field", {item["code"] for item in payload["problems"]})
        self.assertEqual(path.read_bytes(), before)

    def test_complete_and_reopen_enforce_evidence_and_review_gates(self) -> None:
        ticket = canonical_ticket(
            acceptance_criteria=[
                {"id": "AC1", "description": "First behavior."},
                {"id": "AC2", "description": "Second behavior."},
            ],
            lifecycle={"phase": "in_progress"},
            execution={
                "attempt_sequence": 1,
                "evidence": {},
                "blocker": None,
                "current_attempt": {
                    "number": 1,
                    "baseline": {"reference": "snapshot", "staged": [], "unstaged": [], "untracked": []},
                    "existing_changes": {"included": [], "excluded": []},
                    "allowed_write_scope": ["delivery.py"],
                },
                "reopen_context": None,
            },
        )
        path = self.write_ticket(ticket)
        incomplete_request = self.write_request(
            {
                "evidence": {"AC1": {"result": "passed", "summary": "First verified."}},
                "verification": [{"command": "test", "exit_code": 0, "summary": "Passed."}],
                "reviews": {"standards": "pass", "spec": "pass", "hld": "pass"},
                "unverified": [],
            }
        )
        before = path.read_bytes()

        incomplete_result, incomplete_payload = self.run_cli(
            "complete", str(self.task_dir), "T001", "--input", str(incomplete_request)
        )

        self.assertEqual(incomplete_result.returncode, 1)
        self.assertIn(
            "done_without_acceptance_evidence",
            {item["code"] for item in incomplete_payload["problems"]},
        )
        self.assertEqual(path.read_bytes(), before)

        complete_request = self.write_request(
            {
                "evidence": {
                    "AC1": {"result": "passed", "summary": "First verified."},
                    "AC2": {"result": "passed", "summary": "Second verified."},
                },
                "verification": [{"command": "test", "exit_code": 0, "summary": "Passed."}],
                "reviews": {"standards": "pass", "spec": "pass", "hld": "pass"},
                "unverified": [],
            }
        )
        complete_result, _ = self.run_cli(
            "complete", str(self.task_dir), "T001", "--input", str(complete_request)
        )
        self.assertEqual(complete_result.returncode, 0)
        completed = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(completed["lifecycle"]["phase"], "done")
        self.assertIsNone(completed["execution"]["current_attempt"])

        reopen_request = self.write_request(
            {
                "review_finding": "The second behavior does not meet the original contract.",
                "invalidated_acceptance": ["AC2"],
                "upstream_unchanged": True,
            }
        )
        reopen_result, _ = self.run_cli(
            "reopen", str(self.task_dir), "T001", "--input", str(reopen_request)
        )
        self.assertEqual(reopen_result.returncode, 0)
        reopened = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(reopened["lifecycle"]["phase"], "open")
        self.assertEqual(set(reopened["execution"]["evidence"]), {"AC1"})
        self.assertEqual(reopened["execution"]["reopen_context"]["invalidated_acceptance"], ["AC2"])

    def test_complete_rejects_failed_reviews_or_unverified_scope(self) -> None:
        ticket = canonical_ticket(
            lifecycle={"phase": "in_progress"},
            execution={
                "attempt_sequence": 1,
                "evidence": {},
                "blocker": None,
                "current_attempt": {
                    "number": 1,
                    "baseline": {"reference": "snapshot", "staged": [], "unstaged": [], "untracked": []},
                    "existing_changes": {"included": [], "excluded": []},
                    "allowed_write_scope": [],
                },
                "reopen_context": None,
            },
        )
        path = self.write_ticket(ticket)
        request = self.write_request(
            {
                "evidence": {"AC1": {"result": "passed", "summary": "Verified."}},
                "verification": [{"command": "test", "exit_code": 0, "summary": "Passed."}],
                "reviews": {"standards": "pass", "spec": "failed", "hld": "pass"},
                "unverified": ["A required edge case."],
            }
        )
        before = path.read_bytes()

        result, payload = self.run_cli(
            "complete", str(self.task_dir), "T001", "--input", str(request)
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("completion_gate_failed", {item["code"] for item in payload["problems"]})
        self.assertEqual(path.read_bytes(), before)

    def test_create_batch_allocates_ids_and_resolves_temporary_dependencies(self) -> None:
        request = self.write_request(
            {
                "tickets": [
                    {
                        "key": "foundation",
                        "title": "Foundation",
                        "covers": {"requirements": ["R1"], "spec_acceptance": ["AC1"]},
                        "design_decisions": ["D1"],
                        "what_to_build": "Deliver the foundation.",
                        "constraints": ["Preserve the contract."],
                        "acceptance_criteria": [
                            {"id": "AC1", "description": "Foundation is observable."}
                        ],
                        "dependencies": [],
                    },
                    {
                        "key": "consumer",
                        "title": "Consumer behavior",
                        "covers": {"requirements": ["R1"], "spec_acceptance": ["AC1"]},
                        "design_decisions": ["D1"],
                        "what_to_build": "Consume the foundation.",
                        "constraints": ["Use the confirmed foundation."],
                        "acceptance_criteria": [
                            {"id": "AC1", "description": "Consumer behavior is observable."}
                        ],
                        "dependencies": ["foundation"],
                    },
                ]
            }
        )

        result, payload = self.run_cli(
            "create-batch", str(self.task_dir), "--input", str(request)
        )

        self.assertEqual(result.returncode, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(
            [(item["key"], item["id"]) for item in payload["result"]["created"]],
            [("foundation", "T001"), ("consumer", "T002")],
        )
        files = sorted((self.task_dir / "tickets").glob("*.json"))
        self.assertEqual([path.name.split("-", 1)[0] for path in files], ["T001", "T002"])
        stored = [json.loads(path.read_text(encoding="utf-8")) for path in files]
        self.assertEqual(stored[0]["lifecycle"]["phase"], "open")
        self.assertEqual(stored[1]["dependencies"], ["T001"])
        self.assertEqual(payload["graph"]["frontier"], ["T001"])

    def test_create_batch_rejects_malformed_candidates_without_creating_files(self) -> None:
        request = self.write_request(
            {
                "tickets": [
                    {
                        "key": "invalid",
                        "title": {"not": "a string"},
                        "covers": {"requirements": ["R1"], "spec_acceptance": ["AC1"]},
                        "design_decisions": ["D1"],
                        "what_to_build": "Invalid candidate.",
                        "constraints": ["Preserve the contract."],
                        "acceptance_criteria": [
                            {"id": "AC1", "description": "Observable."}
                        ],
                        "dependencies": [],
                    }
                ]
            }
        )

        result, payload = self.run_cli(
            "create-batch", str(self.task_dir), "--input", str(request)
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid_field", {item["code"] for item in payload["problems"]})
        self.assertEqual(list((self.task_dir / "tickets").glob("*.json")), [])

    def test_reconcile_batch_commits_replacement_lineage_and_dependency_reconnect(self) -> None:
        self.write_ticket(canonical_ticket(), "T001-old.json")
        self.write_ticket(canonical_ticket(id="T002", dependencies=["T001"]), "T002-consumer.json")
        request = self.write_request(
            {
                "reason": "The confirmed delivery graph changed.",
                "operations": [
                    {
                        "operation": "create",
                        "key": "replacement",
                        "ticket": {
                            "title": "Replacement",
                            "covers": {"requirements": ["R1"], "spec_acceptance": ["AC1"]},
                            "design_decisions": ["D1"],
                            "what_to_build": "Replace the original delivery.",
                            "constraints": ["Preserve the confirmed behavior."],
                            "acceptance_criteria": [
                                {"id": "AC1", "description": "Replacement is observable."}
                            ],
                            "dependencies": [],
                        },
                    },
                    {
                        "operation": "supersede",
                        "ticket_id": "T001",
                        "replacement": "replacement",
                        "reason": "The original delivery boundary was replaced.",
                    },
                    {
                        "operation": "replace_dependency",
                        "ticket_id": "T002",
                        "from": "T001",
                        "to": "replacement",
                    },
                ],
            }
        )

        result, payload = self.run_cli(
            "reconcile-batch", str(self.task_dir), "--input", str(request)
        )

        self.assertEqual(result.returncode, 0)
        self.assertTrue(payload["ok"])
        by_id = {
            ticket["id"]: ticket
            for ticket in (
                json.loads(path.read_text(encoding="utf-8"))
                for path in (self.task_dir / "tickets").glob("*.json")
            )
        }
        self.assertEqual(by_id["T001"]["lifecycle"]["phase"], "superseded")
        self.assertEqual(by_id["T001"]["supersession"]["replacement_ticket_id"], "T003")
        self.assertEqual(by_id["T002"]["dependencies"], ["T003"])
        self.assertEqual(by_id["T003"]["lifecycle"]["phase"], "open")

    def test_reconcile_batch_rejects_an_invalid_prospective_graph_without_writes(self) -> None:
        first = self.write_ticket(canonical_ticket(), "T001-old.json")
        second = self.write_ticket(
            canonical_ticket(id="T002", dependencies=["T001"]), "T002-consumer.json"
        )
        before = {first: first.read_bytes(), second: second.read_bytes()}
        request = self.write_request(
            {
                "reason": "Invalid plan without dependency reconnect.",
                "operations": [
                    {
                        "operation": "supersede",
                        "ticket_id": "T001",
                        "replacement": None,
                        "reason": "Removed without replacement.",
                    }
                ],
            }
        )

        result, payload = self.run_cli(
            "reconcile-batch", str(self.task_dir), "--input", str(request)
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("dependency_on_superseded", {item["code"] for item in payload["problems"]})
        self.assertEqual(before, {first: first.read_bytes(), second: second.read_bytes()})

    def test_recover_rollback_restores_the_pre_transaction_graph(self) -> None:
        original = canonical_ticket()
        target = canonical_ticket(
            lifecycle={"phase": "done"},
            execution={
                "attempt_sequence": 1,
                "evidence": {"AC1": {"result": "passed", "summary": "Verified."}},
                "blocker": None,
                "current_attempt": None,
                "reopen_context": None,
            },
        )
        ticket_path, staged_path = self.prepare_switching_transaction(original, target)
        shutil.copy2(staged_path, ticket_path)

        inspect_result, inspect_payload = self.run_cli("inspect", str(self.task_dir))
        recover_result, recover_payload = self.run_cli(
            "recover", str(self.task_dir), "rollback"
        )

        self.assertEqual(inspect_result.returncode, 1)
        self.assertEqual(inspect_payload["problems"][0]["code"], "recovery_required")
        self.assertEqual(recover_result.returncode, 0)
        self.assertTrue(recover_payload["ok"])
        self.assertEqual(json.loads(ticket_path.read_text(encoding="utf-8")), original)
        self.assertFalse((self.task_dir / ".ticket-graph-transaction").exists())

    def test_recover_commit_accepts_only_a_valid_staged_graph(self) -> None:
        original = canonical_ticket()
        target = canonical_ticket(
            lifecycle={"phase": "done"},
            execution={
                "attempt_sequence": 1,
                "evidence": {"AC1": {"result": "passed", "summary": "Verified."}},
                "blocker": None,
                "current_attempt": None,
                "reopen_context": None,
            },
        )
        ticket_path, _ = self.prepare_switching_transaction(original, target)

        result, payload = self.run_cli("recover", str(self.task_dir), "commit")

        self.assertEqual(result.returncode, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(json.loads(ticket_path.read_text(encoding="utf-8")), target)

        invalid = canonical_ticket(schema_version=2)
        self.prepare_switching_transaction(original, invalid)
        before = ticket_path.read_bytes()
        invalid_result, invalid_payload = self.run_cli(
            "recover", str(self.task_dir), "commit"
        )
        self.assertEqual(invalid_result.returncode, 1)
        self.assertIn(
            "unsupported_schema_version",
            {item["code"] for item in invalid_payload["problems"]},
        )
        self.assertEqual(ticket_path.read_bytes(), before)
        self.assertTrue((self.task_dir / ".ticket-graph-transaction").exists())

    def test_migrate_check_is_read_only_for_the_initial_current_version(self) -> None:
        path = self.write_ticket(canonical_ticket())
        before = path.read_bytes()

        check_result, check_payload = self.run_cli(
            "migrate", str(self.task_dir), "--check"
        )
        migrate_result, migrate_payload = self.run_cli("migrate", str(self.task_dir))

        self.assertEqual(check_result.returncode, 0)
        self.assertEqual(check_payload["result"]["plan"], [])
        self.assertFalse(check_payload["result"]["migration_required"])
        self.assertEqual(migrate_result.returncode, 0)
        self.assertFalse(migrate_payload["result"]["migrated"])
        self.assertEqual(path.read_bytes(), before)

    def test_migrate_rejects_versions_without_an_explicit_adjacent_path(self) -> None:
        path = self.write_ticket(canonical_ticket(schema_version=0))
        before = path.read_bytes()

        result, payload = self.run_cli("migrate", str(self.task_dir), "--check")

        self.assertEqual(result.returncode, 1)
        self.assertEqual(payload["problems"][0]["code"], "unsupported_migration_path")
        self.assertEqual(path.read_bytes(), before)

    def test_migrate_rejects_markdown_without_conversion(self) -> None:
        legacy = self.task_dir / "tickets" / "01-legacy.md"
        legacy.write_text("# Legacy graph\n", encoding="utf-8")

        result, payload = self.run_cli("migrate", str(self.task_dir), "--check")

        self.assertEqual(result.returncode, 1)
        self.assertEqual(payload["problems"][0]["code"], "unsupported_markdown_ticket")
        self.assertEqual(legacy.read_text(encoding="utf-8"), "# Legacy graph\n")

    def test_workflow_contract_docs_are_json_only_and_command_aligned(self) -> None:
        paths = [
            REPOSITORY / "README.md",
            REPOSITORY / "engineering" / "loop" / "SKILL.md",
            REPOSITORY / "engineering" / "to-tickets" / "SKILL.md",
            REPOSITORY / "engineering" / "loop" / "references" / "ticket-worker.md",
            REPOSITORY / "engineering" / "execution-graph" / "README.md",
            REPOSITORY / "docs" / "ticket-lifecycle.lifecycle.json",
            REPOSITORY / "docs" / "engineering-workflow.workflow.json",
        ]
        text = "\n".join(path.read_text(encoding="utf-8") for path in paths)

        self.assertNotIn("tickets/*.md", text)
        self.assertNotIn("inspect_graph.py", text)
        self.assertIn("tickets/*.json", text)
        self.assertIn("create-batch", text)
        self.assertIn("reconcile-batch", text)
        self.assertIn("worker-receipt.schema.json", text)
        self.assertIn("open", text)
        self.assertIn("superseded", text)


if __name__ == "__main__":
    unittest.main()
