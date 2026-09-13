# Finalization

Read when the graph reports `delivery_ready: true`. Historical completed tickets do not prove the final implementation meets the latest requirements.

1. Run `python3 <loop-skill>/scripts/update-status delivery-prepare <task-dir> --workspace <repo-root>` to record the current requirement, graph, and code snapshot under `.loop/delivery.json`.
2. Run `simplify` on the complete change set after all tickets are completed and obtain its conclusion. Remove only unnecessary complexity in the current scope; do not expand the product requirements. If it changes code or tests, prepare a new snapshot before the following verification and review. No report does not mean no simplification was needed.
3. Use a native `verify` subagent to check every current SPEC AC, including cross-ticket integration. Reuse prior evidence only when its meaning, code, dependencies, and environment remain applicable. Ticket-local AC IDs are not automatically SPEC AC IDs.
4. Use a separate native `code-review` subagent on the complete final change set and evidence, including interactions and regressions from amendments. Read its Markdown directly. Do not ask for a schema or translate its findings into fields.
5. Address required findings before marking the task complete. Required fixes go through corrective tickets, followed by resumed Loop execution. Missing evidence or conflicting requirements need resolution. Apart from the scoped simplify step above, do not fix product code inside finalization.
6. Once you judge delivery acceptable, submit the state record with `python3 <loop-skill>/scripts/update-status delivery-complete <task-dir> --input <path|->`. The original review remains a string. `approved` records Loop's judgement, not a parsed reviewer label. The helper checks evidence and snapshot freshness; it does not perform the review.

Apply Loop's default 600-second inactivity threshold, activity renewal, and [waiting/recovery rules](wait-recovery.md) to finalization roles too. There is no default total time limit; any explicit total budget remains independent. Missing required simplify, verify, or code-review results leave finalization incomplete; do not submit approval or infer a pass from local checks. Any authorised substitution must preserve its authority and evidence source. Recover the missing role while preserving completed tickets.

Store reports and command input under the current task's `.loop/` so they do not change the product snapshot. This directory is exclusively execution output; keep requirements, product code, tests, and necessary configuration outside it. The snapshot still includes full ticket JSON, including execution fields; keep finalization notes in `.loop/` instead of rewriting completed tickets. If code, requirements, graph, or Git HEAD changes, prepare again and recheck affected verification and review. A changed external service or test environment also requires a fresh evidence decision; file fingerprints cannot detect it.

Completion is reported only when `scripts/frontier` shows `delivery_review.state: passed`. Final review continues the same Loop execution; it is not an excuse to stop at `delivery_ready`.
