import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

E = Path(__file__).resolve().parents[2]
class ScriptCliTests(unittest.TestCase):
    def test_all_entrypoints_run_outside_repo_without_pythonpath(self):
        with tempfile.TemporaryDirectory() as directory:
            env = dict(os.environ)
            env.pop('PYTHONPATH', None)
            for skill, names in [('to-tickets', ['create-graph','validate-graph']), ('loop', ['frontier','graph-query','record-attempt','update-status'])]:
                for name in names:
                    result = subprocess.run([sys.executable, str(E / skill / 'scripts' / name), '--help'], cwd=directory, env=env, capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn('usage:', result.stdout)

    def test_entrypoints_reject_other_owners_operations(self):
        for skill, script, args in [('to-tickets','create-graph',['start']), ('loop','update-status',['create-batch']), ('loop','graph-query',['complete']), ('loop','record-attempt',['worker'])]:
            result = subprocess.run([sys.executable, str(E / skill / 'scripts' / script), *args], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)

    def test_each_skill_bundle_runs_with_only_shared_sibling(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(E / 'shared', root / 'shared', ignore=shutil.ignore_patterns('__pycache__', 'tests'))
            env = dict(os.environ)
            env.pop('PYTHONPATH', None)
            for skill, name in [('to-tickets', 'create-graph'), ('loop', 'frontier')]:
                shutil.copytree(E / skill, root / skill, ignore=shutil.ignore_patterns('__pycache__'))
                result = subprocess.run([sys.executable, str(root / skill / 'scripts' / name), '--help'], cwd='/', env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                shutil.rmtree(root / skill)
