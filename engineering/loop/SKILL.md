---
name: loop
description: Consume a ticket graph with loopx, schedule execution units in serial or multi-agents mode, and run delivery review through the completion gate.
---

# Loop

This skill owns ticket selection, attempts, workspace baseline, scheduling mode, receipt acceptance, and the completion gate. Concrete execution comes from the installed `loopx` CLI.

## Entry

On start or resume, inspect the graph first:

```bash
loopx loop status <task-dir>
loopx graph inspect <task-dir>
```

Run the current ready ticket:

```bash
loopx loop run <task-dir> --scope <path>
```

Two execution modes only:

- `serial`: one session, implement → verify → code-review. Default.
- `multi-agents`: several sub-agents for independent tickets or capabilities. Enable only when write scope, shared side effects, and integration order have isolation evidence.

## Rules

- On start, load the task's existing `SPEC.md`, optional `ACCEPTANCE.md`, optional `HLD.md`, and `tickets/*.json` as fact sources and keep the contract unchanged. Loop does not invent conditions for a missing optional protocol, scenario map, or expected result. It blocks only when a ticket or receipt cannot be validated, required evidence is missing, or a bound is violated.
- Only this skill may write `start`, `retry`, `block`, `unblock`, `complete`, and `reopen` through `loopx graph`. A worker runs the current ticket's capability. It does not schedule siblings, edit the graph, commit, or push.
- Judge completion from the actual workspace, scope, verification output, review, and receipts. Do not accept a worker's verbal claim. Default to `serial`. `multi-agents` needs isolation evidence for dependencies, write scope, shared side effects, and integration order.
- After the completion gate passes, do not commit version-control changes unless the caller explicitly authorised it. Accept only acceptance conditions from the ticket, SPEC, or a separate protocol the task explicitly enabled, plus command output, workspace diff, receipts, and review evidence. Do not add acceptance conditions, and do not let worker self-report replace independent evidence.
- `verify` runs the commands the task needs and records actual results. Loop only accepts that evidence, checks scope / Git / graph bounds, and then `unblock`, retry, block, or complete. A separate `ACCEPTANCE.md` is used only when the task explicitly needs it. It is not a default prerequisite.

Command input, interrupts, blockers, and transaction recovery: [Runtime recovery contract](../../docs/loop-runtime.md#graph-mutation-与恢复).
