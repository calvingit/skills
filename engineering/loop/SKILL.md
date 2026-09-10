---
name: loop
description: Execute a ticket graph with loopx, reconcile changed requirements, and verify the final delivery against its current contract.
---

# Loop

Own ticket selection, attempts, workspace scope, receipt acceptance, and final delivery. Use the installed `loopx` CLI; graph state is written only through `loopx graph`.

## Execute

Start or resume with `loopx loop status <task-dir>`. It includes the graph, stale authority, and final delivery-review status; no second `graph inspect` is needed.

Read the task's SPEC, optional ACCEPTANCE and HLD, and the current tickets. Use only their confirmed acceptance conditions. Missing optional documents do not add prerequisites.

`loopx loop run <task-dir> --scope <path>` executes one attempt: implement → verify → review. A current attempt is resumed before other ready tickets. Use `--ticket <id>` to select explicitly when several attempts need recovery. The shared-workspace runtime is serial; do not claim ticket parallelism or run verify and review concurrently.

Loop terminates only when the workflow is complete, cannot make progress without external input, or the user explicitly stops it.

Do not derive termination from a `completed`, `blocked`, `failed`, or empty-ready result. Completing one ticket, finishing one worker pipeline, producing one attempt receipt, finding no ready ticket, or reaching `delivery_ready` is not a stopping condition by itself.

Continue driving the workflow after every attempt.

After each attempt:

1. Refresh with `loopx loop status <task-dir>`.
2. Reconcile the result against the current graph.
3. Select the next valid action.
4. If another ticket is runnable, execute it immediately.
5. Repeat until the termination invariant holds.

Handle results as follows:

- `completed`: refresh status and immediately run the next ready ticket when one exists.
- `retry`: continue the same ticket with its recorded findings and persisted scope.
- `blocked`: report the blocker. Verify its release condition before `graph unblock`; do not busy-retry an environment, permission, or requirement failure.
- `interrupted` or `failed`: preserve partial code and receipts; inspect and resolve the reported cause before resuming.
- No ready tickets: inspect unresolved blockers, coverage gaps, stale authority, and `delivery_ready`. If `delivery_ready` is true, continue into final delivery review rather than returning.

The workflow is complete only when `loop status` shows `delivery_review.state: passed`.

The workflow cannot make progress without external input when no ticket is runnable because unresolved external, permission, environment, requirement, or design input is required, or when an interruption or failure cannot be resolved from the current contract and recorded evidence.

Do not treat the absence of a ready ticket as completion without first determining why the graph cannot progress.

Workers implement, verify, or review the current scope. They do not modify upstream artifacts, schedule siblings, edit graph state, or commit. Verify runs the necessary commands; Loop accepts the recorded evidence and checks workspace, Git, graph, and completion bounds. Do not substitute self-report for results or invent new acceptance conditions.

## Review reports

`code-review` returns readable Markdown in every context. The CLI backend requests its report headings and normalises the final assistant message into the internal receipt; do not ask the reviewer for JSON. Read the preserved report when deciding how to respond.

- Confirmed current-scope findings require correction through the ticket's retry workflow.
- Requirement gaps go to the requirement owner; missing evidence or access must be resolved before completion.
- Optional follow-up does not block delivery. A missing, malformed, or contradictory report cannot pass; obtain a corrected report without inventing evidence or changing code merely to fix its format.

The internal receipt retains its existing review fields for graph validation. They are derived from the report, not separate review passes. For final delivery, apply the same mapping in [references/delivery-review.md](references/delivery-review.md).

## Requirement changes

Before changing shared SPEC/HLD/ACCEPTANCE or reconciling tickets, stop dispatch for this task, interrupt active workers, confirm they have stopped writing, preserve their partial receipts, and `graph block` each active attempt. Block can preserve a stopped attempt even when new requirement IDs temporarily leave graph coverage invalid.

Route requirement changes to `to-spec`, shared design changes to `high-level-design`, then graph changes to `to-tickets`. Do not pass new chat requirements straight into an old ticket. A changed contract blocks resume, retry, completion, and reopening until reconciled.

`stale_authority` means the current contract/evidence needs impact review, not that historical delivery failed. Keep historical done records. Confirm unaffected contracts and evidence through reconciliation; create correction/replacement tickets for changed behaviour. Use `reopen` only for defects against a currently confirmed unchanged contract.

## Final delivery

`all_active_done` describes ticket history. It does not prove the final code meets the latest SPEC. When `delivery_ready` is true, read [references/delivery-review.md](references/delivery-review.md), run whole-task verification and code-review, then accept the snapshot-bound receipt. Report delivery complete only when `loop status` shows `delivery_review.state: passed`.

Final delivery review is part of the same Loop execution. Reaching `delivery_ready` changes the next action; it does not end the Loop.

If final delivery review finds a defect, reopen or create the required corrective ticket through the normal graph workflow, then resume Loop. Do not patch the code directly inside final delivery review.

Commit only when explicitly authorised. A commit or later code/contract/graph change invalidates a prior final snapshot; review the resulting snapshot before reporting final completion.
