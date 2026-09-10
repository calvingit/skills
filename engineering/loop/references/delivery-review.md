# Final delivery review

Read when the graph reports `delivery_ready: true`. Historical completed tickets do not prove the final implementation meets the latest requirements.

1. Run `loopx loop delivery-prepare <task-dir> --workspace <repo-root>` to record the current requirement, graph, and code snapshot under `.loop/delivery.json`.
2. Use a native `verify` subagent to check every current SPEC AC, including cross-ticket integration. Reuse prior evidence only when its meaning, code, dependencies, and environment remain applicable. Ticket-local AC IDs are not automatically SPEC AC IDs.
3. Use a separate native `code-review` subagent on the final scope and evidence, including interactions and regressions from amendments. Read its Markdown directly. Do not ask for a schema or translate its findings into fields.
4. Required fixes go through corrective tickets, followed by resumed Loop execution. Missing evidence or conflicting requirements need resolution. Do not fix product code inside final review.
5. Once you judge delivery acceptable, submit the state record described in [the delivery command](../../../docs/loop-runtime.md#final-delivery). The original review remains a string. `approved` records Loop's judgement, not a parsed reviewer label. The helper checks evidence and snapshot freshness; it does not perform the review.

Store reports and command input under `.loop/` so they do not change the product snapshot. If code, requirements, graph, or Git HEAD changes, prepare again and recheck affected verification and review. A changed external service or test environment also requires a fresh evidence decision; file fingerprints cannot detect it.

Completion is reported only when `loop status` shows `delivery_review.state: passed`. Final review continues the same Loop execution; it is not an excuse to stop at `delivery_ready`.
