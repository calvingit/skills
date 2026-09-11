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

D references may be empty when HLD is not required. Candidate dependencies name other candidate keys. Scripts allocate immutable IDs and initialize lifecycle/execution; callers do not supply either. Local AC IDs are scoped to each ticket, while `covers.spec_acceptance` references SPEC IDs.

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

## Validate and migrate

```bash
python3 <to-tickets-skill>/scripts/validate-graph <task-dir>
python3 <to-tickets-skill>/scripts/migrate-graph <task-dir>
python3 <to-tickets-skill>/scripts/migrate-graph <task-dir> --recover commit
python3 <to-tickets-skill>/scripts/migrate-graph <task-dir> --recover rollback
```

Migration only renames v1 `design_decisions` / `acceptance_criteria` to v2 `referenced_design_decisions` / `delivery_acceptance` and sets `schema_version: 2`. It preserves IDs, dependencies, lifecycle, attempts, evidence and authority binding, including stale bindings. It rejects active attempts, ambiguous/malformed records and unknown versions before writing. Stop writers and block attempts using the previous version before upgrading an active graph. Interrupted graph writes use explicit recovery. Rollback restores the original bytes; a rolled-back v1 graph still needs migration before v2 execution.

A stored final delivery snapshot becomes stale after migration because ticket file bytes changed. Loop must repeat final verification/review before marking that delivery passed. No automatic compatibility reader or global CLI fallback is provided.
