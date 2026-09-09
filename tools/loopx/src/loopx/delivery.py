"""Whole-delivery review bound to current requirements, graph and code.

The caller runs verify and code-review against prepare()'s context. complete()
accepts their receipt only while that exact context is still current.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

from .graph.execution_graph.authority import authority_index, authority_fingerprint
from .graph.execution_graph.contracts import validate_worker_receipt
from .loop_runtime import _graph, _graph_files, _workspace_snapshot, _workspace_revision, _completion_gate_problem


def _write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=path.parent, delete=False) as stream:
            temporary = stream.name
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def _snapshot(task_dir: Path, workspace: Path) -> tuple[str, dict]:
    graph = _graph('inspect', task_dir)
    if not graph.get('ok') or not graph['graph'].get('delivery_ready'):
        raise ValueError('All active tickets need current authority and passed delivery before whole-task review.')
    artifact_root = task_dir / '.loop'

    def contents(root: Path) -> dict:
        files = _workspace_snapshot(root)
        if files is None:
            raise ValueError('A readable Git workspace is required.')
        code = {}
        for relative, (_state, digest) in files.items():
            path = root / relative
            if path.is_relative_to(artifact_root):
                continue
            if path.is_file() and digest is None:
                raise ValueError('Unable to fingerprint workspace file: ' + str(path))
            mode = path.lstat().st_mode if path.exists() or path.is_symlink() else None
            link = os.readlink(path) if path.is_symlink() else None
            code[relative] = [digest, mode, link]
        tracked = subprocess.run(['git', '-C', str(root), 'ls-files', '--stage', '-z'], capture_output=True, check=True)
        for entry in tracked.stdout.split(b'\0'):
            if not entry:
                continue
            metadata, relative_bytes = entry.split(b'\t', 1)
            if metadata.split()[0] != b'160000':
                continue
            relative = os.fsdecode(relative_bytes)
            child = root / relative
            # Git can discover the parent repository in an uninitialised directory;
            # require the submodule's own Git marker before recursing.
            if not (child / '.git').exists() or child.is_symlink():
                raise ValueError('Submodule is unavailable for review: ' + relative)
            code[relative] = {'head': _workspace_revision(child), 'gitlink': metadata.decode(), 'files': contents(child)}
        return code

    code = contents(workspace)
    state = {
        'task_dir': str(task_dir), 'workspace': str(workspace),
        'head': _workspace_revision(workspace), 'code': code,
        'authority': authority_fingerprint(task_dir),
        'graph': {name: hashlib.sha256(data).hexdigest() for name, data in _graph_files(task_dir).items()},
    }
    token = hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()
    return token, graph['graph']


def prepare(task_dir: Path, workspace: Path) -> dict:
    task_dir, workspace = task_dir.resolve(), workspace.resolve()
    token, graph = _snapshot(task_dir, workspace)
    ids, problems = authority_index(task_dir)
    if problems:
        raise ValueError('Unable to read acceptance authority.')
    context = {
        'snapshot': token, 'workspace': str(workspace),
        'spec': (task_dir / 'SPEC.md').read_text(),
        'hld': (task_dir / 'HLD.md').read_text() if (task_dir / 'HLD.md').is_file() else None,
        'acceptance': (task_dir / 'ACCEPTANCE.md').read_text() if (task_dir / 'ACCEPTANCE.md').is_file() else None,
        'spec_acceptance': sorted(ids['spec_acceptance']),
        'tickets': {name: json.loads(data) for name, data in _graph_files(task_dir).items() if name.startswith('tickets/')},
        'graph': graph,
    }
    if _snapshot(task_dir, workspace)[0] != token:
        raise ValueError('Delivery changed while preparing review.')
    _write(task_dir / '.loop/delivery.json', {'state': 'pending', 'context': context})
    return context


def complete(task_dir: Path, request: dict) -> dict:
    task_dir = task_dir.resolve()
    path = task_dir / '.loop/delivery.json'
    artifact = json.loads(path.read_text())
    context = artifact['context']
    fields = {'snapshot', 'acceptance_evidence', 'verification', 'review', 'blocking_findings',
              'non_blocking_findings', 'acceptance_protocol_gaps', 'unverified_scope', 'unverified'}
    if not isinstance(request, dict) or set(request) != fields:
        raise ValueError('Delivery receipt fields do not match the review contract.')
    if request['snapshot'] != context['snapshot'] or _snapshot(task_dir, Path(context['workspace']))[0] != context['snapshot']:
        raise ValueError('Delivery review is stale; prepare and review the current snapshot.')
    receipt = {key: value for key, value in request.items() if key != 'snapshot'}
    receipt.update(schema_version=1, ticket_id='T000', current_attempt=1, outcome='completed',
                   landed_changes=[], simplification={'result': 'no_change'}, blocker=None)
    problems = validate_worker_receipt(receipt)
    if problems:
        raise ValueError('Invalid delivery review receipt: ' + json.dumps(problems))
    ticket = {'acceptance_criteria': [{'id': value} for value in context['spec_acceptance']]}
    gate = _completion_gate_problem(task_dir, ticket, receipt)
    if gate:
        raise ValueError(gate['detail'])
    # Recheck after validation, before accepting the receipt. Any subsequent change
    # also invalidates status(), so completion cannot become permanently stale-green.
    if _snapshot(task_dir, Path(context['workspace']))[0] != context['snapshot']:
        raise ValueError('Delivery changed while accepting review.')
    _write(path, {'state': 'passed', 'context': context, 'receipt': request})
    return {'state': 'passed', 'snapshot': context['snapshot']}


def status(task_dir: Path) -> dict:
    task_dir = task_dir.resolve()
    path = task_dir / '.loop/delivery.json'
    if not path.exists():
        return {'state': 'not_reviewed'}
    try:
        artifact = json.loads(path.read_text())
        context = artifact['context']
        current, _ = _snapshot(task_dir, Path(context['workspace']))
        return {'state': artifact['state'] if current == context['snapshot'] else 'stale', 'snapshot': context['snapshot']}
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError):
        return {'state': 'stale'}
