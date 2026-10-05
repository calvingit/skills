# Finalization

Read when the graph reports `delivery_ready: true`. Historical completed tickets do not prove the final implementation meets the latest requirements. Distinguish initial closeout from rechecking corrections; returning to `delivery_ready` does not restart every finalization role.

## Initial closeout

1. Dispatch a dedicated native `simplify` subagent on the complete change set after all tickets pass local acceptance and record its conclusion. Remove only unnecessary complexity in the current scope; do not expand product requirements. No conclusion does not mean no simplification was needed.
2. After simplification stops writing, run `python3 <loop-skill>/scripts/update-status delivery-prepare <task-dir> --workspace <repo-root>` to record the current requirement, graph, and code snapshot under `.loop/delivery.json` before independent verification and review.
3. Use a native `verify` subagent to check every current SPEC AC, including cross-ticket integration and mandatory project gates. Reuse prior evidence only when its meaning, code, dependencies, and environment remain applicable. Ticket-local AC IDs are not automatically SPEC AC IDs.
4. Use a separate native `code-review` subagent on the complete final change set and evidence, including interactions and regressions from amendments. Read its Markdown directly. Do not ask for a schema or translate its findings into fields.
   Use one reviewer by default. Only for high-impact changes with unresolved, under-evidenced judgements, or an explicit user request for a panel, may the Manager dispatch 2–3 independent reviewers on the same scope and synthesize their findings against the evidence.
5. Address required findings before marking the task complete. For defects in unchanged requirements, use `reopen` only when the graph permits it; otherwise route corrective tickets through `to-tickets`, preserving dependent completed tickets and valid evidence. Resume Loop execution for the corrections, then use correction closeout below. Missing evidence or conflicting requirements need resolution. Apart from the scoped simplify step above, do not fix product code inside finalization.

## Correction closeout

Preserve the initial simplify, verify and broad review reports with their candidate/baseline (including the relevant working-tree diff for an uncommitted candidate) and unresolved findings under `.loop/`. Compare the cumulative correction diff with the most recent completed broad-review candidate, not just the last edit. After an escalated broad review completes, use its candidate/report as the new comparison baseline and retain the earlier history; an already-reviewed scope expansion must not trigger escalation again by itself. Record the affected AC, regression paths, evidence reuse and any escalation reason in the existing closeout notes; no new state fields are needed.

1. Once corrective tickets pass and writers stop, prepare the new delivery snapshot. Preparation overwrites `.loop/delivery.json`, so preserve the prior candidate and reports first.
2. Dispatch independent `verify` for the affected SPEC AC, the original finding's regression and all mandatory project gates. Keep every current SPEC AC accounted for: unchanged AC may retain independently obtained evidence only after its applicability is checked; missing or invalidated evidence must be obtained. Targeted closeout narrows repeated work, not acceptance.
3. Dispatch a separate native `code-review` worker for the cumulative correction diff, original findings and affected callers/integration paths. Ask it to check that the findings are resolved, that the correction introduces no material regression, and that the earlier broad review remains applicable outside this scope. Preserve its original Markdown report and the earlier broad report. Do not default to another full simplify, full verification or broad review.
4. If the targeted checks pass, all current AC and mandatory gates have sufficient evidence, and no required finding or gap remains, complete delivery. Optional improvements do not reopen closeout. An unresolved finding stays in its bounded correction scope; do not repeat an unchanged failing approach without new evidence or a changed correction. If progress requires an unavailable decision, method or capability, report the blocker rather than cycling.

### When to broaden review

Escalate when evidence shows a material impact beyond the prior review basis, including:

- A public contract or shared architecture/HLD behaviour changes.
- A new module/dependency, previously unreviewed critical or security-sensitive path, or new cross-ticket integration surface is introduced or affected.
- Targeted validation discovers an independent material defect, or invalidates the earlier risk judgement.

Resolve requirement/shared-design changes with their owner before dependent work. Record the concrete trigger, then run broad code-review over the complete current change set and expand independent verification to all affected or no-longer-supported AC. Repeat simplify only if its prior conclusion is invalidated by new complexity; escalation alone does not restart every role. Subsequent corrections again default to targeted closeout.

Condition, null/error handling, mapping, local validation and direct regression fixes do not by themselves trigger broad review. Their actual impact can still meet the criteria above; line count or a correction label is not evidence of safety. If the initial broad review was never completed or its report cannot be recovered, obtain it before claiming targeted closeout is sufficient.

## Record completion

Submit `python3 <loop-skill>/scripts/update-status delivery-complete <task-dir> --input <path|->` only after judging delivery acceptable. Keep the existing input shape: `evidence` covers every current SPEC AC, `verification` records actual applicable checks, and `review` is the latest independent report as an original string. For correction closeout, that report must identify the earlier broad report/candidate, the corrected findings, the targeted scope and the applicability of retained review coverage. Retain both reports; do not relabel the old report as a review of new code. `approved` records Loop's judgement, not a parsed reviewer label. The helper checks evidence and snapshot freshness; it neither selects review scope nor performs the review.

Missing required simplify, verify, or code-review results leave finalization incomplete; retrieve or resume the affected role through Runtime while preserving completed tickets and still-valid role results. Do not infer a pass from local checks. Any authorised substitution must preserve its authority, executor, and coverage evidence. Follow Loop's execution boundaries before starting overlapping work.

Store reports and command input under the current task's `.loop/` so they do not change the product snapshot. This directory is exclusively execution output; keep requirements, product code, tests, and necessary configuration outside it. The snapshot still includes full ticket JSON, including execution fields; keep finalization notes in `.loop/` instead of rewriting completed tickets. If code, requirements, graph, or Git HEAD changes, prepare again and recheck affected verification and review. Snapshot invalidation requires reassessment, not automatic broad review. A changed external service or test environment also requires a fresh evidence decision; file fingerprints cannot detect it.

Completion is reported only when `scripts/frontier` shows `delivery_review.state: passed`. Final review continues the same Loop execution; it is not an excuse to stop at `delivery_ready`.
