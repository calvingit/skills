"""Test adapter: build the two stores a v4 graph uses, contract and runtime state."""
from pathlib import Path
import json
import sys
ENGINEERING = Path(__file__).resolve().parents[2]
for path in (ENGINEERING / 'shared', ENGINEERING / 'to-tickets/scripts', ENGINEERING / 'graph-workflow/scripts'):
    sys.path.insert(0, str(path))

from ticket_graph import frontmatter as _frontmatter
from ticket_graph import runtime as _runtime
from ticket_graph.ticket_markdown import (
    BODY_FIELDS as _BODY, RUNTIME_KEY as _RUNTIME, parse_ticket as _parse, render_body as _render_body,
)


def read_ticket(path):
    """Parse a stored Markdown ticket into its contract."""
    return _parse(Path(path).read_text(encoding='utf-8'))[0]


def dump_ticket(ticket):
    """Write any ticket contract, valid or not, so tests can feed invalid documents."""
    meta = {
        key: value for key, value in ticket.items()
        if key not in _BODY and key != _RUNTIME and not key.startswith('_')
    }
    body = _render_body(ticket) if 'title' in ticket else '\n## Delivery\n\nx\n'
    return '---\n' + _frontmatter.dumps(meta) + '---\n' + body


def state_file(task_dir):
    return Path(task_dir) / _runtime.STATE_FILE


def read_state(task_dir):
    """The stored runtime state; empty when the file does not exist."""
    path = state_file(task_dir)
    return json.loads(path.read_text(encoding='utf-8')) if path.is_file() else {}


def runtime_entry(task_dir, ticket_id):
    """The current runtime entry of one ticket."""
    return read_state(task_dir).get('tickets', {})[ticket_id]


def merge_entry(task_dir, ticket_id, entry):
    """Write one runtime entry, keeping the other tickets' progress."""
    state = read_state(task_dir)
    if not state:
        state = {'schema_version': _runtime.RUNTIME_SCHEMA_VERSION, 'tickets': {}}
    state['tickets'][ticket_id] = entry
    _runtime.write_state(Path(task_dir), state)


def write_ticket(task_dir, ticket, filename=None):
    """Write a ticket contract file and its runtime entry, as production does."""
    path = Path(task_dir) / 'tickets' / (filename or f"{ticket['id']}-ticket.md")
    path.write_text(dump_ticket(ticket), encoding='utf-8')
    merge_entry(task_dir, ticket['id'], ticket.get(_RUNTIME, _runtime.fresh_entry()))
    return path
