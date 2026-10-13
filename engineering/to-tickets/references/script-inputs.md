# Graph script inputs

Use Python 3.10+ on macOS/Linux. Resolve script paths from the installed skill, preserving sibling `shared/`. Inputs accept a UTF-8 JSON file or `--input -` for stdin. Success/error results are JSON; exit 0 means accepted, nonzero means rejected. These are state commands, not Agent commands.

## Create

`python3 <to-tickets-skill>/scripts/create-graph create-batch <task-dir> --input <request.json>`

```json
{
  "tickets": [{
    "key": "send-message",
    "title": "Send and observe a message",
    "covers": {"requirements": ["R1"], "spec_acceptance": ["AC1"]},
    "referenced_design_decisions": ["D1"],
    "what_to_build": "The caller can send a message and observe its confirmed result.",
    "constraints": ["Use the persistence boundary established by D1."],
    "delivery_acceptance": [{"id": "AC1", "description": "The returned result satisfies SPEC AC1."}],
    "dependencies": []
  }]
}
```

D references may be empty when HLD is not required. `constraints` may be `[]` when the ticket has no specific constraint; entries, when present, must be non-empty and unique. Candidate dependencies name other candidate keys. Scripts allocate immutable IDs and initialize lifecycle/execution; callers do not supply either. Local AC IDs are scoped to each ticket, while `covers.spec_acceptance` references SPEC IDs.

## Reconcile

`python3 <to-tickets-skill>/scripts/create-graph reconcile-batch <task-dir> --input <request.json>`

Read [amendment rules](amendment.md) first. Request: `{"reason":"confirmed upstream delta","operations":[...]}`. Supported operations:

| Operation | Fields in addition to `operation` |
| --- | --- |
| `create` | `key`, `ticket` (same contract fields as create, excluding `key`; dependency references may be existing IDs or new keys) |
| `update_contract` | `ticket_id`, `changes` (nonempty subset of title, covers, referenced_design_decisions, what_to_build, constraints, delivery_acceptance) |
| `supersede` | `ticket_id`, `replacement` (ID/key or null), `reason`; optional `worker_stopped` |
| `replace_dependency` | `ticket_id`, `from`, `to` |
| `retain_contract` | `ticket_id`, `reason`, `expected_authority` |

Loop must stop writers and block active attempts before reconciliation. Completed contracts are not rewritten. Reconciliation is graph maintenance, not retry or Agent dispatch.

## Validate

```bash
python3 <to-tickets-skill>/scripts/validate-graph <task-dir>
```

Graph transaction recovery is available through `loop`'s `update-status recover` command.

## Migrate legacy JSON tickets

```bash
python3 <to-tickets-skill>/scripts/create-graph migrate <task-dir> --dry-run   # default: report only
python3 <to-tickets-skill>/scripts/create-graph migrate <task-dir> --apply     # commit
```

No `--input`. Migration validates the v2 JSON graph, converts each ticket to [Markdown](ticket-format.md), validates the new graph, proves every field round-trips unchanged (including authority binding status), then commits through the graph transaction and deletes the JSON files. A task with any Markdown ticket is refused; the same ID in both formats is reported as `mixed_ticket_formats` and never resolved automatically. If interrupted, `loop/scripts/update-status recover <task-dir> rollback|commit` restores the JSON graph or finishes the switch.
