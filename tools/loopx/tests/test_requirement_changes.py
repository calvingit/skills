from __future__ import annotations
import copy
import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from loopx.loop_runtime import run_ticket, reopen_ticket, _graph, dispatch_ready
from loopx.graph.execution_graph.batch import reconcile_batch
from loopx.graph.execution_graph.authority import authority_fingerprint
from loopx import delivery
from test_loop_runtime import ticket, receipt


class RequirementChangesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name)
        subprocess.run(['git', 'init', '-q', str(self.workspace)], check=True)
        self.task = self.workspace / 'task'
        (self.task / 'tickets').mkdir(parents=True)
        (self.task / 'SPEC.md').write_text('# Spec\n1. **R1** — Run.\n- **AC1** — Covers: R1. Run.\n')
        (self.task / 'HLD.md').write_text('# HLD\n- **D1** — Use graph.\n')
        self.path = self.task / 'tickets/T001-test.json'
        self.path.write_text(json.dumps(ticket()))
        self.code = self.workspace / 'src.py'
        self.code.write_text('print(1)\n')
        subprocess.run(['git', '-C', str(self.workspace), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(self.workspace), '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'baseline'], check=True)

    def execute(self, **values):
        return run_ticket(self.task, lambda bundle: receipt(current_attempt=bundle['attempt'], **values), workspace_root=self.workspace, allowed_write_scope=['src.py'])

    def change(self):
        p = self.task / 'SPEC.md'
        p.write_text(p.read_text().replace('Run.', 'Reject invalid input.'))

    def retain(self, **overrides):
        operation = {'operation': 'retain_contract', 'ticket_id': 'T001',
                     'reason': 'Reviewed the delta: this ticket contract and its evidence remain applicable.',
                     'expected_authority': authority_fingerprint(self.task)}
        operation.update(overrides)
        return reconcile_batch(self.task, {'reason': 'Confirmed impact review.', 'operations': [operation]})

    def test_resume_rejects_changed_requirement_without_calling_worker(self):
        self.assertEqual(self.execute(outcome='interrupted').outcome, 'interrupted')
        self.change()
        result = run_ticket(self.task, lambda _: self.fail('stale worker dispatched'), workspace_root=self.workspace, allowed_write_scope=['src.py'])
        self.assertEqual(result.outcome, 'blocked')
        self.assertEqual(result.problems[0]['code'], 'upstream_changed')
        self.assertEqual(json.loads(self.path.read_text())['execution']['attempt_sequence'], 1)

    def test_trailing_blank_line_does_not_prevent_reopen(self):
        self.assertEqual(self.execute().outcome, 'completed')
        p = self.task / 'SPEC.md'; p.write_text(p.read_text() + '\n')
        result = reopen_ticket(self.task, 'T001', review_finding='Original contract not met', invalidated_acceptance=['AC1'])
        self.assertEqual(result.outcome, 'reopened')

    def test_done_is_historical_until_authority_is_reconciled(self):
        self.execute(); self.change()
        graph = _graph('inspect', self.task)['graph']
        self.assertEqual(graph['done'], ['T001'])
        self.assertEqual(graph['stale_authority'], ['T001'])
        self.assertTrue(graph['all_active_done'])
        self.assertFalse(graph['delivery_ready'])
        with self.assertRaises(ValueError): delivery.prepare(self.task, self.workspace)

    def test_retention_preserves_evidence_and_allows_original_defect_reopen(self):
        self.execute(); evidence = json.loads(self.path.read_text())['execution']['evidence']
        self.change()
        payload, code = self.retain()
        self.assertEqual(code, 0, payload)
        self.assertEqual(json.loads(self.path.read_text())['execution']['evidence'], evidence)
        result = reopen_ticket(self.task, 'T001', review_finding='Original AC failure', invalidated_acceptance=['AC1'])
        self.assertEqual(result.outcome, 'reopened')

    def test_stale_retention_and_active_attempt_are_rejected(self):
        self.execute(outcome='interrupted'); self.change()
        self.assertEqual(self.retain()[1], 1)
        _graph('block', self.task, 'T001', {'blocker': {'category': 'requirement', 'reason': 'Changed', 'release_condition': 'Reconciled'}, 'evidence': {}})
        self.assertEqual(self.retain(expected_authority='0' * 64)[1], 1)
        self.assertEqual(self.retain()[1], 0)

    def test_direct_graph_retry_complete_and_reopen_reject_stale_authority(self):
        self.execute(outcome='interrupted'); self.change()
        for operation in ('retry', 'complete'):
            result = _graph(operation, self.task, 'T001', {})
            self.assertFalse(result['ok'])
            self.assertEqual(result['problems'][0]['code'], 'upstream_changed')

    def test_ticket_edit_invalidates_authority_even_with_same_spec(self):
        self.execute(outcome='interrupted')
        t = json.loads(self.path.read_text()); t['acceptance_criteria'][0]['description'] = 'Different'
        self.path.write_text(json.dumps(t))
        self.assertEqual(self.execute().outcome, 'blocked')

    def test_resume_precedes_other_ready_ticket(self):
        self.execute(outcome='interrupted')
        second = ticket(); second['id'] = 'T002'
        (self.task/'tickets/T002-test.json').write_text(json.dumps(second))
        result = self.execute()
        self.assertEqual(result.ticket_id, 'T001')
        self.assertEqual(result.outcome, 'completed')

    def test_failed_requirement_receipt_blocks_instead_of_retrying(self):
        result = self.execute(outcome='failed', acceptance_protocol_gaps=[{'category': 'contract', 'severity': 'P1', 'evidence': 'Expected value missing', 'recommended_route': 'to-spec'}])
        self.assertEqual(result.outcome, 'blocked')

    def test_new_acceptance_can_stop_old_attempt_before_reconciliation(self):
        self.execute(outcome='interrupted')
        p = self.task / 'SPEC.md'; p.write_text(p.read_text() + '- **AC2** — Covers: R1. Additional behavior.\n')
        stopped = _graph('block', self.task, 'T001', {'blocker': {'category': 'requirement', 'reason': 'Amended', 'release_condition': 'Reconcile'}, 'evidence': {}})
        self.assertTrue(stopped['ok'], stopped)
        self.assertFalse(stopped['graph']['valid'])
        extra = {key: value for key, value in ticket().items() if key in {'title','covers','design_decisions','what_to_build','constraints','acceptance_criteria','dependencies'}}
        extra['covers'] = {'requirements': [], 'spec_acceptance': ['AC2']}
        extra['acceptance_criteria'] = [{'id': 'AC1', 'description': 'Additional behavior.'}]
        result, code = reconcile_batch(self.task, {'reason': 'Add behavior', 'operations': [
            {'operation':'create', 'key':'extra', 'ticket':extra},
            {'operation':'retain_contract','ticket_id':'T001','reason':'Original AC1 unchanged','expected_authority':authority_fingerprint(self.task)},
        ]})
        self.assertEqual(code, 0, result)
        self.assertTrue(result['graph']['valid'])

    def test_open_bound_ticket_cannot_silently_adopt_changed_spec(self):
        from loopx.graph.execution_graph.authority import bind_authority
        t = ticket(); bind_authority(self.task, t, 'Confirmed split')
        self.path.write_text(json.dumps(t)); self.change()
        self.assertEqual(self.execute().outcome, 'blocked')

    def test_final_review_tracks_gitlink_worktree_content(self):
        child = self.workspace / 'vendor'; child.mkdir()
        subprocess.run(['git','init','-q',str(child)], check=True)
        source = child / 'code.py'; source.write_text('print(1)\n')
        subprocess.run(['git','-C',str(child),'add','.'], check=True)
        subprocess.run(['git','-C',str(child),'-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','child'], check=True)
        sha = subprocess.check_output(['git','-C',str(child),'rev-parse','HEAD'],text=True).strip()
        subprocess.run(['git','-C',str(self.workspace),'update-index','--add','--cacheinfo','160000,' + sha + ',vendor'],check=True)
        self.execute(); context = delivery.prepare(self.task,self.workspace)
        delivery.complete(self.task,self.review_request(context))
        source.write_text('print(999)\n')
        self.assertEqual(delivery.status(self.task)['state'],'stale')

    def review_request(self, context):
        value = receipt()
        return {'snapshot': context['snapshot'], **{key: value[key] for key in (
            'acceptance_evidence', 'verification', 'review', 'blocking_findings',
            'non_blocking_findings', 'acceptance_protocol_gaps', 'unverified_scope', 'unverified')}}

    def test_delivery_cli_prepare_complete_and_status(self):
        from loopx.cli import main
        def invoke(*args):
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                code = main(['loop', *args])
            payload = json.loads(stream.getvalue())
            self.assertEqual(code, 0, payload)
            return payload['result']
        self.execute()
        context = invoke('delivery-prepare', str(self.task), '--workspace', str(self.workspace))
        request = self.task / '.loop/review-input.json'
        request.write_text(json.dumps(self.review_request(context)))
        self.assertEqual(invoke('delivery-complete', str(self.task), '--input', str(request))['state'], 'passed')
        self.assertEqual(invoke('status', str(self.task))['delivery_review']['state'], 'passed')
        self.code.write_text('print(3)\n')
        self.assertEqual(invoke('status', str(self.task))['delivery_review']['state'], 'stale')

    def test_final_review_covers_current_spec_and_expires_after_code_change(self):
        self.execute()
        context = delivery.prepare(self.task, self.workspace)
        self.assertEqual(delivery.status(self.task)['state'], 'pending')
        self.assertEqual(delivery.complete(self.task, self.review_request(context))['state'], 'passed')
        self.code.write_text('print(2)\n')
        self.assertEqual(delivery.status(self.task)['state'], 'stale')
        with self.assertRaises(ValueError): delivery.complete(self.task, self.review_request(context))

    def test_final_review_rejects_missing_acceptance_and_failed_verification(self):
        self.execute(); context = delivery.prepare(self.task, self.workspace)
        request = self.review_request(context)
        for key, value in [('acceptance_evidence', []), ('verification', []), ('verification', [{'command': 'check', 'exit_code': 1, 'summary': 'Failed'}]), ('unverified_scope', ['integration'])]:
            invalid = copy.deepcopy(request); invalid[key] = value
            with self.assertRaises(ValueError): delivery.complete(self.task, invalid)
        self.assertEqual(delivery.status(self.task)['state'], 'pending')

    def test_final_review_expires_after_requirements_or_graph_change(self):
        self.execute(); context = delivery.prepare(self.task, self.workspace)
        self.change(); self.retain()
        with self.assertRaises(ValueError): delivery.complete(self.task, self.review_request(context))
        self.assertEqual(delivery.status(self.task)['state'], 'stale')

    def test_failed_batch_stops_before_dispatching_sibling(self):
        second = ticket(); second['id'] = 'T002'
        (self.task/'tickets/T002-test.json').write_text(json.dumps(second))
        calls = []
        def worker(bundle):
            calls.append(bundle['ticket']['id']); return receipt(outcome='interrupted')
        results = dispatch_ready(self.task, worker, workspace_root=self.workspace, allowed_write_scope=['src.py'])
        self.assertEqual(calls, ['T001'])
        self.assertEqual(results[0].outcome, 'interrupted')
