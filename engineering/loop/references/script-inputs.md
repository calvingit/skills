# Execution script inputs

Resolve scripts relative to this installed skill, preserving sibling `shared/`. Python 3.10+ on macOS/Linux is sufficient; no global CLI install. `--input` accepts a UTF-8 JSON path or `-` for stdin. Responses are JSON and nonzero exits mean rejection. Loop supplies decisions; scripts only check and record facts.

## Attempts and ticket state

```bash
python3 <loop-skill>/scripts/frontier <task-dir>
python3 <loop-skill>/scripts/graph-query show <task-dir> T001
python3 <loop-skill>/scripts/record-attempt start <task-dir> T001 --input <request.json>
python3 <loop-skill>/scripts/update-status complete <task-dir> T001 --input <request.json>
```

| Operation | Required JSON fields |
| --- | --- |
| `start` | `baseline` (object: `reference`, `staged`, `unstaged`, `untracked`), `existing_changes` (object: `included`, `excluded`; both path arrays), `allowed_write_scope` (nonempty relative-path array; guidance, not a write restriction) |
| `retry` | start fields plus `expected_attempt` (current number), `findings` (original report string) |
| `block` | `blocker` (`category`, `reason`, `release_condition`), `evidence` (local AC ID → result/summary) |
| `unblock` | `release_evidence` (Loop-confirmed explanation) |
| `complete` | `expected_attempt`, `evidence`, `verification`, `review`, `approved`, `unverified` |
| `reopen` | `review_finding`, `invalidated_acceptance` (local AC ID array), `upstream_unchanged: true` |

`retry` belongs to `record-attempt`; other state mutations belong to `update-status`. Example complete request:

```json
{
  "expected_attempt": 1,
  "evidence": {"AC1": {"result": "passed", "summary": "Observed required API result."}},
  "verification": [{"command": "project test command", "exit_code": 0, "summary": "Required checks passed."}],
  "review": "Original review text, preserved without parsing.",
  "approved": true,
  "unverified": []
}
```

Evidence must cover every current `delivery_acceptance` ID. Supply real results, not these illustrative strings. Blocker kinds and other stored fields use the [shared schema](../../shared/ticket-schema.json).

## Delivery and recovery

The `delivery-complete` input has `snapshot` (returned by preparation), `evidence` keyed by SPEC AC, `verification`, `review`, `approved`, and `unverified`; it does not take `expected_attempt`.

Whole-delivery preparation/completion use `scripts/update-status delivery-prepare|delivery-complete`; see [finalization](delivery-review.md) for the input and required workflow. Queries use `scripts/frontier` or `scripts/graph-query inspect|list|show`. `list` supports `--phase` and `--readiness`.

`python3 <loop-skill>/scripts/update-status recover <task-dir> commit|rollback` recovers interrupted graph transactions. It does not resume an Agent. Upstream graph reconciliation belongs to `to-tickets`, after Loop stops writers.
