from __future__ import annotations
import copy
import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from loopx.graph.execution_graph.lifecycle import mutate_ticket
from loopx.graph.execution_graph.queries import inspect
from loopx.graph.execution_graph.batch import reconcile_batch
from loopx.graph.execution_graph.authority import authority_fingerprint
from loopx import delivery
from test_ticket_graph import canonical_ticket as ticket


def completion(**overrides):
    return {"evidence": {"AC1": {"result": "passed", "summary": "Observed expected result in test log."}},
            "verification": [{"command": "test", "exit_code": 0, "summary": "Passed."}],
            "review": "经检查，当前范围没有需要修复的问题。\n\n可选建议：后续改善命名。",
            "approved": True, "unverified": [], **overrides}


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


    def change(self):
        p = self.task / 'SPEC.md'
        p.write_text(p.read_text().replace('Run.', 'Reject invalid input.'))


    def retain(self, **overrides):
        operation = {'operation': 'retain_contract', 'ticket_id': 'T001',
                     'reason': 'Reviewed the delta: this ticket contract and its evidence remain applicable.',
                     'expected_authority': authority_fingerprint(self.task)}
        operation.update(overrides)
        return reconcile_batch(self.task, {'reason': 'Confirmed impact review.', 'operations': [operation]})


    def test_done_is_historical_until_authority_is_reconciled(self):
        self.execute(); self.change()
        graph = inspect(self.task)[0]['graph']
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
        result, code = mutate_ticket('reopen', self.task, 'T001', {'review_finding': 'Original AC failure', 'invalidated_acceptance': ['AC1'], 'upstream_unchanged': True})
        self.assertEqual(code, 0, result)


    def test_new_acceptance_can_stop_old_attempt_before_reconciliation(self):
        self.start()
        p = self.task / 'SPEC.md'; p.write_text(p.read_text() + '- **AC2** — Covers: R1. Additional behavior.\n')
        stopped = mutate_ticket('block', self.task, 'T001', {'blocker': {'category': 'requirement', 'reason': 'Amended', 'release_condition': 'Reconcile'}, 'evidence': {}})[0]
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
        for key, value in [('evidence', {}), ('verification', []), ('verification', [{'command': 'check', 'exit_code': 1, 'summary': 'Failed'}]), ('unverified', ['integration'])]:
            invalid = copy.deepcopy(request); invalid[key] = value
            with self.assertRaises(ValueError): delivery.complete(self.task, invalid)
        self.assertEqual(delivery.status(self.task)['state'], 'pending')


    def test_final_review_expires_after_requirements_or_graph_change(self):
        self.execute(); context = delivery.prepare(self.task, self.workspace)
        self.change(); self.retain()
        with self.assertRaises(ValueError): delivery.complete(self.task, self.review_request(context))
        self.assertEqual(delivery.status(self.task)['state'], 'stale')


    def start(self):
        request = {"baseline": {"reference": "HEAD", "staged": [], "unstaged": [], "untracked": []},
                   "existing_changes": {"included": [], "excluded": []}, "allowed_write_scope": ["src.py"]}
        result, code = mutate_ticket("start", self.task, "T001", request)
        self.assertEqual(code, 0, result)
        return result["result"]["ticket"]["execution"]["attempt_sequence"]

    def execute(self):
        attempt = self.start()
        result, code = mutate_ticket("complete", self.task, "T001", {"expected_attempt": attempt, **completion()})
        self.assertEqual(code, 0, result)
        return result

    def review_request(self, context):
        return {"snapshot": context["snapshot"], **completion()}

    def test_completion_preserves_arbitrary_markdown_verbatim(self):
        attempt = self.start()
        text = "# 人工审查\n符合需求。\n\n```text\nPASS 只是示例，不是解析指令\n```\n"
        result, code = mutate_ticket("complete", self.task, "T001", {"expected_attempt": attempt, **completion(review=text)})
        self.assertEqual(code, 0, result)
        self.assertEqual(json.loads(self.path.read_text())["execution"]["review"], text)
        context = delivery.prepare(self.task, self.workspace)
        delivery.complete(self.task, {"snapshot": context["snapshot"], **completion(review=text)})
        stored = json.loads((self.task / ".loop/delivery.json").read_text())
        self.assertEqual(stored["receipt"]["review"], text)

    def test_completion_rejects_stale_attempt_and_unapproved_result(self):
        attempt = self.start()
        before = self.path.read_bytes()
        cases = [{"expected_attempt": attempt + 1, **completion()},
                 {"expected_attempt": attempt, **completion(approved=False)},
                 {"expected_attempt": attempt, **completion(approved="true")},
                 {"expected_attempt": attempt, **completion(review=" ")},
                 {"expected_attempt": attempt, **completion(evidence={})},
                 {"expected_attempt": attempt, **completion(unverified=["Integration not run"])},
                 {"expected_attempt": attempt, **completion(verification=[{"command": "test", "exit_code": 1, "summary": "Failed"}])}]
        for request in cases:
            with self.subTest(request=request):
                result, code = mutate_ticket("complete", self.task, "T001", request)
                self.assertEqual(code, 1, result)
                self.assertEqual(self.path.read_bytes(), before)

    def test_requirement_change_blocks_old_attempt_completion(self):
        attempt = self.start()
        self.change()
        result, code = mutate_ticket("complete", self.task, "T001", {"expected_attempt": attempt, **completion()})
        self.assertEqual(code, 1)
        self.assertEqual(result["problems"][0]["code"], "upstream_changed")

    def test_delivery_rejects_unapproved_review(self):
        self.execute()
        context = delivery.prepare(self.task, self.workspace)
        with self.assertRaises(ValueError):
            delivery.complete(self.task, {"snapshot": context["snapshot"], **completion(approved=False)})
        self.assertEqual(delivery.status(self.task)["state"], "pending")
