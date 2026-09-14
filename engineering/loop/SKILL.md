---
name: loop
description: Orchestrate a ticket graph in a shared task context, with continuous implementation and final independent verification and review.
---

# Loop

Own ticket selection, implementation handoff, progress, and completion decisions. The main Agent normally implements tickets continuously in its existing context. Use the current runtime's native subagents for independent final `verify` and `code-review`, and selectively for exploration, specialist work, or independent parallel tickets. State scripts only read and write ticket state and delivery progress; they do not execute agents. Do not launch external Agent CLIs or build a session manager, provider, polling, or result-parsing layer. If native subagents are unavailable, report the limitation and keep required independent final acceptance incomplete.

## Execution session

A Loop run owns a logical execution session: shared task context, tickets, and delivery evidence. Tickets and correction attempts are units of work inside it, not independent Agent lifetimes. Continue the same Agent context when work shares project knowledge; a new ticket or attempt does not require a new Agent. Runtime owns actual context continuation, handles, waiting, and cancellation; Loop does not create or destroy Runtime sessions.

The main Agent may edit product code while performing `implement`, then use Loop's state commands to record its decisions. Implementers, including the main Agent in that role, do not edit upstream requirements or tickets. Delegated subagents never mutate the graph or Git history.

## Script entrypoints

Resolve `<loop-skill>` to this installed skill directory. Scripts require Python 3.10+ on macOS/Linux and sibling `engineering/shared/`; no global CLI or Agent-specific SDK is needed. Read [script inputs](references/script-inputs.md) when recording state.

- `scripts/frontier <task-dir>`: readiness, blockers, current attempts and final delivery status.
- `scripts/graph-query inspect|list|show ...`: read-only graph queries.
- `scripts/record-attempt start|retry ...`: record a new/correction attempt.
- `scripts/update-status block|unblock|complete|reopen|recover|delivery-prepare|delivery-complete ...`: persist Loop's decisions and recover interrupted transactions.

Use `python3` plus the resolved script path. These helpers do not choose agents, execute tools, interpret reviews, or make completion decisions.

## Execute

1. Read `python3 <loop-skill>/scripts/frontier <task-dir>`, the current SPEC, optional ACCEPTANCE/HLD, and the relevant tickets. Resolve stale requirements before dispatch. Missing optional documents add no prerequisites.
2. Resume an in-progress ticket before selecting a ready one. Establish the baseline, pre-existing edits, the ticket's file scope (recorded as `allowed_write_scope`), acceptance criteria, and current attempt. For a new attempt use `python3 <loop-skill>/scripts/record-attempt start`; for a correction use `scripts/record-attempt retry`. Use `python3 <loop-skill>/scripts/update-status --help` for the current request shape.
3. Prepare or refresh the task context using [context and delegation](references/context-and-delegation.md). Follow `implement` in the main Agent by default, using the ticket, requirements, baseline/scope, and previous findings. Keep existing context across tickets. Delegate only when cognitive isolation or demonstrably independent work warrants it.
4. Run the smallest local checks that cover **every** current ticket AC, including necessary development tests. Inspect actual changes and results; minimum verification means sufficient coverage, not fewer acceptance criteria. Per-ticket independent verify/review is not required by default. Honour any explicit user/project requirement for additional independent checks.
5. Preserve local command evidence and any delegated text/Markdown reports under the task directory's `.loop/` for resume or handoff. Read reports directly; no JSON response envelope, fixed headings, severity parser, or Markdown-to-JSON conversion is required. Record the executor and coverage so local checks are not presented as independent verification.
6. Decide and record the ticket state through `scripts/update-status`, refresh the frontier, and continue. `done` means local acceptance passed and releases dependencies; only final delivery acceptance completes the task. Default to serial work in the main Agent. Before explicitly choosing parallel delegation, establish no dependency, expected write overlap, unresolved shared design decision, or shared mutable resource conflict. Use Runtime worktrees only when isolation is needed.

## State location

`.loop/` belongs to the task execution context: keep it inside the task directory, next to `SPEC.md` and `tickets/`, and never create it at the repository root, where separate tasks would share one state. It stores execution state — current attempts, preserved reports, command logs, delivery inputs, and derived task context under `.loop/context/` — not project-level configuration. On resume, read the current task directory's `.loop/` first.

## File scope

A ticket's file scope describes expected areas of change. It is guidance for implementation and review, not a hard write restriction: the implementing Agent may modify additional files when required to complete the ticket, keeping additional changes related to the ticket objective and avoiding unrelated refactoring. Pass the scope to review as a reference for expected change areas, not as a boundary that turns related out-of-scope edits into defects.

## Decide from evidence

- A `verify` `FAIL` is a defect only when the verifier actually observed behaviour conflicting with the current confirmed contract. Preserve the original finding and execution evidence, pass them to implement through `scripts/record-attempt retry`, re-run affected local checks, and run required independent verification again. Other green tests do not override it; after code, requirements, graph, or relevant environment changes, do not reuse the old report.
- A `verify` `NOT VERIFIED` is insufficient evidence, not a product defect and not a pass. Classify whether the gap is an environment, permission, dependency, or external blocker (record a release condition), an inadequate verification method (try another minimal read-only check), or an incomplete/conflicting requirement (route to its owner). Do not send an evidence gap directly to implement for code repair or busy-retry an unresolved external blocker.
- Requirement/design conflicts go to their owner. A verifier using the wrong expected behaviour is a contract problem, not a reason to modify implementation to satisfy it.
- An unclear report needs clarification from its author. Do not infer success from silence, wording, headings, or a worker saying it finished. Optional follow-up does not block this change.
- Complete only after inspecting the changed scope, verifying every current AC, and confirming no unresolved blockers or required unverified scope. Submit the local evidence and explicit approval to `scripts/update-status complete`. Review is optional for tickets: include unchanged original text only if a review actually ran, never a placeholder such as "review deferred". The helper validates recorded facts, not prose meaning.
- Final delivery requires independent verification and review with valid reports for the current code before approval. Any additional independent ticket checks explicitly required by the user/project also remain mandatory. Local checks do not replace either role unless the user or project explicitly authorises substitution; record that authority, executor, and coverage. While a report is missing, keep the stage incomplete and `approved: false`. Moving the gap from `unverified` into a note cannot authorise completion; `unverified` describes unchecked scope, not every process limitation. Scripts cannot establish report independence. For required Acceptance Criteria, only `PASS` establishes verification completion; any `FAIL` or `NOT VERIFIED` keeps delivery incomplete until correction, contract resolution, or the evidence gap/blocker is resolved. Do not collapse these verdicts into a binary success/failure result.

JSON remains the storage format for ticket state and command input. A review stored in a JSON string is still the original report; do not extract a second finding schema from it. Use a serializer to store multiline text faithfully.

## Wait and recover

These rules apply to actual delegated executions, not ticket switches in the main Agent.

Native subtasks have **no default total time limit**. Use a **600-second inactivity threshold** from dispatch or the latest qualifying activity, unless the user or project specifies another threshold. New execution messages, tool events/output, or a fresh soft-ping reply renew it; repeated `running` snapshots, old messages, wait expiry, and locally generated heartbeats do not. Renewal shows responsiveness, not effective progress or acceptance. An explicitly configured total budget remains independent and cannot be extended by activity. Command timeouts and native wait windows remain separate.

Keep the handle, role, ticket/attempt or delivery snapshot, dispatch time, latest activity evidence/time, inactivity deadline, and any explicit total deadline in existing `.loop/` execution notes. Preserve these on resume; rereading old evidence must not renew a deadline. Read [waiting and recovery](references/wait-recovery.md) for activity evidence and threshold handling. Without reliable timing evidence, do not claim expiry.

After a wait window ends, check native state and retrieve completed results. If unfinished with no new activity, use at most one non-interrupting soft ping per execution, including across context recovery; read [the inquiry procedure](references/wait-recovery.md#one-progress-inquiry-per-execution) before sending. A missing reply or unavailable query does not prove a stall. At the inactivity threshold, verify state and any known running command before orderly recovery; do not immediately kill or restart a role because it has been quiet. Explicit total-budget expiry, failure/blockage, cancellation, or interruption use the same recovery procedure.

Confirm the old execution and relevant commands have stopped before overlapping work. Preserve partial changes and version-bound reports; recover the affected role without automatically rerunning implementation or relaxing acceptance. Runtime owns handles and cancellation; scripts do not recover Agent sessions.

## Resume and requirement changes

On resume, inspect the recorded native execution before dispatching another role and apply the waiting and recovery rules above.

Before changing shared SPEC/HLD/ACCEPTANCE or reconciling tickets, stop dispatch, interrupt active subagents through the runtime, confirm they stopped writing, preserve partial results, and `scripts/update-status block` their attempts. A graph state change alone does not stop a subagent.

Route unsettled requirement choices to `grilling` first, normative requirement changes to `to-spec`, shared design changes to `high-level-design`, and graph-only amendments to `to-tickets`. Do not inject changed requirements into an old attempt. Keep historical done records; retain only confirmed unaffected contracts/evidence. Changed behaviour needs correction/replacement tickets. Use `reopen` for defects against an unchanged confirmed contract.

## Continue through delivery

One completed ticket, an empty ready list, or `delivery_ready` is not a stopping condition. If tickets remain, resolve actionable retries/blockers and continue. When `delivery_ready` is true, perform [Finalization](references/delivery-review.md) in the same execution.

Stop only when final delivery is passed, the user stops the task, or remaining progress requires unavailable external input/capability. Explain the concrete blocker. The skill directs continued work while the runtime is active; it does not promise autonomous execution after that runtime stops.

Commit only when explicitly authorised. A later code, contract, graph, or Git HEAD change invalidates the recorded final snapshot.
