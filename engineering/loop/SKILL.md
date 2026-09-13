---
name: loop
description: Drive a ticket graph through implementation, verification, and review using the current runtime's subagents.
---

# Loop

Own ticket selection, handoff, progress, and completion decisions. Use the current runtime's native subagents for `implement`, `verify`, and `code-review`. Skill-local state scripts only reads and writes ticket state and delivery progress; it does not execute agents. Do not launch external Agent CLIs or build a session, provider, polling, or result-parsing layer. If native subagents are unavailable, report that limitation; do not silently substitute an external CLI or claim independent review.

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
3. Give a native subagent the `implement` skill, ticket, current requirements, baseline/scope, and previous findings. Let it implement and simplify that scope. Subagents do not edit upstream documents, tickets, or Git history. Apply the waiting and recovery rules below to every dispatched role, including finalization.
4. After implementation stops writing, use a separate native subagent for `verify`. Pass the actual changes and requirements; it runs the necessary checks and returns observed results. Then use a separate native subagent for `code-review`, with the scope, requirements, code, and verification evidence. Do not run review against code that is still changing.
5. Read their text/Markdown results directly. Preserve the original reports under the task directory's `.loop/` when needed for resume or handoff. No JSON response envelope, fixed headings, severity parser, or Markdown-to-JSON conversion is required.
6. Decide the next state and write it through `scripts/update-status`. Refresh status and continue immediately to the next actionable ticket. Default to serial execution; use parallel tickets only when the runtime supports them and their expected changes and dependencies are demonstrably independent. Use worktrees only when isolation is needed, through the runtime's existing capabilities.

## State location

`.loop/` belongs to the task execution context: keep it inside the task directory, next to `SPEC.md` and `tickets/`, and never create it at the repository root, where separate tasks would share one state. It stores execution state — current attempts, preserved reports, command logs, delivery inputs — not project-level configuration. On resume, read the current task directory's `.loop/` first.

## File scope

A ticket's file scope describes expected areas of change. It is guidance for implementation and review, not a hard write restriction: the implement subagent may modify additional files when required to complete the ticket, keeping additional changes related to the ticket objective and avoiding unrelated refactoring. Pass the scope to review as a reference for expected change areas, not as a boundary that turns related out-of-scope edits into defects.

## Decide from evidence

- A confirmed defect in the current contract goes back to implement through `scripts/record-attempt retry`, with the original findings as text. Re-run affected verification and review.
- Requirement/design conflicts go to their owner. Missing access, permissions, dependencies, or evidence needs a specific blocker and release condition. Do not busy-retry unresolved external blockers.
- An unclear report needs clarification from its author. Do not infer success from silence, wording, headings, or a worker saying it finished. Optional follow-up does not block this change.
- Complete only after inspecting the changed scope, verifying every current AC, and confirming no unresolved blockers or required unverified scope. Pass the review string unchanged and your explicit approval to `scripts/update-status complete`; the helper validates recorded facts, not prose meaning.
- Required independent verification and review must have valid reports for the current code before approval. Local checks do not replace either role unless the user or project explicitly authorises substitution; record that authority, executor, and coverage. While a report is missing, keep the stage incomplete and `approved: false`. Moving the gap from `unverified` into a note cannot authorise completion; `unverified` describes unchecked scope, not every process limitation. Scripts cannot establish report independence.

JSON remains the storage format for ticket state and command input. A review stored in a JSON string is still the original report; do not extract a second finding schema from it. Use a serializer to store multiline text faithfully.

## Wait and recover

Each native subtask has a default execution budget of **10 minutes (600 seconds)** from dispatch, unless the user or project explicitly sets another budget. Record the handle, role, ticket/attempt or delivery snapshot, and actual start/deadline in the existing `.loop/` execution notes. Distinguish this budget from a single wait window and from a command's own timeout. Use shorter native waits as needed for runtime limits and progress updates; window expiry neither ends the subtask nor resets or shortens its budget. Without reliable elapsed-time evidence, do not claim the budget expired.

Silence, no diff, an unavailable status query, or no matching local process does not prove a stall or unavailable native capability. After a wait window ends, check available runtime state. If the execution is unfinished, has no new progress information, and remains within budget, send one non-interrupting progress inquiry (soft ping) when runtime messaging is supported. Use at most one per execution, including after context recovery; read [the inquiry procedure](references/wait-recovery.md#one-progress-inquiry-per-execution) before sending. If messaging is unavailable, record the limitation and continue waiting. Absence of a reply neither overrides a known running state nor authorises closing, redispatch, or approval. If the runtime reports completion, retrieve that execution's result instead. Do not duplicate a verifier's commands in the same environment while it may still be running.

On budget expiry, explicit failure/blockage, cancellation, or interruption, read [waiting and recovery](references/wait-recovery.md) before stopping or taking over. Confirm the old execution and relevant commands have stopped before overlapping work; preserve partial changes and version-bound reports. Recover the affected role without automatically rerunning implementation or relaxing acceptance. Runtime owns handles and cancellation; scripts do not recover Agent sessions.

## Resume and requirement changes

On resume, inspect the recorded native execution before dispatching another role and apply the waiting and recovery rules above.

Before changing shared SPEC/HLD/ACCEPTANCE or reconciling tickets, stop dispatch, interrupt active subagents through the runtime, confirm they stopped writing, preserve partial results, and `scripts/update-status block` their attempts. A graph state change alone does not stop a subagent.

Route unsettled requirement choices to `grilling` first, normative requirement changes to `to-spec`, shared design changes to `high-level-design`, and graph-only amendments to `to-tickets`. Do not inject changed requirements into an old attempt. Keep historical done records; retain only confirmed unaffected contracts/evidence. Changed behaviour needs correction/replacement tickets. Use `reopen` for defects against an unchanged confirmed contract.

## Continue through delivery

One completed ticket, an empty ready list, or `delivery_ready` is not a stopping condition. If tickets remain, resolve actionable retries/blockers and continue. When `delivery_ready` is true, perform [Finalization](references/delivery-review.md) in the same execution.

Stop only when final delivery is passed, the user stops the task, or remaining progress requires unavailable external input/capability. Explain the concrete blocker. The skill directs continued work while the runtime is active; it does not promise autonomous execution after that runtime stops.

Commit only when explicitly authorised. A later code, contract, graph, or Git HEAD change invalidates the recorded final snapshot.
