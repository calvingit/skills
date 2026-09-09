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

After each result:

- `completed`: inspect the graph again and run the next ready ticket.
- `retry`: continue the same ticket with its recorded findings and persisted scope.
- `blocked`: report the blocker. Verify its release condition before `graph unblock`; do not busy-retry an environment, permission, or requirement failure.
- `interrupted` or `failed`: preserve partial code and receipts; inspect and resolve the reported cause before resuming.
- No ready tickets: report unresolved blockers, coverage gaps, or stale authority. Enter final delivery review only when `delivery_ready` is true.

Workers implement, verify, or review the current scope. They do not modify upstream artifacts, schedule siblings, edit graph state, or commit. Verify runs the necessary commands; Loop accepts the recorded evidence and checks workspace, Git, graph, and completion bounds. Do not substitute self-report for results or invent new acceptance conditions.

## Requirement changes

Before changing shared SPEC/HLD/ACCEPTANCE or reconciling tickets, stop dispatch for this task, interrupt active workers, confirm they have stopped writing, preserve their partial receipts, and `graph block` each active attempt. Block can preserve a stopped attempt even when new requirement IDs temporarily leave graph coverage invalid.

Route requirement changes to `to-spec`, shared design changes to `high-level-design`, then graph changes to `to-tickets`. Do not pass new chat requirements straight into an old ticket. A changed contract blocks resume, retry, completion, and reopening until reconciled.

`stale_authority` means the current contract/evidence needs impact review, not that historical delivery failed. Keep historical done records. Confirm unaffected contracts and evidence through reconciliation; create correction/replacement tickets for changed behaviour. Use `reopen` only for defects against a currently confirmed unchanged contract.

## Final delivery

`all_active_done` describes ticket history. It does not prove the final code meets the latest SPEC. When `delivery_ready` is true, read [references/delivery-review.md](references/delivery-review.md), run whole-task verification and code-review, then accept the snapshot-bound receipt. Report delivery complete only when `loop status` shows `delivery_review.state: passed`.

Commit only when explicitly authorised. A commit or later code/contract/graph change invalidates a prior final snapshot; review the resulting snapshot before reporting final completion.

Interrupts, graph operations, receipts, and recovery: [Runtime contract](../../docs/loop-runtime.md).
