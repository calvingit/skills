import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import test_bootstrap
from test_bootstrap import dump_ticket, read_ticket


class WorkflowCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.task = Path(self.temp.name)
        (self.task / 'tickets').mkdir()
        (self.task / 'SPEC.md').write_text('# SPEC\n1. **R1** — Send a message.\n- **AC1** — Visible result.\n')
        (self.task / 'SOLUTION.md').write_text('# Solution\n- **D1** — Reuse persistence.\n')

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
        doc = (root / 'graph-workflow/references/script-inputs.md').read_text()
        samples = [part.split('```', 1)[0] for part in doc.split('```json\n')[1:]]
        start, complete = map(json.loads, samples[:2])
        for script, operation, request in [('update-status', 'start', start), ('update-status', 'complete', complete)]:
            result = subprocess.run([sys.executable, str(root / 'graph-workflow/scripts' / script), operation, str(self.task), 'T001', '--input', '-'], input=json.dumps(request), capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        ticket = read_ticket(next((self.task / 'tickets').glob('*.md')))
        self.assertEqual(ticket['lifecycle']['phase'], 'done')
