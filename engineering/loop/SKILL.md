---
name: loop
description: Drive a ticket graph through implementation, verification, and review using the current runtime's subagents.
---

# Loop

Own ticket selection, handoff, progress, and completion decisions. Use the current runtime's native subagents for `implement`, `verify`, and `code-review`. `loopx` only reads and writes ticket state and delivery progress; it does not execute agents. Do not launch external Agent CLIs or build a session, provider, polling, or result-parsing layer. If native subagents are unavailable, report that limitation; do not silently substitute an external CLI or claim independent review.

## Execute

1. Read `loopx loop status <task-dir>`, the current SPEC, optional ACCEPTANCE/HLD, and the relevant tickets. Resolve stale requirements before dispatch. Missing optional documents add no prerequisites.
2. Resume an in-progress ticket before selecting a ready one. Establish the baseline, pre-existing edits, the ticket's file scope (recorded as `allowed_write_scope`), acceptance criteria, and current attempt. For a new attempt use `loopx graph start`; for a correction use `graph retry`. Request shapes are in [the state commands](../../docs/loop-runtime.md#state-commands).
3. Give a native subagent the `implement` skill, ticket, current requirements, baseline/scope, and previous findings. Let it implement and simplify that scope. Subagents do not edit upstream documents, tickets, or Git history.
4. After implementation stops writing, use a separate native subagent for `verify`. Pass the actual changes and requirements; it runs the necessary checks and returns observed results. Then use a separate native subagent for `code-review`, with the scope, requirements, code, and verification evidence. Do not run review against code that is still changing.
5. Read their text/Markdown results directly. Preserve the original reports under the task directory's `.loop/` when needed for resume or handoff. No JSON response envelope, fixed headings, severity parser, or Markdown-to-JSON conversion is required.
6. Decide the next state and write it through `loopx graph`. Refresh status and continue immediately to the next actionable ticket. Default to serial execution; use parallel tickets only when the runtime supports them and their expected changes and dependencies are demonstrably independent. Use worktrees only when isolation is needed, through the runtime's existing capabilities.

## State location

`.loop/` belongs to the task execution context: keep it inside the task directory, next to `SPEC.md` and `tickets/`, and never create it at the repository root, where separate tasks would share one state. It stores execution state — current attempts, preserved reports, command logs, delivery inputs — not project-level configuration. On resume, read the current task directory's `.loop/` first.

## File scope

A ticket's file scope describes expected areas of change. It is guidance for implementation and review, not a hard write restriction: the implement subagent may modify additional files when required to complete the ticket, keeping additional changes related to the ticket objective and avoiding unrelated refactoring. Pass the scope to review as a reference for expected change areas, not as a boundary that turns related out-of-scope edits into defects.

## Decide from evidence

- A confirmed defect in the current contract goes back to implement through `graph retry`, with the original findings as text. Re-run affected verification and review.
- Requirement/design conflicts go to their owner. Missing access, permissions, dependencies, or evidence needs a specific blocker and release condition. Do not busy-retry unresolved external blockers.
- An unclear report needs clarification from its author. Do not infer success from silence, wording, headings, or a worker saying it finished. Optional follow-up does not block this change.
- Complete only after inspecting the changed scope, verifying every current AC, and confirming no unresolved blockers or required unverified scope. Pass the review string unchanged and your explicit approval to `graph complete`; the helper validates recorded facts, not prose meaning.

JSON remains the storage format for ticket state and command input. A review stored in a JSON string is still the original report; do not extract a second finding schema from it. Use a serializer to store multiline text faithfully.

## Resume and requirement changes

Runtime owns waiting, interruption, and subagent handles. After interruption, check native task state before starting another writer; preserve partial code and reports. If the old subagent cannot be resumed, start a new one with current state and the recorded attempt. Do not claim an old session was recovered by a script.

Before changing shared SPEC/HLD/ACCEPTANCE or reconciling tickets, stop dispatch, interrupt active subagents through the runtime, confirm they stopped writing, preserve partial results, and `graph block` their attempts. A graph state change alone does not stop a subagent.

Route requirements to `to-spec`, shared design to `high-level-design`, and graph amendments to `to-tickets`. Do not inject changed requirements into an old attempt. Keep historical done records; retain only confirmed unaffected contracts/evidence. Changed behaviour needs correction/replacement tickets. Use `reopen` for defects against an unchanged confirmed contract.

## Continue through delivery

One completed ticket, an empty ready list, or `delivery_ready` is not a stopping condition. If tickets remain, resolve actionable retries/blockers and continue. When `delivery_ready` is true, perform [final delivery review](references/delivery-review.md) in the same execution.

Stop only when final delivery is passed, the user stops the task, or remaining progress requires unavailable external input/capability. Explain the concrete blocker. The skill directs continued work while the runtime is active; it does not promise autonomous execution after that runtime stops.

Commit only when explicitly authorised. A later code, contract, graph, or Git HEAD change invalidates the recorded final snapshot.
