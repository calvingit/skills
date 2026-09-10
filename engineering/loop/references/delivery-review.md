# Final delivery review

Read when the graph reports `delivery_ready: true`: active tickets are done and their requirement bindings are current. Do not reopen all tickets merely to perform this review.

1. Run `loopx loop delivery-prepare <task-dir> --workspace <repo-root>`. The returned context contains the current SPEC, optional HLD/ACCEPTANCE, full ticket graph, SPEC AC IDs, and a snapshot token. It records a pending review under `.loop/delivery.json`.
2. Ask `verify` to check the final workspace against every current SPEC AC, including the required integration paths. Use the prepared context as the handoff bundle. Keep temporary outputs under the task's `.loop/`; do not modify product code during review. Reuse prior evidence only after confirming its acceptance meaning, dependencies, code, and environment remain applicable; identify its source in the summary. Do not equate historical ticket-local AC IDs with SPEC AC IDs.
3. Run `code-review` in implementation mode against the final scope, confirmed requirements, applicable HLD, and actual verification evidence. Include cross-ticket interactions and regressions from requirement amendments. Keep Contract, Change-surface, and Exploratory separate. Report only current-task blockers; pre-existing unrelated risk stays non-blocking.
4. Fix findings through the owning ticket workflow, not during review. If final delivery review finds a defect, reopen or create the required corrective ticket, then resume Loop. Do not patch product code inside this review. If any code, graph, or authority changed, prepare a new snapshot and recheck affected verification and review before accepting it.
5. Submit the combined receipt with `loopx loop delivery-complete <task-dir> --input <receipt.json>`. Store this input under `.loop/` so writing the report itself does not change reviewed product code. The CLI validates evidence and the snapshot; it does not execute verification or manufacture a review result.

Receipt fields (required, with empty arrays retained):

```json
{
  "snapshot": "<token returned by delivery-prepare>",
  "acceptance_evidence": [
    {"acceptance_id": "AC1", "result": "passed", "summary": "<observable result and evidence source>"}
  ],
  "verification": [
    {"command": "<actual command>", "exit_code": 0, "summary": "<actual result>"}
  ],
  "review": {
    "contract": "pass",
    "change_surface": "pass",
    "exploratory": "pass",
    "protocol_health": "not_triggered"
  },
  "blocking_findings": [],
  "non_blocking_findings": [],
  "acceptance_protocol_gaps": [],
  "unverified_scope": [],
  "unverified": []
}
```

Every current SPEC AC needs passed evidence. Missing evidence, a failed command, a review failure, a blocker, or a stale snapshot prevents completion. Uninitialised submodules prevent preparing a complete code snapshot.

`loop status` reports `not_reviewed`, `pending`, `passed`, or `stale`. The snapshot includes requirements, ticket graph, Git HEAD, workspace file contents/modes/links, and nested submodule code. These are review-artifact states, not new ticket lifecycle states. `.loop/` is reserved for runtime and review artifacts and must not contain product code. A changed external service or test environment still requires a fresh verification decision; filesystem fingerprints cannot prove external state unchanged.
