from pathlib import Path
import sys
ENGINEERING = Path(__file__).resolve().parents[2]
for path in (ENGINEERING / 'shared', ENGINEERING / 'to-tickets/scripts', ENGINEERING / 'graph-workflow/scripts'):
    sys.path.insert(0, str(path))

from ticket_graph import frontmatter as _frontmatter
from ticket_graph.ticket_markdown import BODY_FIELDS as _BODY, parse_ticket as _parse, render_body as _render_body


def read_ticket(path):
    """Parse a stored Markdown ticket into the internal ticket object."""
    return _parse(Path(path).read_text(encoding='utf-8'))[0]


def dump_ticket(ticket):
    """Write any ticket dict, valid or not, so tests can feed invalid contracts."""
    meta = {key: value for key, value in ticket.items() if key not in _BODY and not key.startswith('_')}
    body = _render_body(ticket) if 'title' in ticket else '\n## Delivery\n\nx\n'
    return '---\n' + _frontmatter.dumps(meta) + '---\n' + body
