import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import test_bootstrap
from test_ticket_graph import canonical_ticket
from ticket_graph.authority import bind_authority, authority_current
from ticket_graph.recovery import recover_transaction
from ticket_graph import store
from migration import migrate


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.task = Path(self.temp.name)
        (self.task / 'tickets').mkdir()
        (self.task / 'SPEC.md').write_text('# SPEC\n1. **R1** — Send a message.\n- **AC1** — Visible result.\n')
        (self.task / 'HLD.md').write_text('# HLD\n- **D1** — Reuse persistence.\n')
        self.path = self.task / 'tickets/T001-message.json'

    def legacy(self, phase='done'):
        ticket = canonical_ticket()
        ticket['lifecycle']['phase'] = phase
        if phase == 'done':
            ticket['execution']['attempt_sequence'] = 1
            ticket['execution']['evidence'] = {'AC1': {'result': 'passed', 'summary': 'Observed result.'}}
        bind_authority(self.task, ticket, 'Confirmed existing contract.')
        ticket['design_decisions'] = ticket.pop('referenced_design_decisions')
        ticket['acceptance_criteria'] = ticket.pop('delivery_acceptance')
        ticket['schema_version'] = 1
        self.path.write_text(json.dumps(ticket))
        return ticket

    def test_migration_preserves_evidence_and_binding_and_is_idempotent(self):
        old = self.legacy()
        payload, code = migrate(self.task)
        self.assertEqual(code, 0, payload)
        current = json.loads(self.path.read_text())
        self.assertEqual(current['execution'], old['execution'])
        self.assertEqual(current['lifecycle'], old['lifecycle'])
        self.assertTrue(authority_current(self.task, current))
        self.assertEqual(current['schema_version'], 2)
        before = self.path.read_bytes()
        self.assertEqual(migrate(self.task)[1], 0)
        self.assertEqual(self.path.read_bytes(), before)

    def test_migration_keeps_stale_authority_stale(self):
        self.legacy()
        with (self.task / 'SPEC.md').open('a') as stream: stream.write('\nChanged requirement meaning.\n')
        self.assertEqual(migrate(self.task)[1], 0)
        self.assertFalse(authority_current(self.task, json.loads(self.path.read_text())))

    def test_invalid_or_ambiguous_graph_does_not_write(self):
        old = self.legacy()
        for changed in [dict(old, schema_version=99), dict(old, referenced_design_decisions=['D1']), dict(old, lifecycle={'phase':'in_progress'}), dict(old, schema_version=True), dict(old, lifecycle=None)]:
            self.path.write_text(json.dumps(changed))
            before = self.path.read_bytes()
            self.assertNotEqual(migrate(self.task)[1], 0)
            self.assertEqual(self.path.read_bytes(), before)
            self.assertFalse((self.task / '.ticket-graph-transaction').exists())

    def test_failed_switch_can_rollback_exact_legacy_bytes(self):
        self.legacy()
        before = self.path.read_bytes()
        with patch.object(store.os, 'replace', side_effect=OSError('injected switch failure')):
            self.assertNotEqual(migrate(self.task)[1], 0)
        self.assertTrue((self.task / '.ticket-graph-transaction').exists())
        payload, code = recover_transaction(self.task, 'rollback')
        self.assertEqual(code, 0, payload)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertFalse((self.task / '.ticket-graph-transaction').exists())

    def test_failed_switch_can_commit_migrated_graph(self):
        self.legacy()
        with patch.object(store.os, 'replace', side_effect=OSError('injected switch failure')):
            self.assertNotEqual(migrate(self.task)[1], 0)
        payload, code = recover_transaction(self.task, 'commit')
        self.assertEqual(code, 0, payload)
        self.assertEqual(json.loads(self.path.read_text())['schema_version'], 2)

    def test_documented_create_request_runs_with_new_spec_shape(self):
        root = Path(__file__).resolve().parents[2]
        doc = (root / 'to-tickets/references/script-inputs.md').read_text()
        request = doc.split('```json\n', 1)[1].split('```', 1)[0]
        result = subprocess.run([sys.executable, str(root / 'to-tickets/scripts/create-graph'), 'create-batch', str(self.task), '--input', '-'], input=request, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        result = subprocess.run([sys.executable, str(root / 'to-tickets/scripts/validate-graph'), str(self.task)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_documented_delivery_inputs_complete_a_ticket(self):
        self.test_documented_create_request_runs_with_new_spec_shape()
        root = Path(__file__).resolve().parents[2]
        doc = (root.parent / 'docs/loop-runtime.md').read_text()
        samples = [part.split('```', 1)[0] for part in doc.split('```json\n')[1:]]
        start, complete = map(json.loads, samples[:2])
        for script, operation, request in [('record-attempt', 'start', start), ('update-status', 'complete', complete)]:
            result = subprocess.run([sys.executable, str(root / 'loop/scripts' / script), operation, str(self.task), 'T001', '--input', '-'], input=json.dumps(request), capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        ticket = json.loads(next((self.task / 'tickets').glob('*.json')).read_text())
        self.assertEqual(ticket['lifecycle']['phase'], 'done')
