from __future__ import annotations

import test_bootstrap
from test_bootstrap import dump_ticket, read_state, read_ticket, runtime_entry, write_ticket
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from ticket_graph.runtime import fresh_entry


SCRIPT = Path(__file__).parent / "graph_cli.py"
SCHEMAS = Path(__file__).parents[1]
REPOSITORY = Path(__file__).parents[3]

from ticket_graph.authority import bind_authority


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
    """A valid v4 ticket: its contract plus the runtime entry currently attached."""
    ticket: dict[str, object] = {
        "schema_version": 4,
        "id": "T001",
        "title": "Example delivery",
        "covers": {"requirements": ["R1"], "spec_acceptance": ["AC1"]},
        "referenced_design_decisions": ["D1"],
        "what_to_build": "Deliver one observable behavior.",
        "constraints": ["Preserve the confirmed contract."],
        "delivery_acceptance": [
            {"id": "AC1", "description": "The behavior is observable."}
        ],
        "dependencies": [],
        "runtime": fresh_entry(),
    }
    ticket.update(overrides)
    return ticket


def contract_of(ticket: dict[str, object]) -> dict[str, object]:
    """The part of a ticket that is stored in its Markdown document."""
    return {key: value for key, value in ticket.items() if key != "runtime"}


def running_ticket(**overrides: object) -> dict[str, object]:
    """A ticket with an active attempt, as `start` leaves it."""
    ticket = canonical_ticket(runtime={
        "phase": "in_progress",
        "attempt": 1,
        "current_attempt": {
            "number": 1,
            "baseline": {"reference": "snapshot", "staged": [], "unstaged": [], "untracked": []},
            "existing_changes": {"included": [], "excluded": []},
            "allowed_write_scope": ["delivery.py"],
        },
    })
    ticket.update(overrides)
    return ticket


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
        (self.task_dir / "SOLUTION.md").write_text(
            "# Solution\n\n## Design Decisions\n\n- **D1** — Shared decision.\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_ticket(
        self, ticket: dict[str, object], filename: str = "T001-example-delivery.md"
    ) -> Path:
        return write_ticket(self.task_dir, ticket, filename)

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

    def snapshot_bytes(self) -> dict[str, bytes]:
        """Every stored byte a graph operation could change."""
        return {
            path: path.read_bytes()
            for path in [
                *(self.task_dir / "tickets").glob("*.md"),
                test_bootstrap.state_file(self.task_dir),
            ]
            if path.is_file()
        }

    def prepare_switching_transaction(
        self, original: dict[str, object], target: dict[str, object]
    ) -> tuple[Path, Path]:
        ticket_path = self.write_ticket(original)
        original_state = test_bootstrap.state_file(self.task_dir).read_bytes()
        self.write_ticket(target)
        transaction = self.task_dir / ".ticket-graph-transaction"
        staging = transaction / "staging"
        backup = transaction / "backup"
        (staging / "tickets").mkdir(parents=True)
        (backup / "tickets").mkdir(parents=True)
        shutil.copy2(self.task_dir / "SPEC.md", staging / "SPEC.md")
        if (self.task_dir / "ACCEPTANCE.md").is_file():
            shutil.copy2(self.task_dir / "ACCEPTANCE.md", staging / "ACCEPTANCE.md")
        shutil.copy2(self.task_dir / "SOLUTION.md", staging / "SOLUTION.md")
        relative = ticket_path.relative_to(self.task_dir)
        shutil.copy2(ticket_path, backup / relative)
        (staging / relative).write_text(dump_ticket(target), encoding="utf-8")
        staged = json.loads(test_bootstrap.state_file(self.task_dir).read_text(encoding="utf-8"))
        staged["tickets"][target["id"]] = target["runtime"]
        (staging / ".loop").mkdir(parents=True, exist_ok=True)
        (staging / ".loop/state.json").write_text(json.dumps(staged, indent=2) + "\n", encoding="utf-8")
        (backup / ".loop").mkdir(parents=True, exist_ok=True)
        (backup / ".loop/state.json").write_bytes(original_state)
        (transaction / "manifest.json").write_text(
            json.dumps(
                {
                    "operation": "test",
                    "state": "switching",
                    "original_files": [relative.as_posix(), ".loop/state.json"],
                    "target_files": [relative.as_posix(), ".loop/state.json"],
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
        cases.append((missing_title, "invalid_ticket_body"))

        persisted_readiness = canonical_ticket(readiness="ready")
        cases.append((persisted_readiness, "unknown_field"))

        legacy_lifecycle = canonical_ticket(lifecycle={"phase": "open"})
        cases.append((legacy_lifecycle, "unknown_field"))

        invalid_phase = canonical_ticket(runtime={"phase": "ready"})
        cases.append((invalid_phase, "invalid_field"))

        invalid_phase_type = canonical_ticket(runtime={"phase": {"unexpected": True}})
        cases.append((invalid_phase_type, "invalid_field"))

        unsupported_version = canonical_ticket(schema_version=3)
        cases.append((unsupported_version, "unsupported_schema_version"))

        for ticket, expected_code in cases:
            with self.subTest(expected_code=expected_code):
                self.write_ticket(ticket)
                result, payload = self.run_cli("inspect", str(self.task_dir))
                self.assertEqual(result.returncode, 1)
                self.assertFalse(payload["ok"])
                self.assertIn(expected_code, {item["code"] for item in payload["problems"]})

    def test_constraints_may_be_empty_but_entries_must_be_nonempty_and_unique(self) -> None:
        schema = json.loads((SCHEMAS / "ticket-schema.json").read_text(encoding="utf-8"))
        ticket = canonical_ticket(constraints=[])
        self.assertEqual(schema_errors(contract_of(ticket), schema, schema), [])
        self.write_ticket(ticket)
        result, payload = self.run_cli("inspect", str(self.task_dir))
        self.assertEqual(result.returncode, 0)
        self.assertTrue(payload["ok"])

        for constraints in ([""], ["Repeat", "Repeat"]):
            with self.subTest(constraints=constraints):
                self.write_ticket(canonical_ticket(constraints=constraints))
                result, payload = self.run_cli("inspect", str(self.task_dir))
                self.assertEqual(result.returncode, 1)
                self.assertIn("invalid_field", {item["code"] for item in payload["problems"]})

    def test_public_schemas_define_closed_contract_and_runtime_state(self) -> None:
        ticket_schema = json.loads((SCHEMAS / "ticket-schema.json").read_text(encoding="utf-8"))
        state_schema = json.loads((SCHEMAS / "runtime-state-schema.json").read_text(encoding="utf-8"))

        self.assertEqual(ticket_schema["properties"]["schema_version"]["const"], 4)
        self.assertFalse(ticket_schema["additionalProperties"])
        self.assertNotIn("lifecycle", ticket_schema["properties"])
        self.assertNotIn("execution", ticket_schema["properties"])
        self.assertEqual(schema_errors(contract_of(canonical_ticket()), ticket_schema, ticket_schema), [])
        self.assertTrue(
            schema_errors(canonical_ticket(readiness="ready"), ticket_schema, ticket_schema)
        )

        self.assertEqual(state_schema["properties"]["schema_version"]["const"], 1)
        self.assertFalse(state_schema["additionalProperties"])
        ticket_state = state_schema["$defs"]["ticket_state"]
        self.assertEqual(set(ticket_state["required"]), {"phase"})
        self.assertEqual(
            set(ticket_state["properties"]),
            {"phase", "attempt", "authority", "review", "evidence", "blocker", "current_attempt", "reopen_context"},
        )
        state = {
            "schema_version": 1,
            "tickets": {
                "T001": {"phase": "done", "attempt": 1, "evidence": {"AC1": {"attempt": 1, "summary": "Seen."}}}
            },
        }
        self.assertEqual(schema_errors(state, state_schema, state_schema), [])

    def test_markdown_without_frontmatter_is_rejected(self) -> None:
        (self.task_dir / "tickets" / "T001-legacy.md").write_text("# Legacy\n", encoding="utf-8")

        result, payload = self.run_cli("inspect", str(self.task_dir))

        self.assertEqual(result.returncode, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("missing_frontmatter", {item["code"] for item in payload["problems"]})

    def test_v3_tickets_are_not_silently_read_as_v4(self) -> None:
        self.write_ticket(canonical_ticket())
        path = self.task_dir / "tickets/T001-example-delivery.md"
        legacy = path.read_text(encoding="utf-8")
        path.write_text(
            legacy.replace("schema_version: 4", "schema_version: 3").replace(
                "dependencies: []",
                "dependencies: []\nlifecycle:\n  phase: open\nexecution:\n  attempt_sequence: 0\n  evidence: {}\n  blocker: null\n  current_attempt: null\n  reopen_context: null",
            ),
            encoding="utf-8",
        )

        result, payload = self.run_cli("inspect", str(self.task_dir))

        self.assertEqual(result.returncode, 1)
        self.assertFalse(payload["ok"])
        codes = {item["code"] for item in payload["problems"]}
        self.assertEqual(codes, {"unsupported_schema_version"})

    def test_unknown_authority_references_and_coverage_gaps_are_reported(self) -> None:
        ticket = canonical_ticket(
            covers={"requirements": ["R2"], "spec_acceptance": ["AC2"]},
            referenced_design_decisions=["D2"],
        )
        self.write_ticket(ticket)

        result, payload = self.run_cli("inspect", str(self.task_dir))

        self.assertEqual(result.returncode, 1)
        codes = {item["code"] for item in payload["problems"]}
        self.assertTrue(
            {"unknown_requirement", "unknown_spec_acceptance", "unknown_design_decision", "coverage_gap"}
            <= codes
        )

    def test_current_and_legacy_solution_decision_formats_are_accepted(self) -> None:
        for decision in ("- **D1** — Shared decision.", "- **D1:** Shared decision."):
            with self.subTest(decision=decision):
                (self.task_dir / "SOLUTION.md").write_text(
                    f"# Solution\n\n## Design Decisions\n\n{decision}\n",
                    encoding="utf-8",
                )
                self.write_ticket(canonical_ticket())

                result, payload = self.run_cli("inspect", str(self.task_dir))

                self.assertEqual(result.returncode, 0, payload)
                self.assertEqual(payload["problems"], [])

    def test_duplicate_ticket_ids_are_rejected(self) -> None:
        self.write_ticket(canonical_ticket(), "T001-first.md")
        self.write_ticket(canonical_ticket(), "T001-second.md")

        result, payload = self.run_cli("inspect", str(self.task_dir))

        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate_ticket_id", {item["code"] for item in payload["problems"]})

    def test_dependency_cycles_are_rejected(self) -> None:
        self.write_ticket(canonical_ticket(dependencies=["T002"]), "T001-first.md")
        second = canonical_ticket(id="T002", dependencies=["T001"])
        self.write_ticket(second, "T002-second.md")

        result, payload = self.run_cli("inspect", str(self.task_dir))

        self.assertEqual(result.returncode, 1)
        self.assertIn("dependency_cycle", {item["code"] for item in payload["problems"]})

    def test_dependencies_on_superseded_tickets_are_rejected(self) -> None:
        superseded = canonical_ticket(
            runtime={"phase": "superseded"},
            supersession={"reason": "Replaced", "replacement_ticket_id": "T002"},
        )
        self.write_ticket(superseded, "T001-old.md")
        replacement = canonical_ticket(id="T002", dependencies=["T001"])
        self.write_ticket(replacement, "T002-new.md")

        result, payload = self.run_cli("inspect", str(self.task_dir))

        self.assertEqual(result.returncode, 1)
        self.assertIn("dependency_on_superseded", {item["code"] for item in payload["problems"]})

    def test_list_filters_and_show_return_read_only_ticket_views(self) -> None:
        completed = canonical_ticket(
            runtime={
                "phase": "done",
                "attempt": 1,
                "evidence": {"AC1": {"attempt": 1, "summary": "Verified."}},
            },
        )
        first_path = self.write_ticket(completed, "T001-completed.md")
        second = canonical_ticket(id="T002", dependencies=["T001"])
        second_path = self.write_ticket(second, "T002-ready.md")
        before = self.snapshot_bytes()

        list_result, list_payload = self.run_cli(
            "list", str(self.task_dir), "--phase", "open", "--readiness", "ready"
        )
        show_result, show_payload = self.run_cli("show", str(self.task_dir), "T002")

        self.assertEqual(list_result.returncode, 0)
        self.assertEqual([item["id"] for item in list_payload["result"]["tickets"]], ["T002"])
        self.assertEqual(list_payload["result"]["tickets"][0]["readiness"], "ready")
        self.assertEqual(show_result.returncode, 0)
        self.assertEqual(show_payload["result"]["ticket"]["id"], "T002")
        self.assertEqual(show_payload["result"]["ticket"]["runtime"]["phase"], "open")
        self.assertEqual(show_payload["result"]["readiness"], "ready")
        self.assertEqual(before, self.snapshot_bytes())

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

    def test_in_progress_ticket_requires_a_complete_current_attempt(self) -> None:
        ticket = canonical_ticket(
            runtime={"phase": "in_progress", "attempt": 1, "current_attempt": {}},
        )
        self.write_ticket(ticket)

        result, payload = self.run_cli("inspect", str(self.task_dir))

        self.assertEqual(result.returncode, 1)
        self.assertIn("missing_field", {item["code"] for item in payload["problems"]})

    def test_readiness_keeps_dependency_and_execution_blockers_distinct(self) -> None:
        blocked = canonical_ticket(
            runtime={
                "phase": "open",
                "attempt": 0,
                "blocker": {
                    "category": "environment",
                    "reason": "Runtime unavailable.",
                    "release_condition": "Runtime is available.",
                },
            }
        )
        self.write_ticket(blocked, "T001-environment.md")
        dependent = canonical_ticket(id="T002", dependencies=["T001"])
        self.write_ticket(dependent, "T002-dependent.md")

        result, payload = self.run_cli("inspect", str(self.task_dir))

        self.assertEqual(result.returncode, 0)
        by_id = {item["ticket_id"]: item for item in payload["graph"]["blocked"]}
        self.assertEqual(by_id["T001"]["reasons"][0]["source"], "execution")
        self.assertEqual(by_id["T002"]["reasons"][0], {"source": "dependency", "ticket_id": "T001"})

    def test_superseded_ticket_cannot_keep_execution_state(self) -> None:
        superseded = canonical_ticket(
            runtime={
                "phase": "superseded",
                "attempt": 1,
                "blocker": {
                    "category": "external",
                    "reason": "Still waiting.",
                    "release_condition": "External change arrives.",
                },
            },
            supersession={"reason": "Replaced", "replacement_ticket_id": "T002"},
        )
        self.write_ticket(superseded, "T001-old.md")
        self.write_ticket(canonical_ticket(id="T002"), "T002-current.md")

        result, payload = self.run_cli("inspect", str(self.task_dir))

        self.assertEqual(result.returncode, 1)
        self.assertIn("superseded_execution_state", {item["code"] for item in payload["problems"]})

    def test_supersession_lineage_and_runtime_phase_must_agree(self) -> None:
        cases = [
            (canonical_ticket(runtime={"phase": "superseded"}), "missing_supersession"),
            (canonical_ticket(supersession={"reason": "Replaced", "replacement_ticket_id": "T002"}), "unexpected_supersession"),
        ]
        for ticket, expected in cases:
            with self.subTest(expected=expected):
                self.write_ticket(ticket, "T001-current.md")
                self.write_ticket(canonical_ticket(id="T002", dependencies=["T001"]), "T002-consumer.md")

                result, payload = self.run_cli("inspect", str(self.task_dir))

                self.assertEqual(result.returncode, 1)
                self.assertIn(expected, {item["code"] for item in payload["problems"]})

    def test_supersession_replacement_must_resolve_to_an_active_ticket(self) -> None:
        superseded = canonical_ticket(
            runtime={"phase": "superseded"},
            supersession={"reason": "Replaced", "replacement_ticket_id": "T999"},
        )
        self.write_ticket(superseded, "T001-old.md")
        self.write_ticket(canonical_ticket(id="T002"), "T002-current.md")

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
        stored = runtime_entry(self.task_dir, "T001")
        self.assertEqual(stored["phase"], "in_progress")
        self.assertEqual(stored["attempt"], 1)
        self.assertEqual(stored["current_attempt"]["number"], 1)
        self.assertEqual(stored["current_attempt"]["allowed_write_scope"], ["delivery.py"])
        self.assertEqual(read_ticket(path)["schema_version"], 4)

        blocked = canonical_ticket(
            runtime={
                "phase": "open",
                "attempt": 0,
                "blocker": {
                    "category": "environment",
                    "reason": "Runtime unavailable.",
                    "release_condition": "Runtime is available.",
                },
            }
        )
        self.write_ticket(blocked)
        before = self.snapshot_bytes()
        blocked_result, blocked_payload = self.run_cli(
            "start", str(self.task_dir), "T001", "--input", str(request)
        )
        self.assertEqual(blocked_result.returncode, 1)
        self.assertEqual(blocked_payload["problems"][0]["code"], "ticket_not_ready")
        self.assertEqual(self.snapshot_bytes(), before)

    def test_start_rejects_an_empty_write_scope(self) -> None:
        self.write_ticket(canonical_ticket())
        request = self.write_request(
            {
                "baseline": {"reference": "snapshot", "staged": [], "unstaged": [], "untracked": []},
                "existing_changes": {"included": [], "excluded": []},
                "allowed_write_scope": [],
            }
        )

        result, payload = self.run_cli("start", str(self.task_dir), "T001", "--input", str(request))

        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid_field", {item["code"] for item in payload["problems"]})
        self.assertEqual(runtime_entry(self.task_dir, "T001")["phase"], "open")

    def test_block_and_unblock_preserve_the_execution_boundary(self) -> None:
        ticket = running_ticket(runtime={
            "phase": "in_progress",
            "attempt": 1,
            "review": "Review from an earlier execution.",
            "current_attempt": {
                "number": 1,
                "baseline": {"reference": "snapshot", "staged": [], "unstaged": [], "untracked": []},
                "existing_changes": {"included": [], "excluded": []},
                "allowed_write_scope": ["delivery.py"],
            },
        })
        bind_authority(self.task_dir, ticket, "Fixture executed against the current contract.")
        self.write_ticket(ticket)
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
        stored = runtime_entry(self.task_dir, "T001")
        self.assertEqual(stored["phase"], "open")
        self.assertNotIn("current_attempt", stored)
        self.assertEqual(stored["blocker"]["category"], "environment")
        self.assertEqual(stored["evidence"]["AC1"], {"attempt": 1, "summary": "Partial behavior verified."})

        invalid_request = self.write_request({"release_evidence": ""})
        before = self.snapshot_bytes()
        invalid_result, _ = self.run_cli(
            "unblock", str(self.task_dir), "T001", "--input", str(invalid_request)
        )
        self.assertEqual(invalid_result.returncode, 1)
        self.assertEqual(self.snapshot_bytes(), before)

        unblock_request = self.write_request(
            {"release_evidence": "The required runtime verification now exits 0."}
        )
        unblock_result, _ = self.run_cli(
            "unblock", str(self.task_dir), "T001", "--input", str(unblock_request)
        )
        self.assertEqual(unblock_result.returncode, 0)
        self.assertNotIn("blocker", runtime_entry(self.task_dir, "T001"))

        start_request = self.write_request(
            {
                "baseline": {"reference": "snapshot-2", "staged": [], "unstaged": [], "untracked": []},
                "existing_changes": {"included": [], "excluded": []},
                "allowed_write_scope": ["delivery.py"],
            }
        )
        start_result, _ = self.run_cli(
            "start", str(self.task_dir), "T001", "--input", str(start_request)
        )
        self.assertEqual(start_result.returncode, 0)
        self.assertNotIn("review", runtime_entry(self.task_dir, "T001"))

    def test_retry_increments_attempt_without_leaving_in_progress(self) -> None:
        ticket = running_ticket(runtime={
            "phase": "in_progress",
            "attempt": 1,
            "evidence": {"AC1": {"attempt": 1, "summary": "Old attempt evidence."}},
            "review": "Review for the previous attempt only.",
            "current_attempt": {
                "number": 1,
                "baseline": {"reference": "snapshot-1", "staged": [], "unstaged": [], "untracked": []},
                "existing_changes": {"included": [], "excluded": []},
                "allowed_write_scope": ["delivery.py"],
            },
        })
        bind_authority(self.task_dir, ticket, "Fixture executed against the current contract.")
        self.write_ticket(ticket)
        request = self.write_request(
            {
                "expected_attempt": 1,
                "baseline": {"reference": "snapshot-2", "staged": [], "unstaged": [], "untracked": []},
                "existing_changes": {"included": [], "excluded": []},
                "allowed_write_scope": ["delivery.py"],
                "findings": "AC1 failed verification; implement a correction.",
            }
        )

        result, payload = self.run_cli("retry", str(self.task_dir), "T001", "--input", str(request))

        self.assertEqual(result.returncode, 0)
        self.assertTrue(payload["ok"])
        stored = runtime_entry(self.task_dir, "T001")
        self.assertEqual(stored["phase"], "in_progress")
        self.assertEqual(stored["attempt"], 2)
        self.assertNotIn("evidence", stored)
        self.assertNotIn("review", stored)
        self.assertEqual(stored["current_attempt"]["number"], 2)
        self.assertEqual(stored["reopen_context"]["review_finding"], "AC1 failed verification; implement a correction.")
        self.assertEqual(stored["reopen_context"]["invalidated_acceptance"], ["AC1"])

    def test_retry_rejects_a_stale_attempt(self) -> None:
        ticket = running_ticket(runtime={
            "phase": "in_progress",
            "attempt": 2,
            "current_attempt": {
                "number": 2,
                "baseline": {"reference": "snapshot-2", "staged": [], "unstaged": [], "untracked": []},
                "existing_changes": {"included": [], "excluded": []},
                "allowed_write_scope": ["delivery.py"],
            },
        })
        bind_authority(self.task_dir, ticket, "Fixture executed against the current contract.")
        self.write_ticket(ticket)
        request = self.write_request(
            {
                "expected_attempt": 1,
                "baseline": {"reference": "snapshot-3", "staged": [], "unstaged": [], "untracked": []},
                "existing_changes": {"included": [], "excluded": []},
                "allowed_write_scope": ["delivery.py"],
                "findings": "The previous attempt still needs repair.",
            }
        )

        result, payload = self.run_cli("retry", str(self.task_dir), "T001", "--input", str(request))

        self.assertEqual(result.returncode, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("stale_attempt", {item["code"] for item in payload["problems"]})
        self.assertEqual(runtime_entry(self.task_dir, "T001")["attempt"], 2)

    def test_retry_rejects_an_empty_write_scope(self) -> None:
        ticket = running_ticket()
        bind_authority(self.task_dir, ticket, "Fixture executed against the current contract.")
        self.write_ticket(ticket)
        request = self.write_request(
            {
                "expected_attempt": 1,
                "baseline": {"reference": "snapshot-2", "staged": [], "unstaged": [], "untracked": []},
                "existing_changes": {"included": [], "excluded": []},
                "allowed_write_scope": [],
                "findings": "The implementation needs repair.",
            }
        )

        result, payload = self.run_cli("retry", str(self.task_dir), "T001", "--input", str(request))

        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid_field", {item["code"] for item in payload["problems"]})
        self.assertEqual(runtime_entry(self.task_dir, "T001")["attempt"], 1)

    def test_block_accepts_dependency_as_an_execution_blocker(self) -> None:
        ticket = running_ticket(runtime={
            "phase": "in_progress",
            "attempt": 1,
            "current_attempt": {
                "number": 1,
                "baseline": {"reference": "snapshot", "staged": [], "unstaged": [], "untracked": []},
                "existing_changes": {"included": [], "excluded": []},
                "allowed_write_scope": [],
            },
        })
        self.write_ticket(ticket)
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
        result, payload = self.run_cli(
            "block", str(self.task_dir), "T001", "--input", str(request)
        )

        self.assertEqual(result.returncode, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["result"]["ticket"]["runtime"]["blocker"]["category"], "dependency")

    def test_complete_and_reopen_enforce_evidence_and_review_gates(self) -> None:
        ticket = canonical_ticket(
            delivery_acceptance=[
                {"id": "AC1", "description": "First behavior."},
                {"id": "AC2", "description": "Second behavior."},
            ],
            runtime={
                "phase": "in_progress",
                "attempt": 1,
                "current_attempt": {
                    "number": 1,
                    "baseline": {"reference": "snapshot", "staged": [], "unstaged": [], "untracked": []},
                    "existing_changes": {"included": [], "excluded": []},
                    "allowed_write_scope": ["delivery.py"],
                },
            },
        )
        bind_authority(self.task_dir, ticket, "Fixture executed against the current contract.")
        self.write_ticket(ticket)
        verification = [{"command": "test", "exit_code": 0, "summary": "Passed."}]
        incomplete_request = self.write_request(
            {
                "evidence": {"AC1": {"result": "passed", "summary": "First verified."}},
                "verification": verification,
                "expected_attempt": 1, "review": "检查完成，无需修改。",
            }
        )
        before = self.snapshot_bytes()

        incomplete_result, incomplete_payload = self.run_cli(
            "complete", str(self.task_dir), "T001", "--input", str(incomplete_request)
        )

        self.assertEqual(incomplete_result.returncode, 1)
        self.assertIn(
            "done_without_acceptance_evidence",
            {item["code"] for item in incomplete_payload["problems"]},
        )
        self.assertEqual(self.snapshot_bytes(), before)

        complete_request = self.write_request(
            {
                "evidence": {
                    "AC1": {"result": "passed", "summary": "First verified."},
                    "AC2": {"result": "passed", "summary": "Second verified."},
                },
                "verification": verification,
                "expected_attempt": 1, "review": "检查完成，无需修改。",
            }
        )
        complete_result, _ = self.run_cli(
            "complete", str(self.task_dir), "T001", "--input", str(complete_request)
        )
        self.assertEqual(complete_result.returncode, 0)
        completed = runtime_entry(self.task_dir, "T001")
        self.assertEqual(completed["phase"], "done")
        self.assertNotIn("current_attempt", completed)
        self.assertEqual(completed["evidence"]["AC2"], {"attempt": 1, "summary": "Second verified."})

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
        reopened = runtime_entry(self.task_dir, "T001")
        self.assertEqual(reopened["phase"], "open")
        self.assertEqual(set(reopened["evidence"]), {"AC1"})
        self.assertEqual(reopened["reopen_context"]["invalidated_acceptance"], ["AC2"])

    def test_complete_rejects_nonzero_verification(self) -> None:
        ticket = running_ticket()
        bind_authority(self.task_dir, ticket, "Fixture executed against the current contract.")
        self.write_ticket(ticket)
        request = self.write_request(
            {
                "evidence": {"AC1": {"result": "passed", "summary": "Verified."}},
                "verification": [{"command": "test", "exit_code": 1, "summary": "Failed."}],
                "expected_attempt": 1,
            }
        )
        before = self.snapshot_bytes()

        result, payload = self.run_cli(
            "complete", str(self.task_dir), "T001", "--input", str(request)
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("completion_gate_failed", {item["code"] for item in payload["problems"]})
        self.assertEqual(self.snapshot_bytes(), before)

    def test_create_batch_allocates_ids_and_resolves_temporary_dependencies(self) -> None:
        request = self.write_request(
            {
                "tickets": [
                    {
                        "key": "foundation",
                        "title": "Foundation",
                        "covers": {"requirements": ["R1"], "spec_acceptance": ["AC1"]},
                        "referenced_design_decisions": ["D1"],
                        "what_to_build": "Deliver the foundation.",
                        "constraints": [],
                        "delivery_acceptance": [
                            {"id": "AC1", "description": "Foundation is observable."}
                        ],
                        "dependencies": [],
                    },
                    {
                        "key": "consumer",
                        "title": "Consumer behavior",
                        "covers": {"requirements": ["R1"], "spec_acceptance": ["AC1"]},
                        "referenced_design_decisions": ["D1"],
                        "what_to_build": "Consume the foundation.",
                        "constraints": ["Use the confirmed foundation."],
                        "delivery_acceptance": [
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
        files = sorted((self.task_dir / "tickets").glob("*.md"))
        self.assertEqual([path.name.split("-", 1)[0] for path in files], ["T001", "T002"])
        stored = [read_ticket(path) for path in files]
        self.assertEqual(stored[0]["constraints"], [])
        self.assertEqual(stored[1]["dependencies"], ["T001"])
        for contract in stored:
            self.assertNotIn("lifecycle", contract)
            self.assertNotIn("execution", contract)
        state = read_state(self.task_dir)
        self.assertEqual(state["schema_version"], 1)
        for ticket_id in ("T001", "T002"):
            self.assertEqual(state["tickets"][ticket_id]["phase"], "open")
            self.assertEqual(state["tickets"][ticket_id]["attempt"], 0)
        self.assertEqual(payload["graph"]["frontier"], ["T001"])

    def test_create_batch_rejects_malformed_candidates_without_creating_files(self) -> None:
        request = self.write_request(
            {
                "tickets": [
                    {
                        "key": "invalid",
                        "title": {"not": "a string"},
                        "covers": {"requirements": ["R1"], "spec_acceptance": ["AC1"]},
                        "referenced_design_decisions": ["D1"],
                        "what_to_build": "Invalid candidate.",
                        "constraints": ["Preserve the contract."],
                        "delivery_acceptance": [
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
        self.assertEqual(list((self.task_dir / "tickets").glob("*.md")), [])

    def test_reconcile_batch_commits_replacement_lineage_and_dependency_reconnect(self) -> None:
        self.write_ticket(canonical_ticket(), "T001-old.md")
        self.write_ticket(canonical_ticket(id="T002", dependencies=["T001"]), "T002-consumer.md")
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
                            "referenced_design_decisions": ["D1"],
                            "what_to_build": "Replace the original delivery.",
                            "constraints": [],
                            "delivery_acceptance": [
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
                read_ticket(path)
                for path in (self.task_dir / "tickets").glob("*.md")
            )
        }
        state = read_state(self.task_dir)["tickets"]
        self.assertEqual(state["T001"]["phase"], "superseded")
        self.assertEqual(by_id["T001"]["supersession"]["replacement_ticket_id"], "T003")
        self.assertNotIn("lifecycle", by_id["T001"])
        self.assertEqual(by_id["T002"]["dependencies"], ["T003"])
        self.assertEqual(state["T003"]["phase"], "open")
        self.assertEqual(state["T003"]["attempt"], 0)

    def test_reconcile_batch_rejects_an_invalid_prospective_graph_without_writes(self) -> None:
        self.write_ticket(canonical_ticket(), "T001-old.md")
        self.write_ticket(
            canonical_ticket(id="T002", dependencies=["T001"]), "T002-consumer.md"
        )
        before = self.snapshot_bytes()
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
        self.assertEqual(self.snapshot_bytes(), before)

    def test_recover_rollback_restores_the_pre_transaction_graph(self) -> None:
        original = canonical_ticket()
        target = canonical_ticket(
            runtime={
                "phase": "done",
                "attempt": 1,
                "evidence": {"AC1": {"attempt": 1, "summary": "Verified."}},
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
        self.assertEqual(read_ticket(ticket_path), contract_of(original))
        self.assertEqual(runtime_entry(self.task_dir, "T001"), original["runtime"])
        self.assertFalse((self.task_dir / ".ticket-graph-transaction").exists())

    def test_recover_commit_accepts_only_a_valid_staged_graph(self) -> None:
        original = canonical_ticket()
        target = canonical_ticket(
            runtime={
                "phase": "done",
                "attempt": 1,
                "evidence": {"AC1": {"attempt": 1, "summary": "Verified."}},
            },
        )
        ticket_path, _ = self.prepare_switching_transaction(original, target)

        result, payload = self.run_cli("recover", str(self.task_dir), "commit")

        self.assertEqual(result.returncode, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(read_ticket(ticket_path), contract_of(target))
        self.assertEqual(runtime_entry(self.task_dir, "T001"), target["runtime"])

        invalid = canonical_ticket(schema_version=3)
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

    def test_workflow_contract_docs_are_markdown_only_and_command_aligned(self) -> None:
        paths = [
            REPOSITORY / "README.md",
            REPOSITORY / "engineering" / "graph-workflow" / "SKILL.md",
            REPOSITORY / "engineering" / "to-tickets" / "SKILL.md",
            REPOSITORY / "engineering" / "shared" / "ticket-schema.json",
            REPOSITORY / "engineering" / "shared" / "runtime-state-schema.json",
        ]
        text = "\n".join(path.read_text(encoding="utf-8") for path in paths)

        self.assertNotIn("tickets/*.json", text)
        self.assertNotIn("inspect_graph.py", text)
        self.assertIn("tickets/*.md", text)
        self.assertIn("create-batch", text)
        self.assertIn("reconcile-batch", text)
        self.assertIn("open", text)
        self.assertIn("superseded", text)
        self.assertIn(".loop/state.json", text)
        for dispatch_mode in ("serial", "swarm"):
            self.assertIn(dispatch_mode, text)


if __name__ == "__main__":
    unittest.main()
