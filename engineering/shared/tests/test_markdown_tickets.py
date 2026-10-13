"""Markdown ticket storage, explicit JSON migration and recovery (handoff cases A-H)."""
from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import test_bootstrap
from test_bootstrap import dump_ticket, read_ticket
from ticket_graph import frontmatter, store
from ticket_graph.authority import authority_current, bind_authority
from ticket_graph.ticket_markdown import TicketFormatError, parse_ticket, render_ticket
from ticket_graph.queries import inspect
from lifecycle import mutate_ticket
from planning import migrate_graph, reconcile_batch
from ticket_graph.authority import authority_fingerprint
import delivery
from test_ticket_graph import canonical_ticket

E = Path(__file__).resolve().parents[2]
SPEC = ("# Spec\n\n1. **R1** — Behavior.\n2. **R2** — Second.\n3. **R3** — Third.\n\n"
        "- **AC1** — Covers: R1. One.\n- **AC2** — Covers: R2. Two.\n- **AC3** — Covers: R3. Three.\n")
HLD = "# HLD\n\n- **D1** — Shared decision.\n"
BASELINE = {"reference": "HEAD", "staged": [], "unstaged": [], "untracked": []}
START = {"baseline": BASELINE, "existing_changes": {"included": [], "excluded": []}, "allowed_write_scope": ["src/**"]}
PASS = {"verification": [{"command": "make test", "exit_code": 0, "summary": "ok"}]}


def run(script, *args, cwd=None, stdin=None):
    env = dict(os.environ); env.pop("PYTHONPATH", None)
    result = subprocess.run([sys.executable, str(E / script), *args], input=stdin, capture_output=True, text=True, cwd=cwd, env=env)
    return result.returncode, json.loads(result.stdout)


class FrontmatterParserTests(unittest.TestCase):
    def test_round_trips_unicode_colons_quotes_and_nesting(self):
        value = {"a": "中文：值", "b": "x: y # not a comment", "c": 'say "hi"', "d": "it's", "e": ["R1", "- dash", ""],
                 "f": {"g": None, "h": [], "i": {}, "j": 0, "k": True, "l": [{"m": "n", "o": [1]}]}, "p": "yes", "q": "123", "r": "2026-10-13"}
        text = frontmatter.dumps(value)
        self.assertEqual(frontmatter.loads(text), value)
        self.assertIn('p: "yes"', text)
        self.assertIn('q: "123"', text)

    def test_accepts_hand_written_quoted_forms(self):
        self.assertEqual(frontmatter.loads("a: 'it''s: ok'\nb: \"\\u4e2d\"\nc: plain_value\n"), {"a": "it's: ok", "b": "中", "c": "plain_value"})

    def test_rejects_unsupported_or_ambiguous_yaml(self):
        for text in ["a: 1\na: 2\n", "a: &x 1\n", "a: *x\n", "a: |\n  x\n", "a: >\n  x\n", "a: [1, 2]\n", "a: {b: 1}\n",
                     "# c\na: 1\n", "a: 1 # c\n", "a:\n\t- x\n", "a: yes\n", "a: 1.5\n", "a: 2026-10-13\n", "a: !!str x\n",
                     "a:\n", "a:1\n", "  a: 1\n", "a:\n   b: 1\n", "- x\n", "a: b: c\n", "\"a\": 1\n", "a: \"x\n", "a:\n  - \n", "---\na: 1\n"]:
            with self.subTest(text=text):
                with self.assertRaises(frontmatter.FrontmatterError):
                    frontmatter.loads(text)


class MarkdownTicketTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.task = Path(self.temp.name)
        (self.task / "tickets").mkdir()
        (self.task / "SPEC.md").write_text(SPEC)
        (self.task / "HLD.md").write_text(HLD)

    def contract(self, n, deps=()):
        return {"key": f"k{n}", "title": f"第{n}步: \"slice\"", "covers": {"requirements": [f"R{n}"], "spec_acceptance": [f"AC{n}"]},
                "referenced_design_decisions": ["D1"], "what_to_build": f"Build slice {n}.\n\nKeep: colons and **markdown**.",
                "constraints": ["No new deps.", "Multi\nline constraint"], "delivery_acceptance": [{"id": "AC1", "description": f"Slice {n} observable."}],
                "dependencies": list(deps)}

    def create(self):
        request = {"tickets": [self.contract(1), self.contract(2, ["k1"]), self.contract(3, ["k2"])]}
        code, payload = run("to-tickets/scripts/create-graph", "create-batch", str(self.task), "--input", "-", stdin=json.dumps(request))
        self.assertEqual(code, 0, payload)
        return payload

    def path(self, ticket_id):
        return next((self.task / "tickets").glob(ticket_id + "-*.md"))

    def update(self, operation, ticket_id, request, script=None):
        script = script or "loop/scripts/update-status"
        code, payload = run(script, operation, str(self.task), ticket_id, "--input", "-", stdin=json.dumps(request))
        self.assertEqual(code, 0, payload)
        return payload

    # Case A
    def test_create_writes_markdown_with_disjoint_frontmatter_and_body(self):
        self.create()
        self.assertEqual(list((self.task / "tickets").glob("*.json")), [])
        text = self.path("T001").read_text()
        head, body = text.split("\n---\n", 1)
        for field in ("title", "what_to_build", "constraints", "delivery_acceptance"):
            self.assertNotIn(field + ":", head)
        self.assertIn("schema_version: 3", head)
        self.assertIn("# 第1步: \"slice\"", body)
        for section in ("## Delivery", "## Constraints", "## Delivery Acceptance", "- **AC1** — Slice 1 observable."):
            self.assertIn(section, body)
        self.assertEqual(read_ticket(self.path("T001"))["constraints"], ["No new deps.", "Multi\nline constraint"])

    # Case B
    def test_lifecycle_updates_never_rewrite_a_hand_edited_body(self):
        self.create()
        path = self.path("T001")
        head, body = path.read_text().split("\n---\n", 1)
        edited = body.replace("## Constraints", "\n\n## Constraints")  # Equivalent contract, different bytes.
        path.write_text(head + "\n---\n" + edited)
        self.update("start", "T001", START)
        self.update("block", "T001", {"blocker": {"category": "environment", "reason": "db down", "release_condition": "db up"}, "evidence": {}})
        self.update("unblock", "T001", {"release_evidence": "db is up"})
        self.update("start", "T001", START, script="loop/scripts/record-attempt")
        retried = self.update("retry", "T001", {"baseline": BASELINE, "existing_changes": START["existing_changes"], "expected_attempt": 2, "findings": "fix"})
        self.assertEqual(retried["result"]["ticket"]["execution"]["current_attempt"]["allowed_write_scope"], ["src/**"])  # Inherited.
        self.assertEqual(retried["graph"]["in_progress"], ["T001"])  # Callers use this graph; no re-query needed.
        self.update("complete", "T001", {"expected_attempt": 3, "evidence": {"AC1": {"result": "passed", "summary": "seen"}}, **PASS})
        self.update("reopen", "T001", {"review_finding": "regress", "invalidated_acceptance": ["AC1"], "upstream_unchanged": True})
        self.assertEqual(path.read_text().split("\n---\n", 1)[1], edited)
        stored = read_ticket(path)
        self.assertEqual((stored["lifecycle"]["phase"], stored["execution"]["attempt_sequence"]), ("open", 3))

    # Case C
    def test_migration_preserves_states_evidence_attempts_and_authority(self):
        self.create()
        self.update("start", "T001", START)
        self.update("complete", "T001", {"expected_attempt": 1, "evidence": {"AC1": {"result": "passed", "summary": "seen"}}, "review": "ok", **PASS})
        self.update("start", "T002", START)
        self.update("block", "T002", {"blocker": {"category": "dependency", "reason": "api", "release_condition": "api"}, "evidence": {}})
        before = {p.name: read_ticket(p) for p in sorted((self.task / "tickets").glob("*.md"))}
        stale_before = inspect(self.task)[0]["graph"]["stale_authority"]
        for name, ticket in before.items():  # Downgrade to the v2 JSON layout.
            (self.task / "tickets" / name).unlink()
            (self.task / "tickets" / name.replace(".md", ".json")).write_text(json.dumps({**ticket, "schema_version": 2}, ensure_ascii=False, indent=2))
        code, payload = run("loop/scripts/frontier", str(self.task))
        self.assertEqual(code, 1); self.assertIn("legacy_json_ticket", {p["code"] for p in payload["problems"]})
        json_bytes = {p.name: p.read_bytes() for p in (self.task / "tickets").iterdir()}
        code, dry = run("to-tickets/scripts/create-graph", "migrate", str(self.task), "--dry-run")
        self.assertEqual(code, 0, dry); self.assertFalse(dry["result"]["applied"])
        self.assertEqual({p.name: p.read_bytes() for p in (self.task / "tickets").iterdir()}, json_bytes)
        code, applied = run("to-tickets/scripts/create-graph", "migrate", str(self.task), "--apply")
        self.assertEqual(code, 0, applied)
        self.assertEqual(list((self.task / "tickets").glob("*.json")), [])
        self.assertEqual({p.name: read_ticket(p) for p in sorted((self.task / "tickets").glob("*.md"))}, before)
        graph = inspect(self.task)[0]["graph"]
        self.assertEqual(graph["stale_authority"], stale_before)
        self.assertTrue(graph["valid"])
        self.assertFalse((self.task / ".ticket-graph-transaction").exists())

    def test_mixed_formats_for_one_id_are_reported_not_resolved(self):
        self.create()
        md = self.path("T001")
        (self.task / "tickets" / "T001-old.json").write_text(json.dumps({**read_ticket(md), "schema_version": 2}))
        for code, payload in [run("loop/scripts/graph-query", "inspect", str(self.task)),
                              run("to-tickets/scripts/create-graph", "migrate", str(self.task), "--apply")]:
            self.assertEqual(code, 1)
            self.assertIn("mixed_ticket_formats", {p["code"] for p in payload["problems"]})
        self.assertTrue(md.exists()); self.assertTrue((self.task / "tickets" / "T001-old.json").exists())

    def test_migration_rejects_an_invalid_legacy_graph_without_writing(self):
        (self.task / "tickets" / "T001-a.json").write_text(json.dumps(canonical_ticket(schema_version=2, dependencies=["T009"])))
        code, payload = run("to-tickets/scripts/create-graph", "migrate", str(self.task), "--apply")
        self.assertEqual(code, 1, payload)
        self.assertEqual([p.name for p in (self.task / "tickets").iterdir()], ["T001-a.json"])

    # Case D
    def interrupted(self):
        self.create()
        for p in sorted((self.task / "tickets").glob("*.md")):
            p.with_suffix(".json").write_text(json.dumps({**read_ticket(p), "schema_version": 2}))
            p.unlink()
        real = os.replace; calls = []
        def crash(src, dst):
            calls.append(dst)
            if len(calls) == 2:
                raise OSError("simulated crash")
            return real(src, dst)
        with mock.patch.object(store.os, "replace", crash):
            payload, code = migrate_graph(self.task, apply=True)
        self.assertEqual(code, 1, payload)
        self.assertTrue((self.task / ".ticket-graph-transaction").exists())
        code, payload = run("loop/scripts/frontier", str(self.task))
        self.assertIn("recovery_required", {p["code"] for p in payload["problems"]})

    def test_interrupted_migration_rolls_back_to_json(self):
        self.interrupted()
        code, payload = run("loop/scripts/update-status", "recover", str(self.task), "rollback")
        self.assertEqual(code, 0, payload)  # Back to the untouched legacy JSON graph.
        self.assertEqual(payload["result"]["restored"], "legacy_json")
        self.assertEqual(sorted(p.suffix for p in (self.task / "tickets").iterdir()), [".json"] * 3)
        self.assertEqual(migrate_graph(self.task, apply=True)[1], 0)

    def test_interrupted_migration_rolls_forward(self):
        self.interrupted()
        code, payload = run("loop/scripts/update-status", "recover", str(self.task), "commit")
        self.assertEqual(code, 0, payload)
        self.assertEqual(sorted(p.suffix for p in (self.task / "tickets").iterdir()), [".md"] * 3)

    # Case E
    def test_invalid_frontmatter_and_body_are_structured_problems(self):
        self.create()
        path = self.path("T001"); good = path.read_text()
        cases = {
            "invalid_frontmatter": good.replace("schema_version: 3\n", "schema_version: 3\nschema_version: 3\n"),
            "duplicated_authority": good.replace("schema_version: 3\n", "schema_version: 3\ntitle: \"x\"\n"),
            "invalid_ticket_body": good.replace("## Constraints", "## Notes"),
            "missing_frontmatter": good.split("\n---\n", 1)[1],
            "invalid_frontmatter ": good.replace("schema_version: 3\n", "schema_version: 3\n_path: x\n"),
            "unknown_field": good.replace("schema_version: 3\n", "schema_version: 3\nreadiness: ready\n"),
        }
        for expected, text in cases.items():
            with self.subTest(expected=expected):
                path.write_text(text)
                code, payload = run("loop/scripts/graph-query", "inspect", str(self.task))
                self.assertEqual(code, 1)
                self.assertIn(expected.strip(), {p["code"] for p in payload["problems"]})
        path.write_text(good)
        before = path.read_bytes()
        path.write_text(good.replace("schema_version: 3\n", "schema_version: 3\nschema_version: 3\n"))
        code, _ = run("loop/scripts/record-attempt", "start", str(self.task), "T001", "--input", "-", stdin=json.dumps(START))
        self.assertEqual(code, 1)
        path.write_bytes(before)

    def test_body_edit_changes_contract_and_requires_reconciliation(self):
        self.create()
        self.update("start", "T001", START)
        path = self.path("T001")
        path.write_text(path.read_text().replace("Slice 1 observable.", "Slice 1 changed."))
        code, payload = run("loop/scripts/frontier", str(self.task))
        self.assertIn("T001", payload["graph"]["stale_authority"])

    # Case F: amendments on Markdown graphs
    def test_reconcile_update_rewrites_body_and_supersede_keeps_it(self):
        self.create()
        t3_body = self.path("T003").read_text().split("\n---\n", 1)[1]
        payload, code = reconcile_batch(self.task, {"reason": "amend", "operations": [
            {"operation": "update_contract", "ticket_id": "T002", "changes": {"title": "Renamed slice"}},
            {"operation": "create", "key": "t3b", "ticket": {k: v for k, v in self.contract(3).items() if k != "key"}},
            {"operation": "supersede", "ticket_id": "T003", "reason": "Replaced", "replacement": "t3b"},
        ]})
        self.assertEqual(code, 0, payload)
        self.assertIn("# Renamed slice", self.path("T002").read_text())
        self.assertEqual(self.path("T003").read_text().split("\n---\n", 1)[1], t3_body)
        self.assertEqual(read_ticket(self.path("T003"))["lifecycle"]["phase"], "superseded")

    # Case H
    def test_migrate_and_compat_wrappers_run_from_outside_the_repo(self):
        self.create()
        with tempfile.TemporaryDirectory() as elsewhere:
            code, payload = run("to-tickets/scripts/create-graph", "migrate", str(self.task), cwd=elsewhere)
            self.assertEqual(code, 1); self.assertIn("markdown_ticket_present", {p["code"] for p in payload["problems"]})
            code, payload = run("loop/scripts/record-attempt", "start", str(self.task), "T001", "--input", "-", cwd=elsewhere, stdin=json.dumps(START))
            self.assertEqual(code, 0, payload)
            self.assertEqual(payload["graph"]["in_progress"], ["T001"])

    def test_compat_alias_and_unified_entry_write_identical_state(self):
        self.create()
        self.update("start", "T001", START, script="loop/scripts/record-attempt")
        via_alias = self.path("T001").read_text()
        self.update("block", "T001", {"blocker": {"category": "environment", "reason": "r", "release_condition": "c"}, "evidence": {}})
        self.update("unblock", "T001", {"release_evidence": "ok"})
        self.update("start", "T001", START)
        self.assertEqual(read_ticket(self.path("T001"))["execution"]["current_attempt"]["allowed_write_scope"],
                         parse_ticket(via_alias)[0]["execution"]["current_attempt"]["allowed_write_scope"])
        code, payload = run("loop/scripts/update-status", "retry", str(self.task), "T001", "--input", "-",
                            stdin=json.dumps({"baseline": BASELINE, "existing_changes": START["existing_changes"], "expected_attempt": 2, "findings": "x", "allowed_write_scope": ["../escape"]}))
        self.assertEqual(code, 1, payload)  # An explicit scope is still validated.

    def test_render_refuses_lossy_tickets(self):
        bad = canonical_ticket(schema_version=3, what_to_build="text\n## Injected")
        with self.assertRaises(TicketFormatError):
            render_ticket(bad)


if __name__ == "__main__":
    unittest.main()
