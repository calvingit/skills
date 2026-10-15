# Execution script inputs

Resolve scripts relative to this installed skill, preserving sibling `shared/`. Python 3.10+ on macOS/Linux is sufficient; no global CLI install. `--input` accepts a UTF-8 JSON path or `-` for stdin. Responses are JSON and nonzero exits mean rejection. Graph Workflow supplies decisions; scripts only check and record facts.

These commands change `.loop/state.json` only. Ticket documents are contracts and stay byte-identical through `start`, `retry`, `block`, `unblock`, `complete` and `reopen`; only `to-tickets` reconciliation writes them.

## Attempts and ticket state

```bash
python3 <graph-workflow-skill>/scripts/frontier <task-dir>
python3 <graph-workflow-skill>/scripts/graph-query show <task-dir> T001
python3 <graph-workflow-skill>/scripts/update-status start <task-dir> T001 --input <request.json>
python3 <graph-workflow-skill>/scripts/update-status complete <task-dir> T001 --input <request.json>
```

| Operation | Required JSON fields |
| --- | --- |
| `start` | `baseline` (object: `reference`, `staged`, `unstaged`, `untracked`), `existing_changes` (object: `included`, `excluded`; both path arrays), `allowed_write_scope` (nonempty relative-path array; guidance, not a write restriction); optional `mode` (`serial` by default; `swarm` only when the user asked for it) |
| `retry` | `baseline`, `existing_changes`, `expected_attempt` (current number), `findings` (original report string); optional `allowed_write_scope` (defaults to the current attempt's) |
| `block` | `blocker` (`category`, `reason`, `release_condition`), `evidence` (local AC ID → result/summary) |
| `unblock` | `release_evidence` (Loop-confirmed explanation) |
| `complete` | `expected_attempt`, `evidence`, `verification`; optional `review` (actual original report) |
| `reopen` | `review_finding`, `invalidated_acceptance` (local AC ID array), `upstream_unchanged: true` |
| `init-state` | `reason` (why recorded progress is considered lost); only after the user explicitly asks to re-initialize a graph whose state file was lost or is unreadable |

`update-status` owns every state write; Each successful write returns the updated `graph` (frontier, blocked, stale authority); use it to choose the next ticket instead of re-querying. Run `frontier` when resuming a session or before finalization, where its `delivery_review` status is needed. Example start request:

```json
{
  "baseline": {"reference": "<actual commit or recorded baseline>", "staged": [], "unstaged": [], "untracked": []},
  "existing_changes": {"included": [], "excluded": []},
  "allowed_write_scope": ["src/"]
}
```

Graph Workflow must inspect the actual baseline, paths and existing changes; empty arrays in this example are not workspace facts. A second concurrent attempt is refused as `parallel_dispatch_requires_swarm` unless the request carries `mode: swarm`, and under swarm a direct dependency (`dependency_blocks_parallel_dispatch`) or overlapping expected write areas (`write_scope_overlap`) are still refused. Example complete request:

```json
{
  "expected_attempt": 1,
  "evidence": {"AC1": {"result": "passed", "summary": "Observed required API result."}},
  "verification": [{"command": "project test command", "exit_code": 0, "summary": "Required checks passed."}]
}
```

Ticket completion is Graph Workflow's approval of local acceptance and releases dependencies; it does not pass final delivery. Call it only after confirming no unresolved blockers or required unverified scope. Evidence must cover every current `delivery_acceptance` ID and is stored with the attempt that established it, so a later reader can locate the right report under `.loop/`. Optional review must be a nonempty original report from an actual review, never a placeholder for deferred final review. Supply real results, not these illustrative strings. Stored runtime fields (phase, attempt, authority, evidence, blocker, current attempt, reopen context) follow the [shared runtime schema](../../shared/runtime-state-schema.json); ticket contracts follow the [shared ticket schema](../../shared/ticket-schema.json).

## Delivery and recovery

Unlike ticket completion, final delivery requires an original independent review. The `delivery-complete` input has `snapshot` (returned by preparation), `evidence` keyed by SPEC AC, `verification`, `review`, `approved`, and `unverified`; it does not take `expected_attempt`.

Whole-delivery preparation/completion use `scripts/update-status delivery-prepare|delivery-complete`; see [finalization](delivery-review.md) for the input and required workflow. Queries use `scripts/frontier` or `scripts/graph-query inspect|list|show`. `list` supports `--phase` and `--readiness`.

`python3 <graph-workflow-skill>/scripts/update-status recover <task-dir> commit|rollback` recovers interrupted graph transactions; a transaction switches the ticket contracts and `.loop/state.json` together or not at all. It does not resume an Agent. `init-state` rebuilds a lost or unreadable state file with every ticket `open`, no attempt and no evidence, and refuses while a readable one exists. Upstream graph reconciliation and v3 conversion belong to `to-tickets`, after Graph Workflow stops writers.
