import json
import re
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
import test_bootstrap


class WorkflowCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.task = Path(self.temp.name)
        (self.task / 'tickets').mkdir()
        (self.task / 'SPEC.md').write_text('# SPEC\n1. **R1** — Send a message.\n- **AC1** — Visible result.\n')
        (self.task / 'HLD.md').write_text('# HLD\n- **D1** — Reuse persistence.\n')

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
        doc = (root / 'loop/references/script-inputs.md').read_text()
        samples = [part.split('```', 1)[0] for part in doc.split('```json\n')[1:]]
        start, complete = map(json.loads, samples[:2])
        for script, operation, request in [('record-attempt', 'start', start), ('update-status', 'complete', complete)]:
            result = subprocess.run([sys.executable, str(root / 'loop/scripts' / script), operation, str(self.task), 'T001', '--input', '-'], input=json.dumps(request), capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        ticket = json.loads(next((self.task / 'tickets').glob('*.json')).read_text())
        self.assertEqual(ticket['lifecycle']['phase'], 'done')

    def test_diagram_exports_match_source_nodes_edges_and_guided_views(self):
        diagrams = Path(__file__).resolve().parents[3] / 'docs/diagrams'
        for stem, kind in [('engineering-workflow', 'workflow'), ('ticket-lifecycle', 'lifecycle')]:
            source = json.loads((diagrams / f'{stem}.{kind}.json').read_text())
            nodes = {node['id']: node for node in source.get('nodes', source.get('states', []))}
            edges = {edge['id']: edge for edge in source.get('edges', source.get('transitions', []))}
            for extension in ['svg', 'html']:
                with self.subTest(diagram=stem, export=extension):
                    text = (diagrams / f'{stem}.{extension}').read_text()
                    svg = ET.fromstring(re.search(r'<svg\b.*?</svg>', text, re.S)[0])
                    rendered_nodes = {element.get('data-node-id'): element for element in svg.iter()
                                      if element.get('data-node-id') is not None}
                    self.assertEqual(set(rendered_nodes), set(nodes))
                    for node_id, node in nodes.items():
                        element = rendered_nodes[node_id]
                        self.assertEqual(element.get('data-node-label'), node['label'])
                        self.assertEqual(element.get('data-node-sublabel'), node['sublabel'])
                        labels = [part for part in element.iter()
                                  if part.tag.rsplit('}', 1)[-1] == 'text']
                        title = next(part for part in labels if part.get('data-node-label') == '')
                        subtitle = next(part for part in labels if part.get('data-detail') == 'context')
                        self.assertEqual(''.join(title.itertext()).strip(), node['label'])
                        self.assertEqual(''.join(subtitle.itertext()).strip(), node['sublabel'])
                    rendered_edges = {element.get('data-edge-id'): element for element in svg.iter()
                                      if element.tag.rsplit('}', 1)[-1] == 'path'
                                      and element.get('data-edge-id') is not None}
                    self.assertEqual(set(rendered_edges), set(edges))
                    for edge_id, edge in edges.items():
                        element = rendered_edges[edge_id]
                        self.assertEqual(element.get('data-edge-from'), edge['from'])
                        self.assertEqual(element.get('data-edge-to'), edge['to'])
                        self.assertEqual(element.get('data-edge-label', ''), edge.get('label', ''))
                        if edge.get('label'):
                            label = next(part for part in svg.iter()
                                         if part.get('data-edge-id') == edge_id
                                         and part.tag.rsplit('}', 1)[-1] == 'g')
                            visible = next(part for part in label.iter()
                                           if part.tag.rsplit('}', 1)[-1] == 'text')
                            self.assertEqual(''.join(visible.itertext()).strip(), edge['label'])
                    if extension == 'html':
                        views = re.search(r'<script id="archify-guided-views-data"[^>]*>(.*?)</script>',
                                          text, re.S)[1]
                        self.assertEqual(json.loads(views), source['meta']['views'])
