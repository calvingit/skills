"""Markdown + YAML frontmatter ticket documents (schema v4).

Frontmatter owns machine facts of the contract; the body owns the human contract:

    ---
    <schema_version, id, covers, referenced_design_decisions, dependencies,
     supersession>
    ---

    # <title>

    ## Delivery
    <what_to_build>

    ## Constraints
    - <constraint>

    ## Delivery Acceptance
    - **AC1** — <description>

No field lives in both places. Lifecycle, attempts, evidence, blockers and
authority are runtime state and live in ``.loop/state.json``, never in this
document.
"""

from __future__ import annotations

import re
from typing import Any

from . import frontmatter

FRONTMATTER_FIELDS = (
    "schema_version", "id", "covers", "referenced_design_decisions", "dependencies",
    "supersession",
)
BODY_FIELDS = ("title", "what_to_build", "constraints", "delivery_acceptance")
REPRESENTED_FIELDS = FRONTMATTER_FIELDS + BODY_FIELDS
RUNTIME_KEY = "runtime"
SECTIONS = ("Delivery", "Constraints", "Delivery Acceptance")
ACCEPTANCE_RE = re.compile(r"^- \*\*(AC[0-9]+)\*\* — (.*)$")
CONTINUATION = "  "


class TicketFormatError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail


def split_document(text: str) -> tuple[str, str]:
    if text.startswith("\ufeff"):
        raise TicketFormatError("invalid_frontmatter", "A byte-order mark is not supported.")
    if "\r" in text:
        raise TicketFormatError("invalid_frontmatter", "Use LF line endings.")
    if not text.startswith("---\n"):
        raise TicketFormatError("missing_frontmatter", "Ticket must start with a '---' frontmatter line.")
    end = text.find("\n---\n", 3)
    if end < 0:
        raise TicketFormatError("missing_frontmatter", "Frontmatter must end with a '---' line.")
    return text[4:end + 1], text[end + 5:]


def _items(lines: list[str], section: str) -> list[str]:
    items: list[str] = []
    for line in lines:
        if line.startswith("- "):
            items.append(line[2:])
        elif line.startswith(CONTINUATION) and items:
            items[-1] += "\n" + line[len(CONTINUATION):]
        elif line == "" and items:
            items[-1] += "\n"
        elif line != "":
            raise TicketFormatError("invalid_ticket_body", f"## {section} accepts only '- ' list items.")
    return [item.rstrip("\n") for item in items]


def parse_body(body: str) -> dict[str, Any]:
    lines = body.split("\n")
    index = 0
    while index < len(lines) and lines[index] == "":
        index += 1
    if index >= len(lines) or not lines[index].startswith("# ") or not lines[index][2:].strip():
        raise TicketFormatError("invalid_ticket_body", "Body must begin with a '# <title>' heading.")
    title = lines[index][2:].strip()
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in lines[index + 1:]:
        if line.startswith("# "):
            raise TicketFormatError("invalid_ticket_body", "Only one '# ' title heading is allowed.")
        if line.startswith("## "):
            current = line[3:].strip()
            if current not in SECTIONS:
                raise TicketFormatError("invalid_ticket_body", f"Unknown section: ## {current}")
            if current in sections:
                raise TicketFormatError("invalid_ticket_body", f"Duplicate section: ## {current}")
            sections[current] = []
            continue
        if current is None:
            if line.strip():
                raise TicketFormatError("invalid_ticket_body", "Text after the title must be inside a section.")
            continue
        sections[current].append(line)
    if list(sections) != list(SECTIONS):
        raise TicketFormatError("invalid_ticket_body", "Sections must be exactly: " + ", ".join("## " + s for s in SECTIONS) + ".")
    what = "\n".join(sections["Delivery"]).strip("\n")
    constraints = _items(sections["Constraints"], "Constraints")
    acceptance = []
    for item in _items(sections["Delivery Acceptance"], "Delivery Acceptance"):
        match = ACCEPTANCE_RE.match("- " + item.split("\n", 1)[0])
        if not match:
            raise TicketFormatError("invalid_ticket_body", "Delivery Acceptance items must read '- **AC1** — description'.")
        rest = item.split("\n", 1)[1:]
        acceptance.append({"id": match.group(1), "description": "\n".join([match.group(2), *rest])})
    return {"title": title, "what_to_build": what, "constraints": constraints, "delivery_acceptance": acceptance}


def parse_ticket(text: str) -> tuple[dict[str, Any], str]:
    """Return (ticket, raw body). Raises TicketFormatError or FrontmatterError."""
    head, body = split_document(text)
    meta = frontmatter.loads(head)
    internal = sorted(key for key in meta if key.startswith("_"))
    if internal:
        raise TicketFormatError("invalid_frontmatter", "Underscore keys are reserved: " + ", ".join(internal))
    if RUNTIME_KEY in meta:
        raise TicketFormatError(
            "invalid_frontmatter",
            "Execution state is stored in .loop/state.json and must not appear in the ticket contract.",
        )
    misplaced = sorted(set(meta) & set(BODY_FIELDS))
    if misplaced:
        raise TicketFormatError("duplicated_authority", "Body-owned fields must not appear in frontmatter: " + ", ".join(misplaced))
    contract = parse_body(body)
    ticket: dict[str, Any] = {}
    for key in FRONTMATTER_FIELDS:
        if key in meta:
            ticket[key] = meta[key]
    ticket.update(contract)
    for key, value in meta.items():  # Unknown keys survive so validate_ticket reports them.
        ticket.setdefault(key, value)
    return ticket, body


def _block(text: str) -> str:
    return text.replace("\n", "\n" + CONTINUATION)


def render_body(ticket: dict[str, Any]) -> str:
    lines = ["", f"# {ticket['title']}", "", "## Delivery", "", ticket["what_to_build"], "", "## Constraints", ""]
    lines += [f"- {_block(item)}" for item in ticket["constraints"]]
    if ticket["constraints"]:
        lines.append("")
    lines += ["## Delivery Acceptance", ""]
    lines += [f"- **{item['id']}** — {_block(item['description'])}" for item in ticket["delivery_acceptance"]]
    return "\n".join(lines) + "\n"


def body_matches(body: str, ticket: dict[str, Any]) -> bool:
    try:
        parsed = parse_body(body)
    except TicketFormatError:
        return False
    return all(parsed[key] == ticket.get(key) for key in BODY_FIELDS)


def render_ticket(ticket: dict[str, Any], body: str | None = None) -> str:
    """Serialize a ticket contract. An existing body is kept byte-for-byte when it
    still states the same contract, so metadata updates never rewrite human text.

    Runtime progress is never written here: ``runtime`` is rejected instead of
    being silently dropped, so no caller can store execution state in the ticket.
    """
    stored = {key: value for key, value in ticket.items() if key in REPRESENTED_FIELDS}
    unrepresentable = sorted(
        key for key in ticket
        if not key.startswith("_") and key not in REPRESENTED_FIELDS
    )
    if unrepresentable:
        raise TicketFormatError(
            "unrepresentable_ticket",
            f"Ticket {ticket.get('id')} cannot be stored in Markdown: " + ", ".join(unrepresentable),
        )
    meta = {
        key: value for key, value in stored.items()
        if key in FRONTMATTER_FIELDS and value is not None
    }
    if body is None or not body_matches(body, ticket):
        body = render_body(ticket)
    text = "---\n" + frontmatter.dumps(meta) + "---\n" + body
    reparsed, _ = parse_ticket(text)
    public = {key: value for key, value in stored.items() if value is not None or key != "supersession"}
    if reparsed != public:
        raise TicketFormatError("unrepresentable_ticket", f"Ticket {ticket.get('id')} cannot be represented losslessly in Markdown.")
    return text
