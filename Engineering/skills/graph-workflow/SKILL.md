---
name: graph-workflow
description: Advance a confirmed ticket dependency graph through implementation, evidence inspection, and execution-state transitions, dispatching native workers serially by default (swarm only when the user asks). Not an agent runtime or orchestration framework.
---

# Graph Workflow

Select work, Call the Skill tool with the responsible skill (or pass its resolved `SKILL.md` into a native worker), inspect its result, and record the resulting task state. The Manager owns these decisions; Runtime owns worker creation, waiting, cancellation, and session continuation. State scripts record graph and delivery facts, never launch agents or interpret reports.

Graph Workflow's existing execution contract uses Runtime-native workers for implementation and corrections; the Manager does not edit product code. Final simplification, verification, and review use dedicated workers. Do not substitute an external Agent CLI.

## Execute

1. Read `python3 <graph-workflow-skill>/scripts/frontier <task-dir>`, the current SPEC, applicable ACCEPTANCE/SOLUTION, relevant tickets, and existing execution records. Resolve their [Task Contract](../shared/task-contract.md) and current source references; check any recorded native execution before dispatching replacement work. Missing optional documents add no prerequisites.
2. Resume an in-progress ticket before choosing a ready one. Establish its baseline, pre-existing edits, current attempt, expected change areas, and delivery AC. Use `scripts/update-status start` for a new attempt or `retry` for a scoped correction; each write returns the updated graph, so pick the next ticket from it rather than re-querying. Read [script inputs](references/script-inputs.md) when writing state. Ticket documents hold the delivery contract; every phase, attempt, evidence entry and blocker is written to `.loop/state.json`.
3. Dispatch one native worker that loads `ticket-implement` (Call the Skill tool with "ticket-implement", or pass its resolved `SKILL.md`) with the ticket, authoritative inputs, baseline/scope, verification entry, permitted resources, and previous findings. Establish an observation method or visible gap for the delivery AC before implementation; use project methods rather than designing a test strategy in the Manager. Execute serially by default: at most one implementation worker at a time, preferably the same worker with its context refreshed for the new ticket. Parallel workers need the user's explicit swarm choice; read [delegation inputs](references/context-and-delegation.md) for reuse and parallel-safety rules.
4. Inspect actual changes and the worker's local acceptance evidence for every ticket AC and applicable project gate. `ticket-implement` owns development checks; request missing checks or corrections rather than duplicating its test strategy. Per-ticket independent verify/review is optional unless required by the user or project. Record the executor so local checks are not labelled independent verification.
5. Read text/Markdown reports directly and decide whether to complete, correct, block, or route a contract change. Preserve original reports and command evidence under the task's `.loop/`. Do not infer success from silence or a completion claim; scripts cannot judge prose or report independence.
6. Record the decision through `scripts/update-status`. A successful mutation returns the updated graph; continue from it and query again only when it is unclear or stale. Ticket `done` releases dependencies; it does not pass final delivery. Continue until final delivery passes, the user stops work, or progress requires unavailable external input/capability.

## Execution strategy

Serial is the default, and the only mode until the user explicitly asks for swarm (for example `/graph-workflow 使用 swarm 模式实现 tickets`). The mode belongs to the user: ticket count, task complexity, several ready tickets, or a preference for speed never justify swarm on the Manager's own judgement, and a downstream worker cannot enable it. Serial keeps one implementation worker at a time, reusing its context where Runtime supports it, while each ticket keeps its own attempt, write scope and evidence.

Under `swarm`, dispatch only from the current ready frontier, and only when a direct delivery dependency, expected write overlap, shared build cache or test process, mutable external resource, and unresolved shared technical contract are all absent. A ticket that cannot be shown safe waits; not every ready ticket must run at once. `start` refuses a second concurrent attempt unless the request carries `mode: swarm`, and refuses dependent or overlapping write areas even then; the shared-resource and unresolved-contract checks remain the Manager's judgement, not a script's.

Both modes use the same Frontier, Lifecycle, Authority, Evidence, Delivery Snapshot and finalization; the mode never changes a contract, acceptance, permission or closeout requirement. Decide it from the user's current request on every run — never infer it from earlier state, history or the graph shape.

## Decide from evidence

Use `verify`'s [verdict definitions](../verify/SKILL.md#verdicts). Preserve findings and their evidence source; other green checks do not override a required failure or evidence gap.

| Result / conflict | Next action |
| --- | --- |
| Observed defect against an unchanged contract | Send the finding to `ticket-implement`, record a correction attempt, and recheck affected evidence. Use `reopen` for a completed ticket only when graph rules permit it; otherwise request a corrective ticket. |
| Environment, permission, dependency, or external gap | Record a blocker with its release condition; resume only after confirming release evidence. Do not repeatedly retry an unresolved blocker. |
| Inadequate verification method | Try a sufficient existing read-only method; route required harness work to `verification-setup` or missing repository-test work to `ticket-implement`, within caller authority. A gap alone does not prove a product defect. |
| Requirement or shared-design conflict | Return it to the owning upstream skill; do not modify product code to satisfy an unconfirmed or incorrect expectation. |
| Missing or unclear required report | Retrieve or clarify the original result; keep the required stage incomplete. |

Complete a ticket only when every current delivery AC has sufficient local evidence and no required gap or unresolved blocker remains. Final delivery requires `PASS` for every current SPEC AC, independent verification and review for the current candidate, and no required unresolved scope. An explicitly authorised substitution must record authority, executor, and coverage; local checks alone do not satisfy independent gates.

Changes to code, requirements, tests, fixtures, snapshots, verification configuration, graph, or relevant environment require reassessing affected evidence. Do not reuse a report for a candidate it did not establish.

## State and execution boundaries

Resolve `<graph-workflow-skill>` to this installed skill directory; scripts use Python 3.10+ and sibling `Engineering/skills/shared/`. Query with `scripts/frontier` or `scripts/graph-query`; write every ticket state change and delivery record with `scripts/update-status`. Tickets are Markdown contracts: never hand-edit their frontmatter, and expect no execution field there. `recover` repairs a graph transaction, not an Agent session.

A ticket is a stable contract; its progress is ephemeral. `.loop/state.json` is the single source of the current phase, attempt, evidence, blocker and authority, and the graph is always queried with both stores merged — do not read or reconcile the two files by hand. Tickets that exist with no runtime state are never assumed unexecuted: the graph stops with `missing_runtime_state`, and only an explicit user instruction to re-initialize (after confirming the progress is lost) may rebuild it with `scripts/update-status init-state`. Do not commit `.loop/`.

Keep `.loop/` in the task directory next to SPEC and tickets. It contains attempts, reports, command logs, delivery inputs and the runtime state; it is not project configuration or a place for product code/tests, and its own `.gitignore` keeps it out of Git. Use existing source links and brief handoff notes when needed, without mandatory context files, timing ledgers, Agent pools, heartbeat services, or another execution state machine.

A ticket's `allowed_write_scope` records expected change areas, not sandbox permission. Related changes needed to complete the ticket may extend those areas within caller authority; report them for review. Unrelated changes remain outside scope.

Use Runtime's native lifecycle and configured limits. A wait returning without a result does not prove failure or stopped execution. On interruption, preserve partial work and bind reports to their original attempt/candidate. Confirm prior writers and relevant commands have stopped before starting overlapping work; if this cannot be established, report the blocker. Do not invent inactivity thresholds or reconstruct Runtime sessions.

## Requirement changes and final delivery

Before changing shared requirements/design or reconciling tickets, pause dispatch, stop active writers through Runtime, confirm they stopped, preserve partial results, and block affected attempts. Changing graph state alone does not stop a worker.

For unsettled choices Call the Skill tool with "grilling"; for normative requirements with "to-spec"; for shared design with "solution-design"; for graph-only changes with "to-tickets". Keep unaffected contracts/evidence and historical done records; changed behaviour needs amendment/correction tickets rather than reopening an old contract.

When `delivery_ready` is true, continue with [finalization](references/delivery-review.md) in the same run. Initial closeout covers the full change set; select the simplify step by the close-out risk tier — `verify` is never omitted, and an independent `code-review` report is mandated for final delivery by the delivery-state script. After corrections, default to targeted independent verification/review plus mandatory project gates, retaining still-valid evidence for all current SPEC AC. Broaden review only when material impact invalidates its prior basis; returning to `delivery_ready` alone does not restart full finalization. Report completion only when `frontier` shows `delivery_review.state: passed`. Runtime ending does not promise background continuation. Commit or push only when explicitly authorised.
