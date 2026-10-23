# Graph script inputs

Use Python 3.10+ on macOS/Linux; no global CLI installation is needed. Resolve script paths from the installed skill, preserving sibling `shared/`, which owns the [ticket schema](../../shared/ticket-schema.json), [runtime state schema](../../shared/runtime-state-schema.json), validation and transactional storage. Inputs accept a UTF-8 JSON file or `--input -` for stdin. Success/error results are JSON; exit 0 means accepted, nonzero means rejected. These are state commands, not Agent commands. Read only the operation needed for the current task.

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

D references may be empty when SOLUTION is not required. `constraints` may be `[]` when the ticket has no specific constraint; entries, when present, must be non-empty and unique. Candidate dependencies name other candidate keys. Scripts allocate immutable `T001`-style IDs, resolve dependencies, write the v4 ticket contracts and initialize `.loop/state.json` (every ticket `open`, attempt 0, no evidence), then return the ID mapping and full graph. Callers supply neither IDs nor runtime state. Local AC IDs are scoped to each ticket, while `covers.spec_acceptance` references SPEC IDs.

The [ticket format](ticket-format.md) keeps the readable contract in the Markdown body (title, Delivery, Constraints, Delivery Acceptance), with machine facts in frontmatter. Use `python3 <to-tickets-skill>/scripts/create-graph create-batch --help` for the current command input.

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

Graph Workflow must stop writers and block active attempts before reconciliation. Completed contracts are not rewritten. Reconciliation switches the ticket contracts and the runtime entries in one transaction, so it never leaves a contract updated while progress still points at the old one. It is graph maintenance, not retry or Agent dispatch.

## Convert an existing v3 task

```bash
python3 <to-tickets-skill>/scripts/create-graph migrate-v3 <task-dir>
```

One-off local conversion; see [version boundary](ticket-format.md#version-boundary). It refuses to overwrite runtime state, keeps ticket bodies and IDs, carries over the execution record it can confirm, and reports what it cannot.

## Validate

```bash
python3 <to-tickets-skill>/scripts/validate-graph <task-dir>
```

Graph transaction recovery is available through `graph-workflow`'s `update-status recover` command; a lost or unreadable `.loop/state.json` is rebuilt only through `update-status init-state` on an explicit user request.

